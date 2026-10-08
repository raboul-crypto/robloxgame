--!strict
-- BossService.lua
-- Service de gestion des Boss de passage et des Dragons de Zone :
-- 1. Boss de passage uniques (combat de portail pour ouvrir le monde suivant).
-- 2. Dragons de zone mondiaux apparaissant toutes les 30 min.
-- 3. Distribution des récompenses équitables (≥ 5 % des dégâts infligés = œuf garanti du dragon de zone).
-- 4. Immunité des boss à l'étourdissement.

local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local ServerScriptService = game:GetService("ServerScriptService")
local Workspace = game:GetService("Workspace")

local Shared = ReplicatedStorage:WaitForChild("Shared")
local Config = Shared:WaitForChild("Config")
local Worlds = require(Config:WaitForChild("Worlds")) :: any
local Dragons = require(Config:WaitForChild("Dragons")) :: any
local Economy = require(Config:WaitForChild("Economy")) :: any
local DragonModels = require(Shared:WaitForChild("DragonModels")) :: any
local Network = require(Shared:WaitForChild("Network")) :: any

local Services = ServerScriptService:WaitForChild("Services")
local DataService = require(Services:WaitForChild("DataService")) :: any

local fightBossFunction = Network.getFunction("FightBoss")
local combatEffectEvent = Network.getEvent("CombatDamageEffect")

local BossService = {}

-- Dossier dédié aux boss
local bossFolder = Instance.new("Folder")
bossFolder.Name = "Bosses"
bossFolder.Parent = Workspace

type ActiveBoss = {
	WorldId: number,
	Name: string,
	SpeciesId: string?,
	MaxHp: number,
	CurrentHp: number,
	Model: Model,
	IsZoneDragon: boolean,
	DamageContributions: { [Player]: number },
	HealthFill: Frame?,
}

local activeBosses: { [Model]: ActiveBoss } = {}
local lastZoneRewardTimes: { [string]: number } = {} -- "PlayerId_WorldId" -> timestamp

--[[
	Fait apparaître un Boss de passage ou un Dragon de Zone.
]]
function BossService.spawnBoss(worldId: number, isZoneDragon: boolean, spawnCFrame: CFrame): ActiveBoss
	local worldInfo = Worlds.List[worldId]
	local bossName = ""
	local maxHp = 1000
	local speciesId = nil

	if isZoneDragon then
		speciesId = worldInfo.ZoneDragonId
		local dragonCfg = Dragons.List[speciesId]
		bossName = "Dragon de Zone : " .. (dragonCfg and dragonCfg.DisplayName or speciesId)
		maxHp = worldInfo.BaseHp * 8
	else
		local passageBoss = worldInfo.TransitionBoss
		bossName = passageBoss.Name
		maxHp = passageBoss.Hp
		speciesId = worldInfo.ZoneDragonId -- Modèle de référence
	end

	-- Construction du modèle 3D géant
	local model = DragonModels.getModel(speciesId or "Aurore", "Adulte")
	model.Name = "Boss_" .. bossName
	model:ScaleTo(2.2) -- Boss géant imposant
	model:SetAttribute("IsBoss", true)
	model:SetAttribute("ImmuneToStun", true)

	local primary = model.PrimaryPart or model:FindFirstChildWhichIsA("BasePart")
	if primary then
		primary.Anchored = true
	end

	model:PivotTo(spawnCFrame)
	model.Parent = bossFolder

	-- Barre de vie 3D de boss
	local billboard = Instance.new("BillboardGui")
	billboard.Name = "BossHealthBar"
	billboard.Size = UDim2.fromOffset(220, 50)
	billboard.StudsOffset = Vector3.new(0, 8, 0)
	billboard.AlwaysOnTop = true
	billboard.Adornee = primary

	local titleLabel = Instance.new("TextLabel")
	titleLabel.Size = UDim2.new(1, 0, 0.45, 0)
	titleLabel.BackgroundTransparency = 1
	titleLabel.Text = "👑 " .. bossName
	titleLabel.TextColor3 = Color3.fromRGB(255, 215, 0)
	titleLabel.TextStrokeTransparency = 0.2
	titleLabel.TextSize = 15
	titleLabel.Font = Enum.Font.GothamBlack
	titleLabel.Parent = billboard

	local barBg = Instance.new("Frame")
	barBg.Size = UDim2.new(1, 0, 0.45, 0)
	barBg.Position = UDim2.new(0, 0, 0.55, 0)
	barBg.BackgroundColor3 = Color3.fromRGB(30, 20, 25)
	barBg.BorderSizePixel = 0
	barBg.Parent = billboard

	local barFill = Instance.new("Frame")
	barFill.Name = "Fill"
	barFill.Size = UDim2.new(1, 0, 1, 0)
	barFill.BackgroundColor3 = Color3.fromRGB(240, 50, 70)
	barFill.BorderSizePixel = 0
	barFill.Parent = barBg

	billboard.Parent = model

	local bossData: ActiveBoss = {
		WorldId = worldId,
		Name = bossName,
		SpeciesId = speciesId,
		MaxHp = maxHp,
		CurrentHp = maxHp,
		Model = model,
		IsZoneDragon = isZoneDragon,
		DamageContributions = {},
		HealthFill = barFill,
	}

	activeBosses[model] = bossData
	print(string.format("[BossService] Boss apparu : %s (Monde %d, %d PV)", bossName, worldId, maxHp))
	return bossData
