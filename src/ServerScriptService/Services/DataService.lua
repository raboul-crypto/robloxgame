--!strict
-- DataService.lua
-- Service de gestion et de persistance des données joueur (DataStoreService).
-- Conforme aux spécifications 2.15 du brief : cache serveur, auto-save 60s, BindToClose,
-- UpdateAsync, versioning et protection stricte contre l'écrasement en cas d'échec de chargement.

local Players = game:GetService("Players")
local DataStoreService = game:GetService("DataStoreService")
local RunService = game:GetService("RunService")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local HttpService = game:GetService("HttpService")

local Shared = ReplicatedStorage:WaitForChild("Shared")
local Config = Shared:WaitForChild("Config")
local Stages = require(Config:WaitForChild("Stages")) :: any

-- Création du dossier d'événements réseau s'il n'existe pas
local eventsFolder = ReplicatedStorage:FindFirstChild("Events")
if not eventsFolder then
	eventsFolder = Instance.new("Folder")
	eventsFolder.Name = "Events"
	eventsFolder.Parent = ReplicatedStorage
end

local dataSyncEvent = eventsFolder:FindFirstChild("DataSync")
if not dataSyncEvent then
	dataSyncEvent = Instance.new("RemoteEvent")
	dataSyncEvent.Name = "DataSync"
	dataSyncEvent.Parent = eventsFolder
end

-- Nom du DataStore et version des schémas
local DATA_STORE_NAME = "DragonPetsSimulator_v1"
local CURRENT_DATA_VERSION = 1
local AUTOSAVE_INTERVAL = 60
local MAX_RETRIES = 3

local playerDataStore: any = nil
pcall(function()
	playerDataStore = DataStoreService:GetDataStore(DATA_STORE_NAME)
end)

export type DragonRecord = {
	Guid: string,
	SpeciesId: string,
	Level: number,
	Exp: number,
	Stage: string,
	Tradeable: boolean,
	ObtainedAt: number,
}

export type PlayerProfile = {
	DataVersion: number,
	Gold: number,
	Diamonds: number,
	Level: number,
	Exp: number,
	Rebirths: number,
	UnlockedWorlds: { [number]: boolean },
	GamePasses: { [string]: boolean },
	Dragons: { [string]: DragonRecord }, -- Guid -> DragonRecord
	EquippedDragons: { string },         -- Liste de Guids
}

local DataService = {}

-- Cache en mémoire vive côté serveur
local sessionData: { [Player]: PlayerProfile } = {}
local failedLoads: { [Player]: boolean } = {}
local profileLoadedBindable = Instance.new("BindableEvent")
DataService.OnProfileLoaded = profileLoadedBindable.Event

-- Modèle de données par défaut pour un nouveau joueur
local function getDefaultProfile(): PlayerProfile
	return {
		DataVersion = CURRENT_DATA_VERSION,
		Gold = 0,
		Diamonds = 0,
		Level = 1,
		Exp = 0,
		Rebirths = 0,
		UnlockedWorlds = { [1] = true },
		GamePasses = {},
		Dragons = {},
		EquippedDragons = {},
	}
end

--[[
	Synchronise les données du joueur vers son client via RemoteEvent.
]]
function DataService.syncToClient(player: Player)
	local profile = sessionData[player]
	if not profile then
		return
	end

	-- Envoi au client d'une copie nettoyée de ses données
	dataSyncEvent:FireClient(player, {
		Gold = profile.Gold,
		Diamonds = profile.Diamonds,
		Level = profile.Level,
		Exp = profile.Exp,
		Rebirths = profile.Rebirths,
		UnlockedWorlds = profile.UnlockedWorlds,
		Dragons = profile.Dragons,
		EquippedDragons = profile.EquippedDragons,
	})
end

--[[
	Exécute une fonction protégée avec plusieurs tentatives en cas d'erreur réseau.
]]
local function retryWithBackoff<T>(action: () -> (boolean, T?)): (boolean, T?)
	local attempt = 0
	local success, result
	while attempt < MAX_RETRIES do
		attempt += 1
		success, result = action()
		if success then
			return true, result
		end
		if attempt < MAX_RETRIES then
			task.wait(1 * attempt)
		end
	end
	return false, result
end

