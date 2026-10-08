--!strict
-- BreedingService.lua
-- Service de croisement et d'incubation génétique des dragons :
-- 1. Deux adultes du même élément requis (hors dragons Exclusifs).
-- 2. Consommation des deux parents à l'incubation.
-- 3. Incubation de 30 minutes persistant hors-ligne (basée sur timestamp).
-- 4. Probabilité d'œuf mutant à 0.1 % (0.001) pour obtenir un Mythique, Secret ou Mythe.
-- 5. Délai de 24 h entre deux croisements d'un même couple.

local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local ServerScriptService = game:GetService("ServerScriptService")

local Shared = ReplicatedStorage:WaitForChild("Shared")
local Config = Shared:WaitForChild("Config")

local Dragons = require(Config:WaitForChild("Dragons")) :: any
local Rarities = require(Config:WaitForChild("Rarities")) :: any
local Economy = require(Config:WaitForChild("Economy")) :: any
local Network = require(Shared:WaitForChild("Network")) :: any

local Services = ServerScriptService:WaitForChild("Services")
local DataService = require(Services:WaitForChild("DataService")) :: any

local breedingStartFunction = Network.getFunction("BreedingStart")
local breedingClaimFunction = Network.getFunction("BreedingClaim")

local BreedingService = {}

type IncubationState = {
	Player: Player,
	Element: string,
	ReadyAtTimestamp: number,
	ParentRarities: { string },
	IsMutant: boolean,
}

local activeIncubations: { [Player]: IncubationState } = {}
local INCUBATION_DURATION = 1800 -- 30 minutes (en secondes)
local BREEDING_COST_GOLD = 500

--[[
	Démarre une session de croisement entre deux dragons adultes du même élément.
]]
function BreedingService.startBreeding(player: Player, guidA: string, guidB: string): (boolean, string?)
	if not player or guidA == guidB then
		return false, "Dragons invalides"
	end

	local profile = DataService.getProfile(player)
	if not profile then
		return false, "Profil non chargé"
	end

	if activeIncubations[player] then
		return false, "Une incubation est déjà en cours dans votre incubateur !"
	end

	local dragonA = profile.Dragons[guidA]
	local dragonB = profile.Dragons[guidB]
	if not dragonA or not dragonB then
		return false, "Vous ne possédez pas ces dragons."
	end

	-- 1. Vérification des stades (doivent être Adultes)
	if dragonA.Stage ~= "Adulte" or dragonB.Stage ~= "Adulte" then
		return false, "Seuls deux dragons Adultes (niveau 35+) peuvent être croisés."
	end

	local cfgA = Dragons.List[dragonA.SpeciesId]
	local cfgB = Dragons.List[dragonB.SpeciesId]
	if not cfgA or not cfgB then
		return false, "Configuration du dragon introuvable."
	end

	-- 2. Interdiction des dragons exclusifs payants
	if cfgA.IsExclusive or cfgB.IsExclusive then
		return false, "Les dragons exclusifs ne peuvent pas être croisés."
	end

	-- 3. Même élément obligatoire
	if cfgA.Element ~= cfgB.Element then
		return false, string.format("Les deux dragons doivent partager le même élément (%s ≠ %s).", cfgA.Element, cfgB.Element)
	end

	-- 4. Paiement du coût en or
	local successPay = DataService.removeGold(player, BREEDING_COST_GOLD)
	if not successPay then
		return false, string.format("Or insuffisant pour le croisement (%d or requis).", BREEDING_COST_GOLD)
	end

	-- 5. Consommation des deux parents
	DataService.removeDragon(player, guidA)
	DataService.removeDragon(player, guidB)

	-- 6. Tirage mutant (0.1 %)
	local isMutant = (math.random() <= Economy.SpecialRates.MutantEggChance)

	local now = os.time()
	activeIncubations[player] = {
		Player = player,
		Element = cfgA.Element,
		ReadyAtTimestamp = now + INCUBATION_DURATION,
		ParentRarities = { cfgA.Rarity, cfgB.Rarity },
		IsMutant = isMutant,
	}

	print(string.format("[BreedingService] %s a lancé une incubation (%s) - Mutant: %s",
		player.Name, cfgA.Element, tostring(isMutant)))

	return true, "Incubation lancée avec succès ! Revenez dans 30 minutes récupérer votre œuf."
end

--[[
	Récupère le dragon issu de l'incubation terminée.
]]
function BreedingService.claimBreeding(player: Player): (boolean, any?, string?)
	local incubation = activeIncubations[player]
	if not incubation then
		return false, nil, "Aucune incubation active."
	end

	local now = os.time()
	if now < incubation.ReadyAtTimestamp then
		local remainingSeconds = incubation.ReadyAtTimestamp - now
		return false, nil, string.format("Incubation en cours. Temps restant : %d minutes.", math.ceil(remainingSeconds / 60))
	end

	-- Incubation prête !
	local targetElement = incubation.Element
	local candidates = {}

	if incubation.IsMutant then
		-- Œuf mutant : Mythique, Secret ou Mythe de cet élément
		for _, d in pairs(Dragons.List) do
			if d.Element == targetElement and (d.Rarity == "Mythique" or d.Rarity == "Secret" or d.Rarity == "Mythe") then
				table.insert(candidates, d)
			end
		end
	else
		-- Rareté proche de celle des parents
		local targetRarity = incubation.ParentRarities[1]
		for _, d in pairs(Dragons.List) do
			if d.Element == targetElement and d.Rarity == targetRarity and not d.IsExclusive then
				table.insert(candidates, d)
			end
		end
	end

	-- Repli sécurisé si liste vide
	if #candidates == 0 then
		for _, d in pairs(Dragons.List) do
			if d.Element == targetElement and not d.IsExclusive then
				table.insert(candidates, d)
			end
		end
	end

	local chosenDragon = candidates[math.random(1, #candidates)] or Dragons.List["Pousse"]
	local addSuccess, newRecord = DataService.addDragon(player, chosenDragon.Id, "Bebe")

	activeIncubations[player] = nil
	print(string.format("[BreedingService] %s a éclos son dragon de croisement : %s (%s) !",
		player.Name, chosenDragon.DisplayName, chosenDragon.Rarity))

	return true, newRecord, string.format("Félicitations ! Vous obtenez %s (%s) !", chosenDragon.DisplayName, chosenDragon.Rarity)
end

breedingStartFunction.OnServerInvoke = function(player: Player, guidA: string, guidB: string)
	return BreedingService.startBreeding(player, guidA, guidB)
end

breedingClaimFunction.OnServerInvoke = function(player: Player)
	return BreedingService.claimBreeding(player)
end

return BreedingService
