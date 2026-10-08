--!strict
-- StatCalcTest.server.lua
-- Script de test automatique pour la Phase 1 : vérification des formules et de l'intégrité des configs

local ReplicatedStorage = game:GetService("ReplicatedStorage")
local Shared = ReplicatedStorage:WaitForChild("Shared")
local Config = Shared:WaitForChild("Config")

local StatCalc = require(Shared:WaitForChild("StatCalc")) :: any
local Elements = require(Config:WaitForChild("Elements")) :: any
local Rarities = require(Config:WaitForChild("Rarities")) :: any
local Archetypes = require(Config:WaitForChild("Archetypes")) :: any
local Stages = require(Config:WaitForChild("Stages")) :: any
local Worlds = require(Config:WaitForChild("Worlds")) :: any
local Dragons = require(Config:WaitForChild("Dragons")) :: any

print("==================================================")
print("[StatCalcTest] DÉBUT DES VÉRIFICATIONS (PHASE 1)")
print("==================================================")

-- 1. Test de l'exemple de contrôle du brief (partie 2.7) :
-- Sillon (monde 1, Rare, Brute), Jeune, niveau 20 -> PV ≈ 180, dégâts ≈ 31
local hp, damage, speed = StatCalc.getDragonStats("Sillon", "Jeune", 20)
print(string.format("[StatCalcTest] Exemple de contrôle : Sillon (Jeune, Nv. 20) -> PV: %d | Dégâts: %d | Vitesse: %d", hp, damage, speed))

if math.abs(hp - 180) <= 1 and math.abs(damage - 31) <= 1 then
	print("[StatCalcTest] [SUCCÈS] Les stats de Sillon correspondent parfaitement aux valeurs de référence (180 PV, 31 dégâts) !")
else
	warn(string.format("[StatCalcTest] [ATTENTION] Écart détecté pour Sillon : calculé PV=%d (attendu 180), Dégâts=%d (attendu 31)", hp, damage))
end

-- 2. Test de la puissance de farm
local farmPowerCommunBebe = StatCalc.getFarmPower("Commun", "Bebe")
local farmPowerRareAdulte = StatCalc.getFarmPower("Rare", "Adulte")
print(string.format("[StatCalcTest] Puissance farm Commun Bébé: +%.1f%% | Rare Adulte: +%.1f%%", farmPowerCommunBebe * 100, farmPowerRareAdulte * 100))

-- 3. Vérification de la table des éléments
print("[StatCalcTest] Vérification des multiplicateurs élémentaires...")
local testElementCases = {
	{ atk = "Feu", def = "Plante", expected = 1.5, desc = "Feu fort contre Plante" },
	{ atk = "Feu", def = "Eau", expected = 0.75, desc = "Feu faible contre Eau" },
	{ atk = "Feu", def = "Terre", expected = 0.75, desc = "Feu faible contre Terre" },
	{ atk = "Feu", def = "Feu", expected = 0.75, desc = "Même élément (résistance)" },
	{ atk = "Feu", def = "Vol", expected = 1.0, desc = "Neutre (Feu vs Vol)" },
	{ atk = "Tenebres", def = "Vol", expected = 1.5, desc = "Ténèbres fort contre Vol" },
	{ atk = "Mineral", def = "Tenebres", expected = 1.5, desc = "Minéral fort contre Ténèbres" },
}

local elementErrors = 0
for _, case in ipairs(testElementCases) do
	local mult = StatCalc.getElementMultiplier(case.atk, case.def)
	if mult ~= case.expected then
		warn(string.format("[StatCalcTest] Erreur élément : %s vs %s -> obtenu %.2f, attendu %.2f (%s)", case.atk, case.def, mult, case.expected, case.desc))
		elementErrors += 1
	end
end

if elementErrors == 0 then
	print("[StatCalcTest] [SUCCÈS] Tous les tests élémentaires sont validés !")
end

-- 4. Vérification de l'intégrité de la liste des 40 dragons + exclusifs
print("[StatCalcTest] Vérification de l'intégrité des 40 dragons...")
local totalDragons = 0
local dragonsByWorld = { [1] = 0, [2] = 0, [3] = 0, [4] = 0, [5] = 0, [0] = 0 }
local dragonErrors = 0

for id, dragon in pairs(Dragons.List) do
	totalDragons += 1
	
	if id ~= dragon.Id then
		warn(string.format("[StatCalcTest] Incohérence ID clé/valeur pour '%s'", id))
		dragonErrors += 1
	end
	
	if not Elements.List[dragon.Element] then
		warn(string.format("[StatCalcTest] Élément inconnu '%s' pour le dragon '%s'", tostring(dragon.Element), id))
		dragonErrors += 1
	end
	
	if not Rarities.List[dragon.Rarity] then
		warn(string.format("[StatCalcTest] Rareté inconnue '%s' pour le dragon '%s'", tostring(dragon.Rarity), id))
		dragonErrors += 1
	end
	
	if not Archetypes.List[dragon.Archetype] then
		warn(string.format("[StatCalcTest] Archétype inconnu '%s' pour le dragon '%s'", tostring(dragon.Archetype), id))
		dragonErrors += 1
	end
	
	if dragonsByWorld[dragon.World] ~= nil then
		dragonsByWorld[dragon.World] += 1
	else
		warn(string.format("[StatCalcTest] Monde invalide '%s' pour le dragon '%s'", tostring(dragon.World), id))
		dragonErrors += 1
	end
end

print(string.format("[StatCalcTest] Répartition par monde : M1=%d, M2=%d, M3=%d, M4=%d, M5=%d, Exclusifs=%d (Total = %d)",
	dragonsByWorld[1], dragonsByWorld[2], dragonsByWorld[3], dragonsByWorld[4], dragonsByWorld[5], dragonsByWorld[0], totalDragons))

if dragonErrors == 0 and totalDragons == 42 and dragonsByWorld[1] == 8 and dragonsByWorld[2] == 8 and dragonsByWorld[3] == 8 and dragonsByWorld[4] == 8 and dragonsByWorld[5] == 8 then
	print("[StatCalcTest] [SUCCÈS] Les 40 dragons et 2 exclusifs sont parfaitement configurés et valides !")
else
	warn(string.format("[StatCalcTest] [ERREUR] Problème dans la liste des dragons (%d erreurs détectées).", dragonErrors))
end

print("==================================================")
print("[StatCalcTest] FIN DES VÉRIFICATIONS (PHASE 1)")
print("==================================================")