--[[
	Charge les données d'un joueur depuis le DataStore.
]]
local function loadPlayerData(player: Player)
	if not playerDataStore then
		-- Si l'accès aux API Studio n'est pas activé, on fournit le profil par défaut
		warn("[DataService] DataStore inaccessible. Utilisation du profil en mémoire de test pour " .. player.Name)
		sessionData[player] = getDefaultProfile()
		profileLoadedBindable:Fire(player, sessionData[player])
		DataService.syncToClient(player)
		return
	end

	local key = "Player_" .. tostring(player.UserId)
	local success, data = retryWithBackoff(function()
		local ok, res = pcall(function()
			return playerDataStore:GetAsync(key)
		end)
		return ok, res
	end)

	if not success then
		warn(string.format("[DataService] Échec critique du chargement des données pour %s (UserId: %d)", player.Name, player.UserId))
		failedLoads[player] = true
		player:Kick("Impossible de charger vos données en toute sécurité. Veuillez vous reconnecter.")
		return
	end

	local profile: PlayerProfile
	if data and type(data) == "table" then
		profile = data :: PlayerProfile
		-- Migration éventuelle de version
		if not profile.DataVersion or profile.DataVersion < CURRENT_DATA_VERSION then
			profile.DataVersion = CURRENT_DATA_VERSION
		end
		-- Complétion des champs manquants
		local defaultProf = getDefaultProfile()
		for k, v in pairs(defaultProf) do
			if (profile :: any)[k] == nil then
				(profile :: any)[k] = v
			end
		end
	else
		-- Nouveau joueur
		profile = getDefaultProfile()
	end

	sessionData[player] = profile
	print(string.format("[DataService] Profil chargé avec succès pour %s (Or: %d, Diamants: %d)", player.Name, profile.Gold, profile.Diamonds))
	profileLoadedBindable:Fire(player, profile)
	DataService.syncToClient(player)
end

--[[
	Sauvegarde les données d'un joueur vers le DataStore.
]]
local function savePlayerData(player: Player): boolean
	local profile = sessionData[player]
	if not profile then
		return false
	end

	-- PROTECTION CRITIQUE : Ne jamais écraser si le chargement a échoué
	if failedLoads[player] then
		warn(string.format("[DataService] Annulation de la sauvegarde pour %s car le chargement initial avait échoué.", player.Name))
		return false
	end

	if not playerDataStore then
		return false
	end

	local key = "Player_" .. tostring(player.UserId)
	local success = retryWithBackoff(function()
		local ok, err = pcall(function()
			playerDataStore:UpdateAsync(key, function(oldData)
				return profile
			end)
		end)
		return ok, err
	end)

	if success then
		print(string.format("[DataService] Sauvegarde réussie pour %s", player.Name))
		return true
	else
		warn(string.format("[DataService] Échec de sauvegarde pour %s", player.Name))
		return false
	end
end

