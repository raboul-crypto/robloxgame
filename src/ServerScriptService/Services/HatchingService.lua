--!strict
-- HatchingService.lua
-- Service d'achat et d'éclosion des œufs de dragons.
-- Tous les tirages sont effectués à 100 % côté serveur avec les probabilités pondérées officielles.

local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local ServerScriptService = game:GetService("ServerScriptService")

local Shared = ReplicatedStorage:WaitForChild("Shared")
local Config = Shared:WaitForChild("Config")

local Economy = require(Config:WaitForChild("Economy")) :: any
local Worlds = require(Config:WaitForChild("Worlds")) :: any
local Dragons = require(Config:WaitForChild("Dragons")) :: any
local Rarities = require(Config:WaitForChild("Rarities")) :: any

local Services = ServerScriptService:WaitForChild("Services")
local DataService = require(Services:WaitForChild("DataService")) :: any

-- Événements réseau
local eventsFolder = ReplicatedStorage:WaitForChild("Events")

local buyEggFunction = eventsFolder:FindFirstChild("BuyEgg")
if not buyEggFunction then
	buyEggFunction = Instance.new("RemoteFunction")
	buyEggFunction.Name = "BuyEgg"
	buyEggFunction.Parent = eventsFolder
end

local hatchResultEvent = eventsFolder:FindFirstChild("HatchResult")
if not hatchResultEvent then
	hatchResultEvent = Instance.new("RemoteEvent")
	hatchResultEvent.Name = "HatchResult"
	hatchResultEvent.Parent = eventsFolder
end

local HatchingService = {}

local lastHatchTimes: { [Player]: number } = {}
local HATCH_COOLDOWN = 1.0 -- 1 seconde entre deux achats

--[[
	Effectue un tirage pondéré de rareté selon le type d'œuf et le monde.
]]
function HatchingService.rollRarity(worldId: number, eggType: string, playerRebirths: number?): string
	playerRebirths = playerRebirths or 0
	local ratesTable = Economy.EggRates.Common

	if eggType == "Rng" then
		ratesTable = (worldId >= 4) and Economy.EggRates.RngAdvanced or Economy.EggRates.RngStandard
	elseif eggType == "Diamond" then
		ratesTable = Economy.EggRates.Diamond
	end

	-- Bonus de chance du Rebirth (+2 % par rebirth)
	local luckBonus = playerRebirths * Economy.Rebirth.LuckBonusPerRebirth

	-- Tirage entre 0 et 1
	local roll = math.random()

	-- Tirage avec application des seuils cumulés
	local cumulative = 0
	for _, rarityName in ipairs(Rarities.Tiers) do
		local baseChance = ratesTable[rarityName] or 0
		if baseChance > 0 then
			-- Les raretés supérieures à Commun bénéficient du bonus de chance
			local adjustedChance = baseChance
			if rarityName ~= "Commun" then
				adjustedChance = baseChance * (1 + luckBonus)
			end

			cumulative += adjustedChance
			if roll <= cumulative then
				return rarityName
			end
		end
	end

	-- Sécurité par défaut : rareté la plus basse disponible dans l'œuf
	return "Commun"
end

--[[
	Choisit aléatoirement un dragon parmi ceux de la rareté tirée dans le monde indiqué.
]]
function HatchingService.rollDragonFromRarity(worldId: number, rarity: string): any
	local candidates = Dragons.getByRarityAndWorld(rarity, worldId)
	if #candidates == 0 then
		-- Si aucun dragon de cette rareté dans ce monde, repli sur tous les dragons de cette rareté
		local fallback = {}
		for _, d in pairs(Dragons.List) do
			if d.Rarity == rarity and not d.IsExclusive then
				table.insert(fallback, d)
			end
		end
		if #fallback > 0 then
			return fallback[math.random(1, #fallback)]
		else
			-- Secours ultime : premier dragon du monde
			local mDragons = Dragons.getByWorld(worldId)
			return mDragons[1] or Dragons.List["Pousse"]
		end
	end

	return candidates[math.random(1, #candidates)]
end

--[[
	Achète et fait éclore un œuf pour un joueur.
	Vérifie le solde en or, déduit le montant, effectue le tirage, et ajoute le dragon au profil.
]]
function HatchingService.purchaseEgg(player: Player, worldId: number, eggType: string): (boolean, any?, string?)
	if not player then
		return false, nil, "Joueur invalide"
	end

	worldId = worldId or 1
	eggType = eggType or "Common"

	-- Cooldown anti-spam
	local now = os.clock()
	local lastHatch = lastHatchTimes[player] or 0
	if (now - lastHatch) < HATCH_COOLDOWN then
		return false, nil, "Veuillez patienter entre deux éclosions."
	end

	local worldInfo = Worlds.List[worldId]
	if not worldInfo then
		return false, nil, "Monde introuvable"
	end

	local price = worldInfo.EggPrices.Common or 100
	local isDiamondEgg = (eggType == "Diamond")
	if isDiamondEgg then
		price = worldInfo.EggPrices.Diamond or 150
	elseif eggType == "Rng" then
		price = worldInfo.EggPrices.Rng or 5000
	end

	local profile = DataService.getProfile(player)
	if not profile then
		return false, nil, "Profil non chargé"
	end

	-- Déduction de la monnaie sécurisée côté serveur (Diamants ou Or)
	local successDeduct = false
	if isDiamondEgg then
		successDeduct = DataService.removeDiamonds(player, price)
		if not successDeduct then
			return false, nil, "Diamants insuffisants ! (150 requis)"
		end
	else
		successDeduct = DataService.removeGold(player, price)
		if not successDeduct then
			return false, nil, "Or insuffisant !"
		end
	end

	lastHatchTimes[player] = now

	-- Tirage de la rareté et du dragon
	local rolledRarity = HatchingService.rollRarity(worldId, eggType, profile.Rebirths or 0)
	local rolledDragon = HatchingService.rollDragonFromRarity(worldId, rolledRarity)

	-- Ajout au profil du joueur via DataService (bébé niveau 1)
	local addSuccess, dragonRecord = DataService.addDragon(player, rolledDragon.Id, "Bebe")

	-- Chance bonus d'obtenir 1 diamant (~12 %)
	local diamondAwarded = false
	if math.random() <= Economy.SpecialRates.DiamondChanceOnHatch then
		DataService.addDiamonds(player, 1)
		diamondAwarded = true
	end

	-- Données renvoyées au client pour l'animation d'éclosion
	local resultData = {
		DragonId = rolledDragon.Id,
		DisplayName = rolledDragon.DisplayName,
		Element = rolledDragon.Element,
		Rarity = rolledDragon.Rarity,
		Archetype = rolledDragon.Archetype,
		Stage = "Bebe",
		DiamondAwarded = diamondAwarded,
		Record = dragonRecord,
	}

	hatchResultEvent:FireClient(player, resultData)
	print(string.format("[HatchingService] %s a fait éclore un œuf : %s (%s, %s)",
		player.Name, rolledDragon.DisplayName, rolledDragon.Rarity, rolledDragon.Element))

	return true, resultData, nil
end

-- Écoute de la fonction distante invoquée par le client
buyEggFunction.OnServerInvoke = function(player: Player, worldId: number, eggType: string)
	local success, result, errMsg = HatchingService.purchaseEgg(player, worldId, eggType)
	return success, result, errMsg
end

Players.PlayerRemoving:Connect(function(player)
	lastHatchTimes[player] = nil
end)

return HatchingService
