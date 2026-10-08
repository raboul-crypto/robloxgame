--!strict
-- WorldService.lua
-- Service de gestion de la progression, des portails et des conditions de passage entre les mondes.
-- Vérifie les 3 conditions de passage : Dragons uniques obtenus, Niveau joueur, Niveau moyen de l'équipe.

local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local ServerScriptService = game:GetService("ServerScriptService")

local Shared = ReplicatedStorage:WaitForChild("Shared")
local Config = Shared:WaitForChild("Config")
local Worlds = require(Config:WaitForChild("Worlds")) :: any
local Network = require(Shared:WaitForChild("Network")) :: any

local Services = ServerScriptService:WaitForChild("Services")
local DataService = require(Services:WaitForChild("DataService")) :: any

local changeWorldFunction = Network.getFunction("ChangeWorld")

local WorldService = {}

-- Positions d'apparition par monde dans le jeu
local WORLD_SPAWNS: { [number]: Vector3 } = {
	[1] = Vector3.new(0, 3, 40),
	[2] = Vector3.new(500, 3, 40),
	[3] = Vector3.new(1000, 3, 40),
	[4] = Vector3.new(1500, 3, 40),
	[5] = Vector3.new(2000, 3, 40),
}

--[[
	Calcule le niveau moyen de l'équipe de dragons équipés du joueur.
]]
function WorldService.getTeamAverageLevel(player: Player): number
	local profile = DataService.getProfile(player)
	if not profile or not profile.EquippedDragons or #profile.EquippedDragons == 0 then
		return 1
	end

	local sum = 0
	local count = 0
	for _, guid in ipairs(profile.EquippedDragons) do
		local dragon = profile.Dragons[guid]
		if dragon then
			sum += dragon.Level
			count += 1
		end
	end

	return count > 0 and math.floor(sum / count) or 1
end

--[[
	Compte le nombre d'espèces différentes de dragons obtenues par le joueur.
]]
function WorldService.getUniqueDragonsCount(player: Player): number
	local profile = DataService.getProfile(player)
	if not profile or not profile.Dragons then
		return 0
	end

	local uniqueSpecies: { [string]: boolean } = {}
	local count = 0
	for _, dragon in pairs(profile.Dragons) do
		if not uniqueSpecies[dragon.SpeciesId] then
			uniqueSpecies[dragon.SpeciesId] = true
			count += 1
		end
	end

	return count
end

--[[
	Vérifie si le joueur remplit toutes les conditions pour accéder à un monde.
]]
function WorldService.canEnterWorld(player: Player, targetWorldId: number): (boolean, string?)
	if targetWorldId <= 1 then
		return true, nil
	end

	local profile = DataService.getProfile(player)
	if not profile then
		return false, "Profil non chargé"
	end

	-- Déjà débloqué précédemment
	if profile.UnlockedWorlds and profile.UnlockedWorlds[targetWorldId] then
		return true, nil
	end

	local prevWorld = Worlds.List[targetWorldId - 1]
	if not prevWorld or not prevWorld.TransitionRequirements then
		return false, "Monde indisponible"
	end

	local reqs = prevWorld.TransitionRequirements
	local uniqueCount = WorldService.getUniqueDragonsCount(player)
	local playerLevel = profile.Level or 1
	local teamAvg = WorldService.getTeamAverageLevel(player)

	local missing = {}
	if uniqueCount < reqs.RequiredUniqueDragons then
		table.insert(missing, string.format("Dragons uniques : %d/%d", uniqueCount, reqs.RequiredUniqueDragons))
	end
	if playerLevel < reqs.RequiredPlayerLevel then
		table.insert(missing, string.format("Niveau joueur : %d/%d", playerLevel, reqs.RequiredPlayerLevel))
	end
	if teamAvg < reqs.RequiredTeamAvgLevel then
		table.insert(missing, string.format("Niveau moyen équipe : %d/%d", teamAvg, reqs.RequiredTeamAvgLevel))
	end

	if #missing > 0 then
		return false, "Conditions manquantes : " .. table.concat(missing, " • ")
	end

	return true, nil
end

--[[
	Téléporte le joueur vers le point de départ d'un monde.
]]
function WorldService.teleportToWorld(player: Player, targetWorldId: number): (boolean, string?)
	local canEnter, reason = WorldService.canEnterWorld(player, targetWorldId)
	if not canEnter then
		return false, reason
	end

	local profile = DataService.getProfile(player)
	if profile then
		profile.UnlockedWorlds[targetWorldId] = true
		DataService.syncToClient(player)
	end

	local char = player.Character
	local root = char and char:FindFirstChild("HumanoidRootPart") :: BasePart?
	local targetPos = WORLD_SPAWNS[targetWorldId] or WORLD_SPAWNS[1]

	if root then
		root.CFrame = CFrame.new(targetPos)
		print(string.format("[WorldService] %s s'est téléporté au Monde %d (%s)", player.Name, targetWorldId, Worlds.List[targetWorldId].Name))
		return true, nil
	end

	return false, "Personnage introuvable"
end

changeWorldFunction.OnServerInvoke = function(player: Player, targetWorldId: number)
	return WorldService.teleportToWorld(player, targetWorldId)
end

return WorldService
