--!strict
-- EconomyService.lua
-- Service de gestion des gains d'or, du farm et de la validation anti-triche serveur.
-- Vérifie la distance du joueur, le délai entre deux frappes, et applique les multiplicateurs.

local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local Workspace = game:GetService("Workspace")

local Shared = ReplicatedStorage:WaitForChild("Shared")
local Config = Shared:WaitForChild("Config")

local Economy = require(Config:WaitForChild("Economy")) :: any
local Rarities = require(Config:WaitForChild("Rarities")) :: any
local Dragons = require(Config:WaitForChild("Dragons")) :: any
local StatCalc = require(Shared:WaitForChild("StatCalc")) :: any

local ServerScriptService = game:GetService("ServerScriptService")
local Services = ServerScriptService:WaitForChild("Services")
local DataService = require(Services:WaitForChild("DataService")) :: any

-- Création des RemoteEvents
local eventsFolder = ReplicatedStorage:WaitForChild("Events")

local hitFarmTargetEvent = eventsFolder:FindFirstChild("HitFarmTarget")
if not hitFarmTargetEvent then
	hitFarmTargetEvent = Instance.new("RemoteEvent")
	hitFarmTargetEvent.Name = "HitFarmTarget"
	hitFarmTargetEvent.Parent = eventsFolder
end

local farmHitEffectEvent = eventsFolder:FindFirstChild("FarmHitEffect")
if not farmHitEffectEvent then
	farmHitEffectEvent = Instance.new("RemoteEvent")
	farmHitEffectEvent.Name = "FarmHitEffect"
	farmHitEffectEvent.Parent = eventsFolder
end

local EconomyService = {}

-- Suivi des timestamps des dernières frappes pour chaque joueur (anti-spam / cadence)
local lastHitTimes: { [Player]: number } = {}

--[[
	Calcule le montant d'or gagné par frappe selon le monde et les dragons équipés du joueur.
	Formule : gain de base × (1 + somme des puissances des dragons équipés) × bonus rebirth × pass permanent
]]
function EconomyService.calculateFarmGold(player: Player, worldId: number): number
	local profile = DataService.getProfile(player)
	if not profile then
		return 0
	end

	worldId = worldId or 1
	local baseGold = Economy.BaseFarmGold[worldId] or 5

	-- Calcul de la somme des puissances des dragons équipés
	local totalDragonPower = 0
	if profile.EquippedDragons and profile.Dragons then
		for _, guid in ipairs(profile.EquippedDragons) do
			local dragonRecord = profile.Dragons[guid]
			if dragonRecord then
				local dragonConfig = Dragons.List[dragonRecord.SpeciesId]
				if dragonConfig then
					local power = StatCalc.getFarmPower(dragonConfig.Rarity, dragonRecord.Stage)
					totalDragonPower += power
				end
			end
		end
	end

	-- Multiplicateur de puissance des dragons
	local petMultiplier = 1 + totalDragonPower

	-- Bonus de Rebirth (+10 % par rebirth)
	local rebirthBonus = 1 + (profile.Rebirths or 0) * Economy.Rebirth.GoldBonusPerRebirth

	-- Pass Or x2 permanent
	local passMultiplier = 1
	if profile.GamePasses and profile.GamePasses["OrX2Permanent"] then
		passMultiplier = 2
	end

	local finalGold = math.round(baseGold * petMultiplier * rebirthBonus * passMultiplier)
	return math.max(1, finalGold)
end

--[[
	Traite une frappe sur une cible de farm (mannequin).
	Effectue les vérifications de sécurité strictes côté serveur :
	1. Existence du joueur et de son personnage
	2. Cooldown anti-spam entre deux coups
	3. Distance maximale autorisée
]]
function EconomyService.processFarmHit(player: Player, targetModel: Instance?): (boolean, number)
	if not player or not targetModel or not targetModel:IsA("Model") then
		return false, 0
	end

	local character = player.Character
	if not character then
		return false, 0
	end

	local rootPart = character:FindFirstChild("HumanoidRootPart") :: BasePart?
	if not rootPart then
		return false, 0
	end

	-- 1. Vérification de la cadence (Anti-spam / Anti-macro)
	local now = os.clock()
	local lastHit = lastHitTimes[player] or 0
	if (now - lastHit) < Economy.FarmHitCooldown then
		-- Frappe trop rapide, ignorée
		return false, 0
	end

	-- 2. Vérification de la cible et de la distance
	local targetPrimary = targetModel.PrimaryPart or targetModel:FindFirstChildWhichIsA("BasePart")
	if not targetPrimary then
		return false, 0
	end

	local distance = (rootPart.Position - targetPrimary.Position).Magnitude
	if distance > Economy.FarmMaxDistance then
		warn(string.format("[EconomyService] Frappe rejetée pour %s : distance suspecte (%.1f studs > limite %d)",
			player.Name, distance, Economy.FarmMaxDistance))
		return false, 0
	end

	-- Frappe validée !
	lastHitTimes[player] = now

	local worldId = (targetModel:GetAttribute("WorldId") :: number) or 1
	local goldGain = EconomyService.calculateFarmGold(player, worldId)

	-- Crédit de l'or via le DataService sécurisé
	DataService.addGold(player, goldGain)

	-- Effet visuel et audio répliqué
	farmHitEffectEvent:FireAllClients(targetPrimary.Position, goldGain)

	return true, goldGain