-- =============================================================================
-- API PUBLIQUE DU DATASERVICE (pas de modification directe des tables de l'extérieur)
-- =============================================================================

function DataService.getProfile(player: Player): PlayerProfile?
	return sessionData[player]
end

function DataService.addGold(player: Player, amount: number): number
	if amount <= 0 then return 0 end
	local profile = sessionData[player]
	if not profile then return 0 end

	profile.Gold += math.floor(amount)
	DataService.syncToClient(player)
	return profile.Gold
end

function DataService.removeGold(player: Player, amount: number): boolean
	if amount <= 0 then return true end
	local profile = sessionData[player]
	if not profile then return false end

	if profile.Gold >= amount then
		profile.Gold -= math.floor(amount)
		DataService.syncToClient(player)
		return true
	end
	return false
end

function DataService.addDiamonds(player: Player, amount: number): number
	if amount <= 0 then return 0 end
	local profile = sessionData[player]
	if not profile then return 0 end

	profile.Diamonds += math.floor(amount)
	DataService.syncToClient(player)
	return profile.Diamonds
end

function DataService.removeDiamonds(player: Player, amount: number): boolean
	if amount <= 0 then return true end
	local profile = sessionData[player]
	if not profile then return false end

	if profile.Diamonds >= amount then
		profile.Diamonds -= math.floor(amount)
		DataService.syncToClient(player)
		return true
	end
	return false
end

function DataService.addDragon(player: Player, speciesId: string, stage: string?): (boolean, DragonRecord?)
	local profile = sessionData[player]
	if not profile then return false, nil end

	stage = stage or "Bebe"
	local guid = HttpService:GenerateGUID(false)
	local newDragon: DragonRecord = {
		Guid = guid,
		SpeciesId = speciesId,
		Level = 1,
		Exp = 0,
		Stage = stage,
		Tradeable = true,
		ObtainedAt = os.time(),
	}

	profile.Dragons[guid] = newDragon
	DataService.syncToClient(player)
	print(string.format("[DataService] Dragon ajouté à l'inventaire de %s : %s (GUID: %s)", player.Name, speciesId, guid))
	return true, newDragon
end

function DataService.removeDragon(player: Player, guid: string): boolean
	local profile = sessionData[player]
	if not profile or not profile.Dragons[guid] then return false end

	-- Déséquiper si équipé
	DataService.unequipDragon(player, guid)
	profile.Dragons[guid] = nil
	DataService.syncToClient(player)
	return true
end

function DataService.equipDragon(player: Player, guid: string): boolean
	local profile = sessionData[player]
	if not profile or not profile.Dragons[guid] then return false end

	-- Vérifie si déjà équipé
	for _, id in ipairs(profile.EquippedDragons) do
		if id == guid then
			return false
		end
	end

	-- Vérifie la limite d'équipement (3 par défaut)
	local maxSlots = 3
	if profile.GamePasses["EquipePlus3"] then
		maxSlots = 8
	elseif profile.GamePasses["EquipePlus2"] then
		maxSlots = 5
	end

	if #profile.EquippedDragons < maxSlots then
		table.insert(profile.EquippedDragons, guid)
		DataService.syncToClient(player)
		return true
	end

	return false
end

function DataService.unequipDragon(player: Player, guid: string): boolean
	local profile = sessionData[player]
	if not profile then return false end

	for index, id in ipairs(profile.EquippedDragons) do
		if id == guid then
			table.remove(profile.EquippedDragons, index)
			DataService.syncToClient(player)
			return true
		end
	end

	return false
end

--[[
	Ajoute de l'expérience au joueur et gère les montées de niveau jusqu'au niveau 50.
]]
function DataService.addPlayerExp(player: Player, amount: number): (boolean, number)
	local profile = sessionData[player]
	if not profile or amount <= 0 then return false, 0 end

	if profile.Level >= 50 then
		return false, profile.Level
	end

	profile.Exp += math.floor(amount)
	local leveledUp = false

	while profile.Level < 50 do
		local requiredExp = profile.Level * 100
		if profile.Exp >= requiredExp then
			profile.Exp -= requiredExp
			profile.Level += 1
			leveledUp = true
			print(string.format("[DataService] %s monte au niveau %d !", player.Name, profile.Level))
		else
			break
		end
	end

	DataService.syncToClient(player)
	return leveledUp, profile.Level
end

--[[
	Ajoute de l'expérience à un dragon et gère son évolution automatique :
	Bébé (1 à 14) -> Jeune (15 à 34) -> Adulte (35 à 50).
]]
function DataService.addDragonExp(player: Player, guid: string, amount: number): (boolean, boolean)
	local profile = sessionData[player]
	if not profile or not profile.Dragons[guid] or amount <= 0 then return false, false end

	local dragon = profile.Dragons[guid]
	if dragon.Level >= 50 then return false, false end

	dragon.Exp += math.floor(amount)
	local leveledUp = false
	local evolved = false

	while dragon.Level < 50 do
		local req = dragon.Level * 60
		if dragon.Exp >= req then
			dragon.Exp -= req
			dragon.Level += 1
			leveledUp = true

			-- Évolution automatique selon le niveau
			if dragon.Level >= 35 and dragon.Stage ~= "Adulte" then
				dragon.Stage = "Adulte"
				evolved = true
				print(string.format("[DataService] Évolution majeure : Le dragon %s (%s) de %s devient Adulte !",
					dragon.SpeciesId, guid, player.Name))
			elseif dragon.Level >= 15 and dragon.Stage == "Bebe" then
				dragon.Stage = "Jeune"
				evolved = true
				print(string.format("[DataService] Évolution : Le dragon %s (%s) de %s devient Jeune !",
					dragon.SpeciesId, guid, player.Name))
			end
		else
			break
		end
	end

	DataService.syncToClient(player)
	return leveledUp, evolved
end


-- =============================================================================
-- ÉVÉNEMENTS DU CYCLE DE VIE
-- =============================================================================

Players.PlayerAdded:Connect(function(player)
	loadPlayerData(player)
end)

Players.PlayerRemoving:Connect(function(player)
	savePlayerData(player)
	sessionData[player] = nil
	failedLoads[player] = nil
end)

-- Sauvegarde automatique toutes les 60 secondes
task.spawn(function()
	while true do
		task.wait(AUTOSAVE_INTERVAL)
		for _, player in ipairs(Players:GetPlayers()) do
			if sessionData[player] and not failedLoads[player] then
				savePlayerData(player)
			end
		end
	end
end)

-- Sauvegarde à la fermeture du serveur
game:BindToClose(function()
	print("[DataService] Fermeture du serveur : sauvegarde de tous les profils...")
	for _, player in ipairs(Players:GetPlayers()) do
		savePlayerData(player)
	end
end)

return DataService
