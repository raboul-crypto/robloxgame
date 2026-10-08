--!strict
-- CaptureService.lua
-- Service d'apprivoisement et de capture des dragons sauvages :
-- Condition : PV du dragon sauvage < 30 %.
-- Taux de réussite : 25 % de base (+10 % par niveau d'appât).
-- En cas d'échec : le dragon récupère 50 % de ses PV max et le combat continue.
-- En cas de succès : le dragon rejoint l'inventaire du joueur avec son stade d'origine.

local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local ServerScriptService = game:GetService("ServerScriptService")

local Shared = ReplicatedStorage:WaitForChild("Shared")
local Config = Shared:WaitForChild("Config")

local Economy = require(Config:WaitForChild("Economy")) :: any
local Dragons = require(Config:WaitForChild("Dragons")) :: any

local Services = ServerScriptService:WaitForChild("Services")
local DataService = require(Services:WaitForChild("DataService")) :: any

-- Événements réseau
local eventsFolder = ReplicatedStorage:WaitForChild("Events")

local captureFunction = eventsFolder:FindFirstChild("AttemptCapture")
if not captureFunction then
	captureFunction = Instance.new("RemoteFunction")
	captureFunction.Name = "AttemptCapture"
	captureFunction.Parent = eventsFolder
end

local CaptureService = {}

--[[
	Tente d'apprivoiser un dragon sauvage.
]]
function CaptureService.attemptCapture(player: Player, targetModel: Model?, baitTier: number?): (boolean, any?, string?)
	if not player or not targetModel or not targetModel:IsA("Model") then
		return false, nil, "Cible invalide"
	end

	local char = player.Character
	local root = char and char:FindFirstChild("HumanoidRootPart") :: BasePart?
	local targetPrimary = targetModel.PrimaryPart
	if not root or not targetPrimary then
		return false, nil, "Position introuvable"
	end

	-- Vérification de la distance (maximum 20 studs)
	local distance = (root.Position - targetPrimary.Position).Magnitude
	if distance > 22 then
		return false, nil, "Trop éloigné pour utiliser un appât !"
	end

	local speciesId = targetModel:GetAttribute("SpeciesId") :: string?
	if not speciesId or not Dragons.List[speciesId] then
		return false, nil, "Ce dragon ne peut pas être apprivoisé."
	end

	-- Récupération de la barre de vie
	local billboard = targetModel:FindFirstChild("WildHealthBar")
	local barBg = billboard and billboard:FindFirstChild("Frame")
	local barFill = barBg and barBg:FindFirstChild("Fill") :: Frame?

	local currentHpRatio = barFill and (barFill.Size.X.Scale) or 1.0

	-- 1. Condition obligatoire : PV < 30 %
	if currentHpRatio > Economy.Capture.HpThresholdPercent then
		local percentInt = math.floor(currentHpRatio * 100)
		return false, nil, string.format("Le dragon est trop fort (%d%% PV). Affaiblissez-le sous 30%% de PV !", percentInt)
	end

	-- 2. Calcul du taux de réussite (25 % de base + 10 % par tier d'appât)
	baitTier = baitTier or 0
	local successChance = Economy.Capture.BaseSuccessRate + (baitTier * Economy.Capture.BaitTierBonusRate)
	local roll = math.random()

	if roll <= successChance then
		-- SUCCÈS : Ajout du dragon à l'inventaire
		local addSuccess, dragonRec = DataService.addDragon(player, speciesId, "Bebe")
		targetModel:Destroy()

		print(string.format("[CaptureService] %s a réussi à apprivoiser %s sauvage !", player.Name, speciesId))
		return true, dragonRec, "Apprivoisement réussi ! Le dragon a rejoint votre inventaire."
	else
		-- ÉCHEC : Le dragon récupère 50 % de ses PV
		local newRatio = math.min(1.0, currentHpRatio + Economy.Capture.FailureHealPercent)
		if barFill then
			barFill.Size = UDim2.new(newRatio, 0, 1, 0)
		end

		print(string.format("[CaptureService] Échec de capture de %s par %s. Le dragon a repris 50%% de PV.", speciesId, player.Name))
		return false, nil, "L'appât a échoué ! Le dragon sauvage s'est ressaisi et récupère 50 % de ses PV."
	end
end

captureFunction.OnServerInvoke = function(player: Player, targetModel: Model, baitTier: number)
	local success, result, msg = CaptureService.attemptCapture(player, targetModel, baitTier)
	return success, result, msg
end

return CaptureService