end

-- Écoute des requêtes envoyées via RemoteEvent
hitFarmTargetEvent.OnServerEvent:Connect(function(player, targetInstance)
	if targetInstance and typeof(targetInstance) == "Instance" then
		EconomyService.processFarmHit(player, targetInstance)
	end
end)

-- Liaison automatique avec les ProximityPrompts et ClickDetectors des mannequins
local function bindDummyInteractions(dummyModel: Model)
	local prompt = dummyModel:FindFirstChildWhichIsA("ProximityPrompt", true)
	if prompt then
		prompt.Triggered:Connect(function(player)
			EconomyService.processFarmHit(player, dummyModel)
		end)
	end

	local clickDetector = dummyModel:FindFirstChildWhichIsA("ClickDetector", true)
	if clickDetector then
		clickDetector.MouseClick:Connect(function(player)
			EconomyService.processFarmHit(player, dummyModel)
		end)
	end
end

-- Recherche des mannequins existants et détection des futurs ajouts dans le Workspace
task.spawn(function()
	local world1 = Workspace:WaitForChild("World1", 15)
	if not world1 then
		warn("[EconomyService] World1 non trouvé après 15s")
		return
	end
	local farmZone = world1:WaitForChild("FarmZone", 15)
	if not farmZone then
		warn("[EconomyService] FarmZone non trouvée après 15s")
		return
	end

	for _, child in ipairs(farmZone:GetChildren()) do
		if child:IsA("Model") and child:GetAttribute("TargetType") == "FarmDummy" then
			bindDummyInteractions(child)
		end
	end

	farmZone.ChildAdded:Connect(function(child)
		if child:IsA("Model") then
			task.wait(0.2)
			if child:GetAttribute("TargetType") == "FarmDummy" then
				bindDummyInteractions(child)
			end
		end
	end)
end)

-- =============================================================================
-- SYSTÈME DE REBIRTH (déblocable à partir du Monde 3)
-- =============================================================================
local Network = require(Shared:WaitForChild("Network")) :: any
local rebirthFunction = Network.getFunction("RebirthRequest")

function EconomyService.requestRebirth(player: Player): (boolean, string?)
	local profile = DataService.getProfile(player)
	if not profile then
		return false, "Profil non chargé"
	end

	-- 1. Condition : Monde 3 débloqué
	if not profile.UnlockedWorlds or not profile.UnlockedWorlds[3] then
		return false, "Le Rebirth se débloque à partir du Monde 3 !"
	end

	-- 2. Limite max au lancement : 20 rebirths
	if profile.Rebirths >= Economy.Rebirth.MaxRebirths then
		return false, "Vous avez atteint le nombre maximum de Rebirths (20) !"
	end

	-- 3. Coût croissant en or
	local currentRebirths = profile.Rebirths or 0
	local cost = Economy.Rebirth.BaseCost * math.pow(Economy.Rebirth.CostMultiplierPerLevel, currentRebirths)
	cost = math.round(cost)

	if profile.Gold < cost then
		return false, string.format("Or insuffisant pour le Rebirth (%d or requis).", cost)
	end

	-- 4. Application du Rebirth : Réinitialisation de l'or et du niveau du joueur uniquement
	profile.Gold = 0
	profile.Level = 1
	profile.Exp = 0
	profile.Rebirths = currentRebirths + 1

	DataService.syncToClient(player)
	print(string.format("[EconomyService] %s a effectué un Rebirth (#%d) ! (+%.0f%% or, +%.0f%% chance)",
		player.Name, profile.Rebirths, profile.Rebirths * 10, profile.Rebirths * 2))

	return true, string.format("Rebirth #%d réussi ! Bonus permanent : +%d%% Or et +%d%% Chance !",
		profile.Rebirths, profile.Rebirths * 10, profile.Rebirths * 2)
end

rebirthFunction.OnServerInvoke = function(player: Player)
	return EconomyService.requestRebirth(player)
end

Players.PlayerRemoving:Connect(function(player)
	lastHitTimes[player] = nil
end)

return EconomyService

