--!strict
-- PetService.lua
-- Service serveur de gestion de l'équipement des dragons.
-- Valide la possession, le nombre de slots disponibles et la synchronisation avec le client.

local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local ServerScriptService = game:GetService("ServerScriptService")

local Services = ServerScriptService:WaitForChild("Services")
local DataService = require(Services:WaitForChild("DataService")) :: any

-- Création des fonctions distantes
local eventsFolder = ReplicatedStorage:WaitForChild("Events")

local equipPetFunction = eventsFolder:FindFirstChild("EquipPet")
if not equipPetFunction then
	equipPetFunction = Instance.new("RemoteFunction")
	equipPetFunction.Name = "EquipPet"
	equipPetFunction.Parent = eventsFolder
end

local unequipPetFunction = eventsFolder:FindFirstChild("UnequipPet")
if not unequipPetFunction then
	unequipPetFunction = Instance.new("RemoteFunction")
	unequipPetFunction.Name = "UnequipPet"
	unequipPetFunction.Parent = eventsFolder
end

local PetService = {}

--[[
	Équipe un dragon pour un joueur après vérification de possession et des slots libres.
]]
function PetService.equipPet(player: Player, dragonGuid: string): (boolean, string?)
	if not player or not dragonGuid then
		return false, "Paramètres invalides"
	end

	local profile = DataService.getProfile(player)
	if not profile then
		return false, "Profil non chargé"
	end

	-- 1. Vérification que le joueur possède bien ce dragon
	if not profile.Dragons[dragonGuid] then
		return false, "Vous ne possédez pas ce dragon."
	end

	-- 2. Vérification s'il est déjà équipé
	for _, id in ipairs(profile.EquippedDragons) do
		if id == dragonGuid then
			return false, "Ce dragon est déjà équipé."
		end
	end

	-- 3. Vérification des slots disponibles (3 de base, 5 avec pass, 8 avec pass +3)
	local maxSlots = 3
	if profile.GamePasses and profile.GamePasses["EquipePlus3"] then
		maxSlots = 8
	elseif profile.GamePasses and profile.GamePasses["EquipePlus2"] then
		maxSlots = 5
	end

	if #profile.EquippedDragons >= maxSlots then
		return false, string.format("Nombre maximum de dragons équipés atteint (%d/%d).", #profile.EquippedDragons, maxSlots)
	end

	-- Succès : ajout à la liste des équipés
	local success = DataService.equipDragon(player, dragonGuid)
	if success then
		print(string.format("[PetService] %s a équipé le dragon %s (%d/%d)", player.Name, dragonGuid, #profile.EquippedDragons, maxSlots))
		return true, nil
	else
		return false, "Échec de l'équipement."
	end
end

--[[
	Déséquipe un dragon.
]]
function PetService.unequipPet(player: Player, dragonGuid: string): (boolean, string?)
	if not player or not dragonGuid then
		return false, "Paramètres invalides"
	end

	local success = DataService.unequipDragon(player, dragonGuid)
	if success then
		print(string.format("[PetService] %s a déséquipé le dragon %s", player.Name, dragonGuid))
		return true, nil
	else
		return false, "Le dragon n'était pas équipé."
	end
end

-- Liaison avec les RemoteFunctions
equipPetFunction.OnServerInvoke = function(player: Player, dragonGuid: string)
	return PetService.equipPet(player, dragonGuid)
end

unequipPetFunction.OnServerInvoke = function(player: Player, dragonGuid: string)
	return PetService.unequipPet(player, dragonGuid)
end

return PetService
