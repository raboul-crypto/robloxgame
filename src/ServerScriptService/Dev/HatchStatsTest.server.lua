--!strict
-- HatchStatsTest.server.lua
-- Script de test statistique pour la Phase 4 :
-- Simule 10 000 tirages d'œufs communs du Monde 1 et vérifie la conformité avec les taux 60/30/9/1.

local ServerScriptService = game:GetService("ServerScriptService")
local Services = ServerScriptService:WaitForChild("Services")
local HatchingService = require(Services:WaitForChild("HatchingService")) :: any

print("==================================================")
print("[HatchStatsTest] DÉBUT DE LA SIMULATION (10 000 TIRAGES)")
print("==================================================")

local NUM_SIMULATIONS = 10000
local counts = {
	Commun = 0,
	Rare = 0,
	Epique = 0,
	Legendaire = 0,
	Mythique = 0,
}

for _ = 1, NUM_SIMULATIONS do
	local rarity = HatchingService.rollRarity(1, "Common", 0)
	counts[rarity] = (counts[rarity] or 0) + 1
end

local expectedRates = {
	Commun = 60.0,
	Rare = 30.0,
	Epique = 9.0,
	Legendaire = 1.0,
}

local hasSignificantDeviation = false

print(string.format("[HatchStatsTest] Résultats sur %d tirages :", NUM_SIMULATIONS))
for _, rarityName in ipairs({ "Commun", "Rare", "Epique", "Legendaire" }) do
	local count = counts[rarityName] or 0
	local percent = (count / NUM_SIMULATIONS) * 100
	local expected = expectedRates[rarityName] or 0
	local diff = math.abs(percent - expected)

	print(string.format("  • %-10s : %5d tirages (%5.2f%% | attendu %4.1f%% | écart: %+.2f%%)",
		rarityName, count, percent, expected, percent - expected))

	-- Tolérance statistique raisonnable sur 10 000 tirages (~1.5 % max d'écart)
	if diff > 1.8 then
		hasSignificantDeviation = true
	end
end

if not hasSignificantDeviation then
	print("[HatchStatsTest] [SUCCÈS] Les taux observés sont conformes aux probabilités 60 / 30 / 9 / 1 !")
else
	warn("[HatchStatsTest] [ATTENTION] Écart statistique supérieur à la normale.")
end

print("==================================================")
print("[HatchStatsTest] FIN DU TEST STATISTIQUE")
print("==================================================")
