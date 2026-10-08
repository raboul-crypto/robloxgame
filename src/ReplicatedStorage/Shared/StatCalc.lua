--!strict
-- StatCalc.lua
-- Formules mathématiques du jeu : stats d'un dragon, multiplicateurs d'éléments, puissance de farm

local ReplicatedStorage = game:GetService("ReplicatedStorage")
local Config = ReplicatedStorage:WaitForChild("Shared"):WaitForChild("Config")

local Elements = require(Config:WaitForChild("Elements")) :: any
local Rarities = require(Config:WaitForChild("Rarities")) :: any
local Archetypes = require(Config:WaitForChild("Archetypes")) :: any
local Stages = require(Config:WaitForChild("Stages")) :: any
local Worlds = require(Config:WaitForChild("Worlds")) :: any
local Dragons = require(Config:WaitForChild("Dragons")) :: any
local Combat = require(Config:WaitForChild("Combat")) :: any

local StatCalc = {}

--[[
	Calcule les statistiques complètes d'un dragon (PV, dégâts, vitesse).
	Formule : stat finale = stat de base du monde × mult. rareté × mult. archétype × mult. stade × (1 + 0,06 × (niveau - 1))
	
	@param dragonId string Identifiant du dragon (ex: "Sillon")
	@param stage string Stade d'évolution ("Bebe", "Jeune", "Adulte")
	@param level number Niveau du dragon (1 à 50)
	@return number, number, number PV, Dégâts, Vitesse
]]
function StatCalc.getDragonStats(dragonId: string, stage: string, level: number): (number, number, number)
	local dragon = Dragons.List[dragonId]
	assert(dragon, "[StatCalc] Dragon introuvable : " .. tostring(dragonId))

	local worldInfo = Worlds.List[dragon.World]
	local baseHp = worldInfo and worldInfo.BaseHp or 100
	local baseDamage = worldInfo and worldInfo.BaseDamage or 10

	local rarityInfo = Rarities.List[dragon.Rarity]
	local rarityMult = rarityInfo and rarityInfo.CombatMultiplier or 1.0

	local archetypeInfo = Archetypes.List[dragon.Archetype]
	local archepHpMult = archetypeInfo and archetypeInfo.HpMultiplier or 1.0
	local archepDmgMult = archetypeInfo and archetypeInfo.DamageMultiplier or 1.0
	local archepSpeedMult = archetypeInfo and archetypeInfo.SpeedMultiplier or 1.0

	local stageInfo = Stages.List[stage]
	local stageMult = stageInfo and stageInfo.StatMultiplier or 1.0

	level = math.clamp(level, 1, Stages.MaxLevel)
	local levelMult = 1 + 0.06 * (level - 1)

	local rawHp = baseHp * rarityMult * archepHpMult * stageMult * levelMult
	local rawDamage = baseDamage * rarityMult * archepDmgMult * stageMult * levelMult
	local rawSpeed = Combat.PetCombat.BaseSpeed * archepSpeedMult

	-- Arrondi propre
	local finalHp = math.round(rawHp)
	local finalDamage = math.round(rawDamage)
	local finalSpeed = math.round(rawSpeed)

	return finalHp, finalDamage, finalSpeed
end

--[[
	Calcule la puissance de farm d'un dragon (bonus appliqué aux gains d'or).
	Puissance effective = puissance de base de la rareté × multiplicateur de stade.
	
	@param rarity string Identifiant de la rareté ("Commun", "Rare", ...)
	@param stage string Identifiant du stade ("Bebe", "Jeune", "Adulte")
	@return number Puissance effective (ex: 0.20 pour +20%)
]]
function StatCalc.getFarmPower(rarity: string, stage: string): number
	local rarityInfo = Rarities.List[rarity]
	local basePower = rarityInfo and rarityInfo.FarmPower or 0.10

	local stageInfo = Stages.List[stage]
	local stageMultiplier = stageInfo and stageInfo.FarmPowerMultiplier or 1.0

	return basePower * stageMultiplier
end

--[[
	Calcule le multiplicateur de dégâts entre l'élément de l'attaquant et du défenseur.
	Règles :
	- Même élément : 0.75 (résistance)
	- Attaque forte : 1.5
	- Attaque faible : 0.75
	- Neutre : 1.0
	
	@param attackElement string Élément du lanceur
	@param defenderElement string Élément de la cible
	@return number Multiplicateur de dégâts
]]
function StatCalc.getElementMultiplier(attackElement: string, defenderElement: string): number
	if attackElement == defenderElement then
		return Elements.Multipliers.SameElement
	end

	local elementData = Elements.List[attackElement]
	if not elementData then
		return Elements.Multipliers.Neutral
	end

	if elementData.StrongAgainst and elementData.StrongAgainst[defenderElement] then
		return Elements.Multipliers.Strong
	elseif elementData.WeakAgainst and elementData.WeakAgainst[defenderElement] then
		return Elements.Multipliers.Weak
	end

	return Elements.Multipliers.Neutral
end

return StatCalc
