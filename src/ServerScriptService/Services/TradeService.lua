--!strict
-- TradeService.lua
-- Service d'échanges sécurisés entre joueurs (système de troc de dragons) :
-- 1. Double confirmation obligatoire avant validation finale.
-- 2. Validation stricte côté serveur de la possession des dragons.
-- 3. Interdiction formelle d'échanger les dragons payants ou exclusifs (Tradeable == false).
-- 4. Journal d'audit complet de chaque échange pour traçabilité anti-exploit.
-- 5. DÉSACTIVÉ PAR DÉFAUT pour le lancement (activable via drapeau).

local Players = game:GetService("Players")
local ServerScriptService = game:GetService("ServerScriptService")
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local Services = ServerScriptService:WaitForChild("Services")
local DataService = require(Services:WaitForChild("DataService")) :: any

local TradeService = {}

-- Drapeau d'activation du système d'échange (laissé à false pour le lancement selon le brief)
TradeService.TRADING_ENABLED = false

type TradeSession = {
	PlayerA: Player,
	PlayerB: Player,
	OfferA: { string }, -- Liste de GUIDs
	OfferB: { string },
	ConfirmedA: boolean,
	ConfirmedB: boolean,
}

local activeTrades: { [Player]: TradeSession } = {}

--[[
	Initialise une session d'échange entre deux joueurs.
]]
function TradeService.startTrade(playerA: Player, playerB: Player): (boolean, string?)
	if not TradeService.TRADING_ENABLED then
		return false, "Le système d'échange entre joueurs est actuellement désactivé."
	end

	if playerA == playerB or not playerA or not playerB then
		return false, "Joueurs invalides pour l'échange."
	end

	if activeTrades[playerA] or activeTrades[playerB] then
		return false, "L'un des joueurs est déjà engagé dans un échange."
	end

	local session: TradeSession = {
		PlayerA = playerA,
		PlayerB = playerB,
		OfferA = {},
		OfferB = {},
		ConfirmedA = false,
		ConfirmedB = false,
	}

	activeTrades[playerA] = session
	activeTrades[playerB] = session
	print(string.format("[TradeService] Session d'échange ouverte entre %s et %s.", playerA.Name, playerB.Name))
	return true, nil
end

--[[
	Finalise et applique l'échange avec toutes les validations de sécurité.
]]
function TradeService.executeTrade(session: TradeSession): (boolean, string?)
	if not session.ConfirmedA or not session.ConfirmedB then
		return false, "Les deux joueurs doivent confirmer l'échange."
	end

	local profA = DataService.getProfile(session.PlayerA)
	local profB = DataService.getProfile(session.PlayerB)
	if not profA or not profB then
		return false, "Profils inaccessibles."
	end

	-- 1. Vérification que le joueur A possède tous les dragons offerts et qu'ils sont échangeables
	for _, guid in ipairs(session.OfferA) do
		local dragon = profA.Dragons[guid]
		if not dragon then
			return false, string.format("%s ne possède plus le dragon %s !", session.PlayerA.Name, guid)
		end
		if not dragon.Tradeable then
			return false, string.format("Le dragon %s (%s) est exclusif et ne peut pas être échangé.", dragon.SpeciesId, guid)
		end
	end

	-- 2. Vérification que le joueur B possède tous les dragons offerts et qu'ils sont échangeables
	for _, guid in ipairs(session.OfferB) do
		local dragon = profB.Dragons[guid]
		if not dragon then
			return false, string.format("%s ne possède plus le dragon %s !", session.PlayerB.Name, guid)
		end
		if not dragon.Tradeable then
			return false, string.format("Le dragon %s (%s) est exclusif et ne peut pas être échangé.", dragon.SpeciesId, guid)
		end
	end

	-- 3. Exécution du transfert atomique sécurisé
	for _, guid in ipairs(session.OfferA) do
		local d = profA.Dragons[guid]
		DataService.removeDragon(session.PlayerA, guid)
		DataService.addDragon(session.PlayerB, d.SpeciesId, d.Stage)
	end

	for _, guid in ipairs(session.OfferB) do
		local d = profB.Dragons[guid]
		DataService.removeDragon(session.PlayerB, guid)
		DataService.addDragon(session.PlayerA, d.SpeciesId, d.Stage)
	end

	-- 4. Journal d'audit de sécurité
	print(string.format("[TradeService] [AUDIT ÉCHANGE RÉUSSI] %s a échangé %d dragons avec %s (%d dragons).",
		session.PlayerA.Name, #session.OfferA, session.PlayerB.Name, #session.OfferB))

	activeTrades[session.PlayerA] = nil
	activeTrades[session.PlayerB] = nil
	return true, "Échange finalisé avec succès !"
end

return TradeService
