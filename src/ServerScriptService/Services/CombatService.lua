--!strict
-- CombatService.lua
-- Service de gestion du combat complet :
-- 1. Apparition et comportement des dragons sauvages errants dans le Monde 1.
-- 2. Attaques automatiques des dragons équipés vers la cible désignée avec multiplicateurs élémentaires et statuts.
-- 3. Riposte des dragons sauvages sur le joueur (3 % des PV max par coup).
-- 4. Régénération hors combat (2 %/s après 5 s), gestion des K.O. et mort du joueur (perte 5 % or, respawn, protection 3 s).
-- 5. Récompenses de victoire : XP joueur, XP dragons (évolution), or, 12 % diamant, et chance d'œuf de combat (5 à 15 %).

local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local ServerScriptService = game:GetService("ServerScriptService")
local Workspace = game:GetService("Workspace")

local Shared = ReplicatedStorage:WaitForChild("Shared")
local Config = Shared:WaitForChild("Config")

local Combat = require(Config:WaitForChild("Combat")) :: any
local Elements = require(Config:WaitForChild("Elements")) :: any
local Dragons = require(Config:WaitForChild("Dragons")) :: any
local Worlds = require(Config:WaitForChild("Worlds")) :: any
local Economy = require(Config:WaitForChild("Economy")) :: any
local StatCalc = require(Shared:WaitForChild("StatCalc")) :: any
local DragonModels = require(Shared:WaitForChild("DragonModels")) :: any

local Services = ServerScriptService:WaitForChild("Services")
local DataService = require(Services:WaitForChild("DataService")) :: any

-- Événements réseau
local eventsFolder = ReplicatedStorage:WaitForChild("Events")

local selectTargetEvent = eventsFolder:FindFirstChild("SelectCombatTarget")
if not selectTargetEvent then
	selectTargetEvent = Instance.new("RemoteEvent")
	selectTargetEvent.Name = "SelectCombatTarget"
	selectTargetEvent.Parent = eventsFolder
end

local combatEffectEvent = eventsFolder:FindFirstChild("CombatDamageEffect")
if not combatEffectEvent then
	combatEffectEvent = Instance.new("RemoteEvent")
	combatEffectEvent.Name = "CombatDamageEffect"
	combatEffectEvent.Parent = eventsFolder
end

local playerHealthSyncEvent = eventsFolder:FindFirstChild("PlayerHealthSync")
if not playerHealthSyncEvent then
	playerHealthSyncEvent = Instance.new("RemoteEvent")
	playerHealthSyncEvent.Name = "PlayerHealthSync"
	playerHealthSyncEvent.Parent = eventsFolder
end

local CombatService = {}

-- Dossier contenant les dragons sauvages
local wildFolder = Instance.new("Folder")
wildFolder.Name = "WildDragons"
wildFolder.Parent = Workspace

-- Types internes
type WildDragon = {
	Id: string,
	SpeciesId: string,
	DisplayName: string,
	Element: string,
	Rarity: string,
	Stage: string,
	Model: Model,
	MaxHp: number,
	CurrentHp: number,
	SpawnOrigin: Vector3,
	LastAttackTime: number,
	HealthFill: Frame?,
	IsDead: boolean,
}

type PlayerCombatState = {
	CurrentHp: number,
	MaxHp: number,
	TargetDragon: WildDragon?,
	LastCombatTime: number,
	IsProtected: boolean,
}

local wildDragons: { [Model]: WildDragon } = {}
local playerStates: { [Player]: PlayerCombatState } = {}

--[[
	Initialise l'état de combat d'un joueur.
]]
local function initPlayerCombat(player: Player)
	local profile = DataService.getProfile(player)
	local level = profile and profile.Level or 1
	local maxHp = Combat.getPlayerMaxHp(level)

	playerStates[player] = {
		CurrentHp = maxHp,
		MaxHp = maxHp,
		TargetDragon = nil,
		LastCombatTime = 0,
		IsProtected = false,
	}

	playerHealthSyncEvent:FireClient(player, maxHp, maxHp)
end

