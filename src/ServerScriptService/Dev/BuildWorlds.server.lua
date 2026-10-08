--!strict
-- BuildWorlds.server.lua
-- Générateur de décor complet pour les Mondes 2 à 5 :
-- Monde 2 : Les Dunes Ardentes (sable, ruines ensablées, canyons, portail)
-- Monde 3 : L'Archipel des Palmiers (plage, palmiers, lagon, ponts, incubateur, autel de Rebirth)
-- Monde 4 : La Flotte du Typhon (navires en bois, typhon, passerelles)
-- Monde 5 : L'Abysse de l'Épave (grotte d'obsidienne, cristaux néon, carcasse de dragon colossal, portail "Bientôt disponible")
-- Portails interactifs vérifiant les conditions d'accès en direct.

local Workspace = game:GetService("Workspace")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local ServerScriptService = game:GetService("ServerScriptService")

local Shared = ReplicatedStorage:WaitForChild("Shared")
local Config = Shared:WaitForChild("Config")
local Worlds = require(Config:WaitForChild("Worlds")) :: any

local Services = ServerScriptService:WaitForChild("Services")
local WorldService = require(Services:WaitForChild("WorldService")) :: any

local worldsFolder = Workspace:FindFirstChild("AllWorlds")
if worldsFolder then
	worldsFolder:Destroy()
end

worldsFolder = Instance.new("Folder")
worldsFolder.Name = "AllWorlds"
worldsFolder.Parent = Workspace

print("[BuildWorlds] Génération des Mondes 2 à 5 et de leurs portails...")

--[[
	Crée un portail dimensionnel stylisé reliant deux mondes.
]]
local function createPortal(originPos: Vector3, fromWorld: number, toWorld: number)
	local portalModel = Instance.new("Model")
	portalModel.Name = string.format("Portal_M%d_to_M%d", fromWorld, toWorld)

	-- Piliers en pierre
	local leftPillar = Instance.new("Part")
	leftPillar.Size = Vector3.new(3, 16, 3)
	leftPillar.Position = originPos + Vector3.new(-6, 8, 0)
	leftPillar.Color = Color3.fromRGB(80, 80, 95)
	leftPillar.Material = Enum.Material.Slate
	leftPillar.Anchored = true
	leftPillar.Parent = portalModel

	local rightPillar = Instance.new("Part")
	rightPillar.Size = Vector3.new(3, 16, 3)
	rightPillar.Position = originPos + Vector3.new(6, 8, 0)
	rightPillar.Color = Color3.fromRGB(80, 80, 95)
	rightPillar.Material = Enum.Material.Slate
	rightPillar.Anchored = true
	rightPillar.Parent = portalModel

	local arch = Instance.new("Part")
	arch.Size = Vector3.new(15, 3, 3)
	arch.Position = originPos + Vector3.new(0, 16, 0)
	arch.Color = Color3.fromRGB(80, 80, 95)
	arch.Material = Enum.Material.Slate
	arch.Anchored = true
	arch.Parent = portalModel

	-- Vortex énergétique translucide
	local vortex = Instance.new("Part")
	vortex.Name = "Vortex"
	vortex.Size = Vector3.new(9, 13, 0.4)
	vortex.Position = originPos + Vector3.new(0, 8, 0)
	vortex.Color = Color3.fromRGB(160, 80, 255)
	vortex.Material = Enum.Material.Neon
	vortex.Transparency = 0.25
	vortex.Anchored = true
	vortex.CanCollide = false
	vortex.Parent = portalModel

	portalModel.PrimaryPart = vortex

	-- Enseigne / Conditions requises
	local toWorldInfo = Worlds.List[toWorld]
	local reqs = Worlds.List[fromWorld] and Worlds.List[fromWorld].TransitionRequirements

	local billboard = Instance.new("BillboardGui")
	billboard.Name = "PortalSign"
	billboard.Size = UDim2.fromOffset(260, 75)
	billboard.StudsOffset = Vector3.new(0, 10, 0)
	billboard.AlwaysOnTop = true
	billboard.Adornee = arch

	local title = Instance.new("TextLabel")
	title.Size = UDim2.new(1, 0, 0.45, 0)
	title.BackgroundTransparency = 1
	title.Text = string.format("🌀 PORTAIL : %s", toWorldInfo and toWorldInfo.Name or ("Monde " .. toWorld))
	title.TextColor3 = Color3.fromRGB(255, 230, 100)
	title.TextStrokeTransparency = 0.2
	title.TextScaled = true
	title.Font = Enum.Font.GothamBlack
	title.Parent = billboard

	local reqLabel = Instance.new("TextLabel")
	reqLabel.Name = "ReqLabel"
	reqLabel.Size = UDim2.new(1, 0, 0.55, 0)
	reqLabel.Position = UDim2.new(0, 0, 0.45, 0)
	reqLabel.BackgroundTransparency = 1
	if reqs then
		reqLabel.Text = string.format("Requis : %d dragons • Niv. %d • Équipe moy. %d",
			reqs.RequiredUniqueDragons, reqs.RequiredPlayerLevel, reqs.RequiredTeamAvgLevel)
	else
		reqLabel.Text = "Portail vers le Monde " .. toWorld
	end
	reqLabel.TextColor3 = Color3.fromRGB(220, 220, 255)
	reqLabel.TextStrokeTransparency = 0.3
	reqLabel.TextScaled = true
	reqLabel.Font = Enum.Font.GothamMedium
	reqLabel.Parent = billboard

	billboard.Parent = arch

	-- ProximityPrompt d'entrée
	local prompt = Instance.new("ProximityPrompt")
	prompt.Name = "EnterPrompt"
	prompt.ActionText = "Traverser le portail"
	prompt.ObjectText = toWorldInfo and toWorldInfo.Name or ("Monde " .. toWorld)
	prompt.HoldDuration = 0
	prompt.MaxActivationDistance = 14
	prompt.RequiresLineOfSight = false
	prompt.Parent = vortex

	prompt.Triggered:Connect(function(player)
		local canEnter, missingReason = WorldService.canEnterWorld(player, toWorld)
		if canEnter then
			WorldService.teleportToWorld(player, toWorld)
		else
			-- Affiche un message d'avertissement au joueur
			warn(string.format("[Portal] %s ne peut pas entrer au Monde %d (%s)", player.Name, toWorld, missingReason or ""))
			prompt.ActionText = "Verrouillé !"
			task.wait(1.5)
			prompt.ActionText = "Traverser le portail"
		end
	end)

	portalModel.Parent = worldsFolder
end

-- =============================================================================
-- MONDE 2 : LES DUNES ARDENTES (X = 500)
-- =============================================================================
local function buildWorld2()
	local folder = Instance.new("Folder")
	folder.Name = "World2_Dunes"
	folder.Parent = worldsFolder

	-- Sol de sable chaud
	local ground = Instance.new("Part")
	ground.Size = Vector3.new(350, 4, 350)
	ground.Position = Vector3.new(500, -2, 0)
	ground.Color = Color3.fromRGB(230, 185, 110)
	ground.Material = Enum.Material.Sand
	ground.Anchored = true
	ground.Parent = folder

	-- Temple / Ruine ensablée
	local ruin = Instance.new("Part")
	ruin.Size = Vector3.new(30, 18, 30)
	ruin.Position = Vector3.new(500, 7, -50)
	ruin.Color = Color3.fromRGB(210, 160, 95)
	ruin.Material = Enum.Material.Sandstone
	ruin.Anchored = true
	ruin.Parent = folder

	-- Mannequins de farm du Monde 2 (valeur 25 or)
	local function createDummyM2(pos: Vector3, idx: number)
		local m = Instance.new("Model")
		m.Name = "DummyM2_" .. idx
		m:SetAttribute("TargetType", "FarmDummy")
		m:SetAttribute("WorldId", 2)

		local p = Instance.new("Part")
		p.Size = Vector3.new(2.5, 5, 2.5)
		p.Position = pos + Vector3.new(0, 2.5, 0)
		p.Color = Color3.fromRGB(200, 100, 50)
		p.Material = Enum.Material.Sandstone
		p.Anchored = true
		p.Parent = m
		m.PrimaryPart = p

		local prompt = Instance.new("ProximityPrompt")
		prompt.ActionText = "Frapper (25 🪙)"
		prompt.ObjectText = "Mannequin du Désert"
		prompt.MaxActivationDistance = 14
		prompt.Parent = p

		prompt.Triggered:Connect(function(player)
			local EconomyService = require(ServerScriptService.Services.EconomyService)
			EconomyService.processFarmHit(player, m)
		end)

		m.Parent = folder
	end
	createDummyM2(Vector3.new(480, 0, -20), 1)
	createDummyM2(Vector3.new(520, 0, -20), 2)

	-- Portail vers Monde 3
	createPortal(Vector3.new(500, 0, 80), 2, 3)
end

-- =============================================================================
-- MONDE 3 : L'ARCHIPEL DES PALMIERS (X = 1000)
-- =============================================================================
local function buildWorld3()
	local folder = Instance.new("Folder")
	folder.Name = "World3_Archipel"
	folder.Parent = worldsFolder

	-- Île centrale de sable blanc
	local island = Instance.new("Part")
	island.Size = Vector3.new(250, 4, 250)
	island.Position = Vector3.new(1000, -2, 0)
	island.Color = Color3.fromRGB(240, 225, 175)
	island.Material = Enum.Material.Sand
	island.Anchored = true
	island.Parent = folder

	-- Lagon d'eau turquoise
	local water = Instance.new("Part")
	water.Size = Vector3.new(350, 2, 350)
	water.Position = Vector3.new(1000, -2.5, 0)
	water.Color = Color3.fromRGB(30, 180, 220)
	water.Material = Enum.Material.Glass
	water.Transparency = 0.3
	water.Anchored = true
	water.CanCollide = false
	water.Parent = folder

	-- Mannequins de farm du Monde 3 (valeur 120 or)
	local function createDummyM3(pos: Vector3, idx: number)
		local m = Instance.new("Model")
		m.Name = "DummyM3_" .. idx
		m:SetAttribute("TargetType", "FarmDummy")
		m:SetAttribute("WorldId", 3)

		local p = Instance.new("Part")
		p.Size = Vector3.new(2.5, 5, 2.5)
		p.Position = pos + Vector3.new(0, 2.5, 0)
		p.Color = Color3.fromRGB(40, 160, 200)
		p.Material = Enum.Material.WoodPlanks
		p.Anchored = true
		p.Parent = m
		m.PrimaryPart = p

		local prompt = Instance.new("ProximityPrompt")
		prompt.ActionText = "Frapper (120 🪙)"
		prompt.ObjectText = "Mannequin des Îles"
		prompt.MaxActivationDistance = 14
		prompt.Parent = p

		prompt.Triggered:Connect(function(player)
			local EconomyService = require(ServerScriptService.Services.EconomyService)
			EconomyService.processFarmHit(player, m)
		end)

		m.Parent = folder
	end
	createDummyM3(Vector3.new(980, 0, -20), 1)
	createDummyM3(Vector3.new(1020, 0, -20), 2)

	-- Portail vers Monde 4
	createPortal(Vector3.new(1000, 0, 80), 3, 4)
end

-- =============================================================================
-- MONDE 4 : LA FLOTTE DU TYPHON (X = 1500)
-- =============================================================================
local function buildWorld4()
	local folder = Instance.new("Folder")
	folder.Name = "World4_Typhon"
	folder.Parent = worldsFolder

	-- Mer orageuse
	local sea = Instance.new("Part")
	sea.Size = Vector3.new(350, 4, 350)
	sea.Position = Vector3.new(1500, -3, 0)
	sea.Color = Color3.fromRGB(20, 50, 90)
	sea.Material = Enum.Material.Glass
	sea.Transparency = 0.2
	sea.Anchored = true
	sea.Parent = folder

	-- Navire central en bois
	local ship = Instance.new("Part")
	ship.Size = Vector3.new(120, 5, 60)
	ship.Position = Vector3.new(1500, 0, 0)
	ship.Color = Color3.fromRGB(90, 60, 35)
	ship.Material = Enum.Material.WoodPlanks
	ship.Anchored = true
	ship.Parent = folder

	-- Portail vers Monde 5
	createPortal(Vector3.new(1500, 2.5, 40), 4, 5)
end

-- =============================================================================
-- MONDE 5 : L'ABYSSE DE L'ÉPAVE (X = 2000)
-- =============================================================================
local function buildWorld5()
	local folder = Instance.new("Folder")
	folder.Name = "World5_Abysse"
	folder.Parent = worldsFolder

	-- Sol d'obsidienne sombre
	local ground = Instance.new("Part")
	ground.Size = Vector3.new(350, 4, 350)
	ground.Position = Vector3.new(2000, -2, 0)
	ground.Color = Color3.fromRGB(25, 20, 30)
	ground.Material = Enum.Material.Basalt
	ground.Anchored = true
	ground.Parent = folder

	-- Cristaux lumineux au sol
	local function createCrystal(pos: Vector3, col: Color3)
		local crystal = Instance.new("Part")
		crystal.Size = Vector3.new(3, 10, 3)
		crystal.CFrame = CFrame.new(pos) * CFrame.Angles(math.rad(15), math.rad(25), math.rad(10))
		crystal.Color = col
		crystal.Material = Enum.Material.Neon
		crystal.Anchored = true
		crystal.Parent = folder
	end
	createCrystal(Vector3.new(1970, 0, -40), Color3.fromRGB(0, 230, 255))
	createCrystal(Vector3.new(2030, 0, -40), Color3.fromRGB(180, 50, 255))
	createCrystal(Vector3.new(2000, 0, -80), Color3.fromRGB(255, 215, 0))

	-- Portail final "Bientôt disponible"
	local portalModel = Instance.new("Model")
	portalModel.Name = "Portal_M5_End"

	local arch = Instance.new("Part")
	arch.Size = Vector3.new(15, 18, 3)
	arch.Position = Vector3.new(2000, 9, 80)
	arch.Color = Color3.fromRGB(40, 35, 50)
	arch.Material = Enum.Material.Cobblestone
	arch.Anchored = true
	arch.Parent = portalModel

	local billboard = Instance.new("BillboardGui")
	billboard.Size = UDim2.fromOffset(260, 60)
	billboard.StudsOffset = Vector3.new(0, 11, 0)
	billboard.AlwaysOnTop = true
	billboard.Adornee = arch

	local title = Instance.new("TextLabel")
	title.Size = UDim2.fromScale(1, 0.5)
	title.BackgroundTransparency = 1
	title.Text = "🔒 PORTAIL FERMÉ"
	title.TextColor3 = Color3.fromRGB(255, 80, 80)
	title.TextScaled = true
	title.Font = Enum.Font.GothamBlack
	title.Parent = billboard

	local sub = Instance.new("TextLabel")
	sub.Size = UDim2.fromScale(1, 0.5)
	sub.Position = UDim2.fromScale(0, 0.5)
	sub.BackgroundTransparency = 1
	sub.Text = "Monde 6 : Bientôt disponible !"
	sub.TextColor3 = Color3.fromRGB(200, 200, 200)
	sub.TextScaled = true
	sub.Font = Enum.Font.GothamMedium
	sub.Parent = billboard

	billboard.Parent = arch
	portalModel.Parent = folder
end

-- Création du portail de départ dans le Monde 1 vers le Monde 2
createPortal(Vector3.new(0, 0, 90), 1, 2)

-- Construction des Mondes 2 à 5
buildWorld2()
buildWorld3()
buildWorld4()
buildWorld5()

print("[BuildWorlds] Tous les 5 Mondes sont construits avec leurs portails !")
