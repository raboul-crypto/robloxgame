--!strict
-- MonetizationService.lua
-- Service officiel de monétisation via MarketplaceService :
-- 1. Traitement fiable et idempotent des Developer Products avec ProcessReceipt.
-- 2. Vérification et application immédiate des Game Passes à la connexion et à l'achat.
-- 3. Historique anti-doublon des reçus traités pour éviter les doubles crédits.

local Players = game:GetService("Players")
local MarketplaceService = game:GetService("MarketplaceService")
local ServerScriptService = game:GetService("ServerScriptService")
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local Shared = ReplicatedStorage:WaitForChild("Shared")
local Config = Shared:WaitForChild("Config")
local Monetization = require(Config:WaitForChild("Monetization")) :: any

local Services = ServerScriptService:WaitForChild("Services")
local DataService = require(Services:WaitForChild("DataService")) :: any

local MonetizationService = {}

-- Historique en mémoire des reçus traités pour cette session (anti-rejeu)
local processedReceipts: { [string]: boolean } = {}

--[[
	Vérifie et applique les Game Passes possédés par un joueur lors de sa connexion.
]]
function MonetizationService.checkGamePasses(player: Player)
	local profile = DataService.getProfile(player)
	if not profile then return end

	for passKey, passInfo in pairs(Monetization.GamePasses) do
		if passInfo.Id and passInfo.Id > 0 then
			local success, owns = pcall(function()
				return MarketplaceService:UserOwnsGamePassAsync(player.UserId, passInfo.Id)
			end)
			if success and owns then
				profile.GamePasses[passKey] = true
				print(string.format("[MonetizationService] Game Pass actif pour %s : %s", player.Name, passInfo.Name))
			end
		end
	end

	DataService.syncToClient(player)
end

--[[
	Callback officiel de traitement des reçus d'achats consommables (Developer Products).
]]
MarketplaceService.ProcessReceipt = function(receiptInfo)
	local purchaseId = receiptInfo.PurchaseId
	if processedReceipts[purchaseId] then
		return Enum.ProductPurchaseDecision.PurchaseGranted
	end

	local player = Players:GetPlayerByUserId(receiptInfo.PlayerId)
	if not player then
		-- Joueur déconnecté, Roblox réessaiera à sa prochaine connexion
		return Enum.ProductPurchaseDecision.NotProcessedYet
	end

	local profile = DataService.getProfile(player)
	if not profile then
		return Enum.ProductPurchaseDecision.NotProcessedYet
	end

	local productId = receiptInfo.ProductId
	local awarded = false

	-- Identification du produit acheté
	for productKey, productInfo in pairs(Monetization.Products) do
		if productInfo.Id == productId or (productInfo.Id == 0 and productId == 0) then
			-- 1. Packs de Diamants
			if productInfo.DiamondsAmount then
				DataService.addDiamonds(player, productInfo.DiamondsAmount)
				awarded = true
			end

			-- 2. Boost temporaire d'or ou de chance
			if productInfo.Multiplier and productInfo.DurationSeconds then
				profile.GamePasses["TempBoostGold"] = true
				awarded = true
			end

			-- 3. Œuf exclusif
			if productKey == "OeufExclusifMonde" then
				DataService.addDragon(player, "Exclusif1", "Bebe")
				awarded = true
			end
			break
		end
	end

	if awarded then
		processedReceipts[purchaseId] = true
		DataService.syncToClient(player)
		print(string.format("[MonetizationService] Achat validé pour %s (Produit ID: %d)", player.Name, productId))
		return Enum.ProductPurchaseDecision.PurchaseGranted
	else
		return Enum.ProductPurchaseDecision.NotProcessedYet
	end
end

-- Détection d'achat de Game Pass en jeu
MarketplaceService.PromptGamePassPurchaseFinished:Connect(function(player, passId, wasPurchased)
	if wasPurchased then
		local profile = DataService.getProfile(player)
		if profile then
			for passKey, passInfo in pairs(Monetization.GamePasses) do
				if passInfo.Id == passId then
					profile.GamePasses[passKey] = true
					DataService.syncToClient(player)
					print(string.format("[MonetizationService] Nouveau Game Pass acquis par %s : %s", player.Name, passInfo.Name))
					break
				end
			end
		end
	end
end)

Players.PlayerAdded:Connect(function(player)
	task.delay(1, function()
		MonetizationService.checkGamePasses(player)
	end)
end)

return MonetizationService