--[[
	Crée un dragon sauvage dans le monde avec sa barre de vie 3D.
]]
function CombatService.spawnWildDragon(speciesId: string, position: Vector3): WildDragon
	local dragonConfig = Dragons.List[speciesId] or Dragons.List["Pousse"]
	local stage = "Bebe"
	local maxHp = Worlds.List[1].WildHp.Bebe or 80

	local model = DragonModels.getModel(speciesId, stage)
	model.Name = "Wild_" .. speciesId
	model:SetAttribute("IsWild", true)
	model:SetAttribute("SpeciesId", speciesId)

	local primary = model.PrimaryPart or model:FindFirstChildWhichIsA("BasePart")
	if primary then
		primary.Anchored = true
	end

	model:PivotTo(CFrame.new(position) * CFrame.Angles(0, math.rad(math.random(0, 360)), 0))
	model.Parent = wildFolder

	-- Barre de vie 3D (BillboardGui)
	local billboard = Instance.new("BillboardGui")
	billboard.Name = "WildHealthBar"
	billboard.Size = UDim2.fromOffset(130, 36)
	billboard.StudsOffset = Vector3.new(0, 3.5, 0)
	billboard.AlwaysOnTop = true
	billboard.Adornee = primary

	local nameLabel = Instance.new("TextLabel")
	nameLabel.Size = UDim2.new(1, 0, 0.45, 0)
	nameLabel.BackgroundTransparency = 1
	nameLabel.Text = string.format("%s (%s)", dragonConfig.DisplayName, dragonConfig.Element)
	nameLabel.TextColor3 = Color3.fromRGB(255, 255, 255)
	nameLabel.TextStrokeTransparency = 0.2
	nameLabel.TextSize = 13
	nameLabel.Font = Enum.Font.GothamBold
	nameLabel.Parent = billboard

	local barBg = Instance.new("Frame")
	barBg.Size = UDim2.new(1, 0, 0.45, 0)
	barBg.Position = UDim2.new(0, 0, 0.55, 0)
	barBg.BackgroundColor3 = Color3.fromRGB(35, 35, 45)
	barBg.BorderSizePixel = 0
	barBg.Parent = billboard

	local bgCorner = Instance.new("UICorner")
	bgCorner.CornerRadius = UDim.new(0, 4)
	bgCorner.Parent = barBg

	local barFill = Instance.new("Frame")
	barFill.Name = "Fill"
	barFill.Size = UDim2.new(1, 0, 1, 0)
	barFill.BackgroundColor3 = Color3.fromRGB(80, 220, 100)
	barFill.BorderSizePixel = 0
	barFill.Parent = barBg

	local fillCorner = Instance.new("UICorner")
	fillCorner.CornerRadius = UDim.new(0, 4)
	fillCorner.Parent = barFill

	billboard.Parent = model

	-- ProximityPrompt pour cibler / engager le combat
	local prompt = Instance.new("ProximityPrompt")
	prompt.Name = "TargetPrompt"
	prompt.ActionText = "Combattre"
	prompt.ObjectText = dragonConfig.DisplayName .. " sauvage"
	prompt.HoldDuration = 0
	prompt.MaxActivationDistance = 18
	prompt.RequiresLineOfSight = false
	prompt.Parent = primary

	local wildData: WildDragon = {
		Id = tostring(math.random(100000, 999999)),
		SpeciesId = speciesId,
		DisplayName = dragonConfig.DisplayName,
		Element = dragonConfig.Element,
		Rarity = dragonConfig.Rarity,
		Stage = stage,
		Model = model,
		MaxHp = maxHp,
		CurrentHp = maxHp,
		SpawnOrigin = position,
		LastAttackTime = 0,
		HealthFill = barFill,
		IsDead = false,
	}

	wildDragons[model] = wildData

	prompt.Triggered:Connect(function(player)
		CombatService.setPlayerTarget(player, model)
	end)

	return wildData
end

--[[
	Définit la cible de combat active pour un joueur.
]]
function CombatService.setPlayerTarget(player: Player, targetModel: Model?)
	local state = playerStates[player]
	if not state then return end

	if targetModel and wildDragons[targetModel] and not wildDragons[targetModel].IsDead then
		state.TargetDragon = wildDragons[targetModel]
		print(string.format("[CombatService] %s a ciblé %s sauvage", player.Name, state.TargetDragon.DisplayName))
	else
		state.TargetDragon = nil
	end
end

selectTargetEvent.OnServerEvent:Connect(function(player, model)
	if model and model:IsA("Model") then
		CombatService.setPlayerTarget(player, model)
	end
end)

