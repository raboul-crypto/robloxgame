--!strict
-- PetFollowController.client.lua
-- Contrôleur client gérant le suivi ultra-fluide des dragons équipés autour du joueur.
-- Mouvements interpolés (lerp), balancement naturel, zéro lag réseau, aucune collision physique.

local Players = game:GetService("Players")
local RunService = game:GetService("RunService")
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local Shared = ReplicatedStorage:WaitForChild("Shared")
local DragonModels = require(Shared:WaitForChild("DragonModels")) :: any

local Network = require(Shared:WaitForChild("Network")) :: any

local player = Players.LocalPlayer
local dataSyncEvent = Network.getEvent("DataSync")

-- Dossier local pour héberger les modèles visuels des dragons du joueur
local localPetsFolder = Instance.new("Folder")
localPetsFolder.Name = "LocalPets"
localPetsFolder.Parent = workspace

type ActivePet = {
	Guid: string,
	Model: Model,
	CurrentCFrame: CFrame,
	Offset: Vector3,
}

local activePets: { [string]: ActivePet } = {}
local currentEquippedGuids: { string } = {}
local ownedDragonsData: { [string]: any } = {}

-- Offsets de formation selon le nombre de dragons équipés (1 à 8)
local FORMATIONS: { [number]: { Vector3 } } = {
	[1] = {
		Vector3.new(3.5, 1.2, 3.2),
	},
	[2] = {
		Vector3.new(-3.5, 1.2, 3.2),
		Vector3.new(3.5, 1.2, 3.2),
	},
	[3] = {
		Vector3.new(-4.5, 1.2, 3.0),
		Vector3.new(0, 1.6, 4.5),
		Vector3.new(4.5, 1.2, 3.0),
	},
	[4] = {
		Vector3.new(-5.0, 1.2, 2.5),
		Vector3.new(-2.0, 1.5, 4.2),
		Vector3.new(2.0, 1.5, 4.2),
		Vector3.new(5.0, 1.2, 2.5),
	},
	[5] = {
		Vector3.new(-5.5, 1.2, 2.5),
		Vector3.new(-3.0, 1.5, 4.0),
		Vector3.new(0, 1.8, 5.0),
		Vector3.new(3.0, 1.5, 4.0),
		Vector3.new(5.5, 1.2, 2.5),
	},
}

--[[
	Supprime le modèle d'un dragon qui n'est plus équipé.
]]
local function removePetModel(guid: string)
	local pet = activePets[guid]
	if pet then
		if pet.Model then
			pet.Model:Destroy()
		end
		activePets[guid] = nil
	end
end

--[[
	Met à jour la liste des dragons affichés autour du joueur.
]]
local function refreshEquippedPets()
	local character = player.Character
	local rootPart = character and character:FindFirstChild("HumanoidRootPart") :: BasePart?
	local spawnCFrame = rootPart and rootPart.CFrame or CFrame.new(0, 5, 0)

	local count = #currentEquippedGuids
	local formationOffsets = FORMATIONS[count] or FORMATIONS[3]

	-- 1. Supprime les dragons qui ne sont plus dans la liste des équipés
	for guid, _ in pairs(activePets) do
		local stillEquipped = false
		for _, eqGuid in ipairs(currentEquippedGuids) do
			if eqGuid == guid then
				stillEquipped = true
				break
			end
		end
		if not stillEquipped then
			removePetModel(guid)
		end
	end

	-- 2. Crée ou met à jour les dragons équipés
	for index, guid in ipairs(currentEquippedGuids) do
		local dragonRecord = ownedDragonsData[guid]
		local offset = formationOffsets[index] or Vector3.new(index * 3, 1, 3)

		if dragonRecord then
			local existingPet = activePets[guid]
			if not existingPet then
				-- Instanciation du modèle 3D du dragon
				local model = DragonModels.getModel(dragonRecord.SpeciesId, dragonRecord.Stage)
				model.Name = "Pet_" .. tostring(dragonRecord.SpeciesId)

				-- Sécurisation : ancré, pas de collision, massless
				for _, desc in ipairs(model:GetDescendants()) do
					if desc:IsA("BasePart") then
						desc.CanCollide = false
						desc.CanTouch = false
						desc.CanQuery = false
						desc.Anchored = true
						desc.Massless = true
					end
				end

				local startCFrame = spawnCFrame * CFrame.new(offset)
				model:PivotTo(startCFrame)
				model.Parent = localPetsFolder

				activePets[guid] = {
					Guid = guid,
					Model = model,
					CurrentCFrame = startCFrame,
					Offset = offset,
				}
			else
				existingPet.Offset = offset
			end
		end
	end
end

-- Réception de la synchronisation des données depuis le serveur
dataSyncEvent.OnClientEvent:Connect(function(data)
	if not data then return end

	if data.Dragons then
		ownedDragonsData = data.Dragons
	end

	if data.EquippedDragons then
		currentEquippedGuids = data.EquippedDragons
		refreshEquippedPets()
	end
end)

-- Rafraîchissement lors de la réapparition du personnage
player.CharacterAdded:Connect(function()
	task.wait(0.5)
	refreshEquippedPets()
end)

-- =============================================================================
-- BOUCLE D'ANIMATION ET DE SUIVI FLUIDE (RenderStepped)
-- =============================================================================
RunService.RenderStepped:Connect(function(dt: number)
	local character = player.Character
	if not character then return end

	local rootPart = character:FindFirstChild("HumanoidRootPart") :: BasePart?
	if not rootPart then return end

	local rootCFrame = rootPart.CFrame
	local clock = os.clock()
	local index = 0

	for _, pet in pairs(activePets) do
		index += 1
		local model = pet.Model
		if model and model.PrimaryPart then
			-- Effet de flottement et balancement sinusoïdal
			local bobbingY = math.sin(clock * 3.2 + index * 0.8) * 0.35
			local bobbingTilt = math.sin(clock * 2.0 + index * 0.5) * 0.06

			-- Position cible calculée dans l'espace local du joueur
			local targetPosition = rootCFrame:PointToWorldSpace(pet.Offset + Vector3.new(0, bobbingY, 0))
			local lookAtPosition = targetPosition + rootCFrame.LookVector * 10

			local targetCFrame = CFrame.lookAt(targetPosition, lookAtPosition) * CFrame.Angles(0, 0, bobbingTilt)

			-- Si le joueur vient d'être téléporté ou respawn (distance trop grande), téléportation directe
			local distance = (pet.CurrentCFrame.Position - targetPosition).Magnitude
			if distance > 40 then
				pet.CurrentCFrame = targetCFrame
			else
				-- Interpolation fluide (Lerp)
				local lerpSpeed = math.clamp(dt * 7.5, 0, 1)
				pet.CurrentCFrame = pet.CurrentCFrame:Lerp(targetCFrame, lerpSpeed)
			end

			model:PivotTo(pet.CurrentCFrame)
		end
	end
end)

print("[PetFollowController] Contrôleur de suivi des dragons initialisé.")