end

--[[
	Distribue les récompenses à la défaite d'un Boss.
]]
local function onBossDefeated(boss: ActiveBoss)
	print(string.format("[BossService] Le Boss %s a été vaincu !", boss.Name))

	local now = os.time()
	local minDamageRequired = boss.MaxHp * Economy.SpecialRates.ZoneDragonMinDamagePercent

	for player, damageDealt in pairs(boss.DamageContributions) do
		local profile = DataService.getProfile(player)
		if profile and damageDealt >= minDamageRequired then
			if boss.IsZoneDragon and boss.SpeciesId then
				local rewardKey = tostring(player.UserId) .. "_" .. tostring(boss.WorldId)
				local lastReward = lastZoneRewardTimes[rewardKey] or 0

				-- Limite de récompense de dragon de zone : 1 fois par heure max
				if (now - lastReward) >= Economy.SpecialRates.ZoneDragonRewardCooldownSeconds then
					lastZoneRewardTimes[rewardKey] = now
					DataService.addDragon(player, boss.SpeciesId, "Bebe")
					DataService.addDiamonds(player, 5)
					DataService.addGold(player, 500)
					print(string.format("[BossService] 🏆 Récompense majeure attribuée à %s : Œuf de %s + 5 Diamants !", player.Name, boss.SpeciesId))
				end
			else
				-- Victoire sur le boss de passage : débloque le monde suivant
				local nextWorld = boss.WorldId + 1
				if nextWorld <= Worlds.MaxWorld then
					profile.UnlockedWorlds[nextWorld] = true
					DataService.addDiamonds(player, 10)
					DataService.syncToClient(player)
					print(string.format("[BossService] 🚪 %s a débloqué le Monde %d !", player.Name, nextWorld))
				end
			end
		end
	end

	activeBosses[boss.Model] = nil
	boss.Model:Destroy()
end

--[[
	Inflige des dégâts à un boss.
]]
function BossService.damageBoss(player: Player, bossModel: Model, amount: number)
	local boss = activeBosses[bossModel]
	if not boss or boss.CurrentHp <= 0 then return end

	boss.CurrentHp = math.max(0, boss.CurrentHp - amount)
	boss.DamageContributions[player] = (boss.DamageContributions[player] or 0) + amount

	if boss.HealthFill then
		boss.HealthFill.Size = UDim2.new(boss.CurrentHp / boss.MaxHp, 0, 1, 0)
	end

	if boss.Model.PrimaryPart then
		combatEffectEvent:FireAllClients(boss.Model.PrimaryPart.Position, amount, true, "Feu")
	end

	if boss.CurrentHp <= 0 then
		onBossDefeated(boss)
	end
end

-- Cycle d'apparition automatique du Dragon de Zone toutes les 30 minutes (1800 s)
task.spawn(function()
	while true do
		task.wait(1800) -- 30 minutes
		for worldId = 1, Worlds.MaxWorld do
			local spawnCFrame = CFrame.new(Vector3.new(0, 6, -140))
			BossService.spawnBoss(worldId, true, spawnCFrame)
		end
	end
end)

return BossService