--[[
	Tue un dragon sauvage et distribue les récompenses.
]]
local function killWildDragon(wild: WildDragon, killer: Player)
	if wild.IsDead then return end
	wild.IsDead = true
	wildDragons[wild.Model] = nil

	local deathPos = wild.SpawnOrigin
	if wild.Model.PrimaryPart then
		deathPos = wild.Model.PrimaryPart.Position
	end
	wild.Model:Destroy()

	-- Distribution des récompenses au joueur victorieux
	local profile = DataService.getProfile(killer)
	if profile then
		-- 1. XP du joueur (+35 XP)
		DataService.addPlayerExp(killer, 35)

		-- 2. XP des dragons équipés (+45 XP chacun) avec test d'évolution
		if profile.EquippedDragons then
			for _, guid in ipairs(profile.EquippedDragons) do
				DataService.addDragonExp(killer, guid, 45)
			end
		end

		-- 3. Or gagné (base 25 or)
		DataService.addGold(killer, 25)

		-- 4. 12 % de chance pour 1 diamant
		if math.random() <= Economy.SpecialRates.DiamondChanceOnKill then
			DataService.addDiamonds(killer, 1)
			print(string.format("[CombatService] 💎 Diamant découvert par %s !", killer.Name))
		end

		-- 5. Chance d'œuf de combat (5 % à 15 %)
		local eggChance = math.random() * (Economy.SpecialRates.CombatEggMaxDropChance - Economy.SpecialRates.CombatEggMinDropChance) + Economy.SpecialRates.CombatEggMinDropChance
		if math.random() <= eggChance then
			-- Don d'un dragon sauvage commun ou rare
			local dropRarity = math.random() <= 0.8 and "Commun" or "Rare"
			local candidates = Dragons.getByRarityAndWorld(dropRarity, 1)
			if #candidates > 0 then
				local wonDragon = candidates[math.random(1, #candidates)]
				DataService.addDragon(killer, wonDragon.Id, "Bebe")
				print(string.format("[CombatService] 🥚 Œuf de combat obtenu par %s : %s (%s) !", killer.Name, wonDragon.DisplayName, dropRarity))
			end
		end
	end

	-- Réapparition programmée après 60 secondes
	task.delay(Combat.WildDragonRespawnSeconds, function()
		CombatService.spawnWildDragon(wild.SpeciesId, wild.SpawnOrigin)
	end)
end

--[[
	Applique des dégâts au joueur lors d'une riposte sauvage.
]]
local function damagePlayer(player: Player, damageAmount: number)
	local state = playerStates[player]
	if not state or state.IsProtected then return end

	state.LastCombatTime = os.clock()
	state.CurrentHp = math.max(0, state.CurrentHp - damageAmount)
	playerHealthSyncEvent:FireClient(player, state.CurrentHp, state.MaxHp)

	local char = player.Character
	local root = char and char:FindFirstChild("HumanoidRootPart") :: BasePart?
	if root then
		combatEffectEvent:FireAllClients(root.Position, math.round(damageAmount), false, "Feu")
	end

	-- Mort du joueur si PV <= 0
	if state.CurrentHp <= 0 then
		print(string.format("[CombatService] %s a été mis K.O. !", player.Name))
		state.IsProtected = true

		-- Perte de 5 % de l'or porté (plafonnée)
		local profile = DataService.getProfile(player)
		if profile and profile.Gold > 0 then
			local goldLost = math.min(math.floor(profile.Gold * Economy.DeathPenalty.GoldLossPercent), Economy.DeathPenalty.MaxGoldLoss)
			DataService.removeGold(player, goldLost)
		end

		-- Respawn au village
		if root then
			root.CFrame = CFrame.new(0, 4, 35)
		end

		state.CurrentHp = state.MaxHp
		playerHealthSyncEvent:FireClient(player, state.CurrentHp, state.MaxHp)

		-- Protection de 3 secondes
		task.delay(Economy.DeathPenalty.RespawnProtectionDuration, function()
			state.IsProtected = false
		end)
	end
end

-- =============================================================================
-- BOUCLE DE COMBAT EN TEMPS RÉEL (Attaques des pets & riposte sauvage)
-- =============================================================================
task.spawn(function()
	while true do
		task.wait(1.2) -- Cadence de frappe moyenne
		local now = os.clock()

		for player, state in pairs(playerStates) do
			local target = state.TargetDragon
			if target and not target.IsDead and target.Model.PrimaryPart then
				local char = player.Character
				local root = char and char:FindFirstChild("HumanoidRootPart") :: BasePart?

				if root then
					local distToTarget = (root.Position - target.Model.PrimaryPart.Position).Magnitude
					if distToTarget <= 35 then
						state.LastCombatTime = now
						local profile = DataService.getProfile(player)

						-- 1. Attaques de chacun des dragons équipés du joueur
						local totalDamageDealt = 0
						if profile and profile.EquippedDragons and profile.Dragons then
							for _, guid in ipairs(profile.EquippedDragons) do
								local dragonRec = profile.Dragons[guid]
								if dragonRec then
									local dragonCfg = Dragons.List[dragonRec.SpeciesId]
									if dragonCfg then
										local _, baseDmg = StatCalc.getDragonStats(dragonRec.SpeciesId, dragonRec.Stage, dragonRec.Level)
										local elementMult = StatCalc.getElementMultiplier(dragonCfg.Element, target.Element)
										local finalDmg = math.max(1, math.round(baseDmg * elementMult))
										totalDamageDealt += finalDmg
									end
								end
							end
						end

						-- Si le joueur n'a aucun dragon équipé, il frappe avec ses poings
						if totalDamageDealt == 0 then
							totalDamageDealt = Combat.getPlayerDamage(profile and profile.Level or 1)
						end

						-- Application des dégâts au dragon sauvage
						target.CurrentHp = math.max(0, target.CurrentHp - totalDamageDealt)
						if target.HealthFill then
							target.HealthFill.Size = UDim2.new(target.CurrentHp / target.MaxHp, 0, 1, 0)
						end

						combatEffectEvent:FireAllClients(target.Model.PrimaryPart.Position, totalDamageDealt, false, "Plante")

						if target.CurrentHp <= 0 then
							killWildDragon(target, player)
							state.TargetDragon = nil
						else
							-- 2. Riposte du dragon sauvage (3 % des PV max du joueur pour un bébé)
							local retaliationDmg = math.max(1, math.round(state.MaxHp * Combat.WildDamageToPlayerPercent.Bebe))
							damagePlayer(player, retaliationDmg)
						end
					else
						-- Trop éloigné de la cible
						state.TargetDragon = nil
					end
				end
			end
		end
	end
end)

-- =============================================================================
-- RÉGÉNÉRATION HORS COMBAT (2 % des PV max par seconde après 5 s)
-- =============================================================================
task.spawn(function()
	while true do
		task.wait(1.0)
		local now = os.clock()

		for player, state in pairs(playerStates) do
			if (now - state.LastCombatTime) >= Combat.Player.RegenOutOfCombatSeconds then
				if state.CurrentHp < state.MaxHp then
					local regenAmount = math.ceil(state.MaxHp * Combat.Player.RegenPercentPerSec)
					state.CurrentHp = math.min(state.MaxHp, state.CurrentHp + regenAmount)
					playerHealthSyncEvent:FireClient(player, state.CurrentHp, state.MaxHp)
				end
			end
		end
	end
end)

-- Apparition initiale d'une dizaine de bébés dragons sauvages dans le Monde 1
task.spawn(function()
	task.wait(2)
	local world1Dragons = { "Pousse", "Mottin", "Brindille", "Galet", "Trefle", "Bruyere", "Sillon" }
	local spawnPoints = {
		Vector3.new(-50, 0.5, -20),
		Vector3.new(-35, 0.5, 5),
		Vector3.new(-65, 0.5, 35),
		Vector3.new(-85, 0.5, -15),
		Vector3.new(45, 0.5, -25),
		Vector3.new(65, 0.5, 10),
		Vector3.new(85, 0.5, 30),
		Vector3.new(50, 0.5, -70),
		Vector3.new(-50, 0.5, -70),
		Vector3.new(0, 0.5, -85),
	}

	for i, pt in ipairs(spawnPoints) do
		local species = world1Dragons[((i - 1) % #world1Dragons) + 1]
		CombatService.spawnWildDragon(species, pt)
	end
	print(string.format("[CombatService] %d bébés dragons sauvages déployés dans le Monde 1.", #spawnPoints))
end)

Players.PlayerAdded:Connect(function(player)
	initPlayerCombat(player)
end)

Players.PlayerRemoving:Connect(function(player)
	playerStates[player] = nil
end)

return CombatService
