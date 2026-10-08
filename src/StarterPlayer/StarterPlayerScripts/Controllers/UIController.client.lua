--!strict
-- UIController.client.lua
-- Contrôleur client de l'interface utilisateur complète :
-- 1. HUD supérieur (Or, Diamants, Niveau) avec mises à jour et pulsations temps réel.
-- 2. Écran d'animation d'éclosion d'œufs (tremblement de l'œuf, révélation 3D en ViewportFrame).
-- 3. Fenêtre d'Inventaire des Dragons (liste, aperçus 3D ViewportFrame, boutons Équiper/Déséquiper, puissance de farm totale).
-- 4. Textes flottants lors des frappes de farm.

local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local TweenService = game:GetService("TweenService")
local Debris = game:GetService("Debris")
local RunService = game:GetService("RunService")

local Shared = ReplicatedStorage:WaitForChild("Shared")
local Config = Shared:WaitForChild("Config")

local Rarities = require(Config:WaitForChild("Rarities")) :: any
local Dragons = require(Config:WaitForChild("Dragons")) :: any
local StatCalc = require(Shared:WaitForChild("StatCalc")) :: any
local DragonModels = require(Shared:WaitForChild("DragonModels")) :: any

local Network = require(Shared:WaitForChild("Network")) :: any

local player = Players.LocalPlayer
local playerGui = player:WaitForChild("PlayerGui")

-- =============================================================================
-- INTERFACE PRINCIPALE (ScreenGui - instanciée immédiatement)
-- =============================================================================
local screenGui = Instance.new("ScreenGui")
screenGui.Name = "MainHUD"
screenGui.ResetOnSpawn = false
screenGui.ZIndexBehavior = Enum.ZIndexBehavior.Sibling
screenGui.Parent = playerGui

-- Récupération sécurisée des RemoteEvents et RemoteFunctions via Network
local dataSyncEvent = Network.getEvent("DataSync")
local farmHitEffectEvent = Network.getEvent("FarmHitEffect")
local hatchResultEvent = Network.getEvent("HatchResult")
local combatEffectEvent = Network.getEvent("CombatDamageEffect")
local playerHealthSyncEvent = Network.getEvent("PlayerHealthSync")
local selectTargetEvent = Network.getEvent("SelectCombatTarget")

local equipPetFunction = Network.getFunction("EquipPet")
local unequipPetFunction = Network.getFunction("UnequipPet")
local captureFunction = Network.getFunction("AttemptCapture")

-- Fonction utilitaire pour formater les grands nombres
local function formatNumber(n: number): string
	if n >= 1000000000000 then
		return string.format("%.1fT", n / 1000000000000)
	elseif n >= 1000000000 then
		return string.format("%.1fB", n / 1000000000)
	elseif n >= 1000000 then
		return string.format("%.1fM", n / 1000000)
	elseif n >= 1000 then
		return string.format("%.1fK", n / 1000)
	else
		return tostring(math.floor(n))
	end
end

-- =============================================================================
-- 1. HUD SUPÉRIEUR (Or, Diamants, Niveau)
-- =============================================================================
local topContainer = Instance.new("Frame")
topContainer.Name = "TopContainer"
topContainer.Size = UDim2.new(0, 680, 0, 50)
topContainer.Position = UDim2.new(0.5, -340, 0, 15)
topContainer.BackgroundTransparency = 1
topContainer.Parent = screenGui

local uiLayout = Instance.new("UIListLayout")
uiLayout.FillDirection = Enum.FillDirection.Horizontal
uiLayout.HorizontalAlignment = Enum.HorizontalAlignment.Center
uiLayout.VerticalAlignment = Enum.VerticalAlignment.Center
uiLayout.Padding = UDim.new(0, 12)
uiLayout.Parent = topContainer

-- Créateur de carte de vie du joueur
local function createHealthCard()
	local card = Instance.new("Frame")
	card.Name = "HealthCard"
	card.Size = UDim2.new(0, 160, 0, 42)
	card.BackgroundColor3 = Color3.fromRGB(24, 26, 36)
	card.BorderSizePixel = 0

	local corner = Instance.new("UICorner")
	corner.CornerRadius = UDim.new(0, 10)
	corner.Parent = card

	local stroke = Instance.new("UIStroke")
	stroke.Color = Color3.fromRGB(255, 75, 75)
	stroke.Thickness = 1.8
	stroke.Transparency = 0.4
	stroke.Parent = card

	local icon = Instance.new("TextLabel")
	icon.Size = UDim2.new(0, 32, 1, 0)
	icon.Position = UDim2.new(0, 6, 0, 0)
	icon.BackgroundTransparency = 1
	icon.Text = "❤️"
	icon.TextSize = 20
	icon.Font = Enum.Font.GothamBold
	icon.Parent = card

	-- Conteneur barre de vie
	local barBg = Instance.new("Frame")
	barBg.Size = UDim2.new(1, -44, 0, 14)
	barBg.Position = UDim2.new(0, 38, 0, 8)
	barBg.BackgroundColor3 = Color3.fromRGB(45, 20, 25)
	barBg.BorderSizePixel = 0
	barBg.Parent = card

	local barCorner = Instance.new("UICorner")
	barCorner.CornerRadius = UDim.new(0, 4)
	barCorner.Parent = barBg

	local barFill = Instance.new("Frame")
	barFill.Name = "Fill"
	barFill.Size = UDim2.new(1, 0, 1, 0)
	barFill.BackgroundColor3 = Color3.fromRGB(80, 220, 100)
	barFill.BorderSizePixel = 0
	barFill.Parent = barBg

	local fillCorner = Instance.new("UICorner")
	fillCorner.CornerRadius = UDim.new(0, 4)
	fillCorner.Parent = barFill

	-- Texte PV (ex: 100 / 100)
	local hpLabel = Instance.new("TextLabel")
	hpLabel.Name = "HpLabel"
	hpLabel.Size = UDim2.new(1, -44, 0, 14)
	hpLabel.Position = UDim2.new(0, 38, 0, 24)
	hpLabel.BackgroundTransparency = 1
	hpLabel.Text = "100 / 100"
	hpLabel.TextColor3 = Color3.fromRGB(255, 220, 220)
	hpLabel.TextSize = 11
	hpLabel.Font = Enum.Font.GothamBold
	hpLabel.Parent = card

	card.Parent = topContainer
	return barFill, hpLabel
end

local function createStatCard(name: string, iconText: string, iconColor: Color3, defaultText: string)
	local card = Instance.new("Frame")
	card.Name = name .. "Card"
	card.Size = UDim2.new(0, 150, 0, 42)
	card.BackgroundColor3 = Color3.fromRGB(24, 26, 36)
	card.BorderSizePixel = 0

	local corner = Instance.new("UICorner")
	corner.CornerRadius = UDim.new(0, 10)
	corner.Parent = card

	local stroke = Instance.new("UIStroke")
	stroke.Color = iconColor
	stroke.Thickness = 1.8
	stroke.Transparency = 0.4
	stroke.Parent = card

	local icon = Instance.new("TextLabel")
	icon.Size = UDim2.new(0, 36, 1, 0)
	icon.Position = UDim2.new(0, 6, 0, 0)
	icon.BackgroundTransparency = 1
	icon.Text = iconText
	icon.TextColor3 = iconColor
	icon.TextSize = 22
	icon.Font = Enum.Font.GothamBold
	icon.Parent = card

	local valueLabel = Instance.new("TextLabel")
	valueLabel.Name = "ValueLabel"
	valueLabel.Size = UDim2.new(1, -48, 1, 0)
	valueLabel.Position = UDim2.new(0, 44, 0, 0)
	valueLabel.BackgroundTransparency = 1
	valueLabel.Text = defaultText
	valueLabel.TextColor3 = Color3.fromRGB(255, 255, 255)
	valueLabel.TextSize = 18
	valueLabel.Font = Enum.Font.GothamBold
	valueLabel.TextXAlignment = Enum.TextXAlignment.Left
	valueLabel.Parent = card

	card.Parent = topContainer
	return valueLabel
end

local healthFill, healthLabel = createHealthCard()
local goldLabel = createStatCard("Gold", "🪙", Color3.fromRGB(255, 215, 0), "0")
local diamondLabel = createStatCard("Diamond", "💎", Color3.fromRGB(80, 210, 255), "0")
local levelLabel = createStatCard("Level", "⭐", Color3.fromRGB(160, 90, 255), "Niv. 1")

local function popAnimation(label: TextLabel)
	local originalSize = label.TextSize
	local tweenGrow = TweenService:Create(label, TweenInfo.new(0.08, Enum.EasingStyle.Quad, Enum.EasingDirection.Out), {
		TextSize = originalSize + 4,
	})
	local tweenShrink = TweenService:Create(label, TweenInfo.new(0.12, Enum.EasingStyle.Quad, Enum.EasingDirection.In), {
		TextSize = originalSize,
	})
	tweenGrow:Play()
	tweenGrow.Completed:Connect(function()
		tweenShrink:Play()
	end)
end

-- =============================================================================
-- 2. BOUTON D'OUVERTURE DE L'INVENTAIRE
-- =============================================================================
local invButton = Instance.new("TextButton")
invButton.Name = "InventoryButton"
invButton.Size = UDim2.new(0, 130, 0, 42)
invButton.Position = UDim2.new(0, 20, 0.5, -21)
invButton.BackgroundColor3 = Color3.fromRGB(30, 34, 48)
invButton.Text = "🎒 Dragons (0)"
invButton.TextColor3 = Color3.fromRGB(255, 255, 255)
invButton.TextSize = 15
invButton.Font = Enum.Font.GothamBold
invButton.Parent = screenGui

local invCorner = Instance.new("UICorner")
invCorner.CornerRadius = UDim.new(0, 10)
invCorner.Parent = invButton

local invStroke = Instance.new("UIStroke")
invStroke.Color = Color3.fromRGB(100, 140, 255)
invStroke.Thickness = 1.8
invStroke.Parent = invButton

-- =============================================================================
-- 3. FENÊTRE DE L'INVENTAIRE DES DRAGONS
-- =============================================================================
local invModal = Instance.new("Frame")
invModal.Name = "InventoryModal"
invModal.Size = UDim2.new(0, 560, 0, 420)
invModal.Position = UDim2.new(0.5, -280, 0.5, -210)
invModal.BackgroundColor3 = Color3.fromRGB(20, 22, 32)
invModal.BorderSizePixel = 0
invModal.Visible = false
invModal.ZIndex = 20
invModal.Parent = screenGui

local modalCorner = Instance.new("UICorner")
modalCorner.CornerRadius = UDim.new(0, 14)
modalCorner.Parent = invModal

local modalStroke = Instance.new("UIStroke")
modalStroke.Color = Color3.fromRGB(80, 110, 200)
modalStroke.Thickness = 2
modalStroke.Parent = invModal

-- En-tête de l'inventaire
local headerTitle = Instance.new("TextLabel")
headerTitle.Size = UDim2.new(1, -60, 0, 45)
headerTitle.Position = UDim2.new(0, 20, 0, 0)
headerTitle.BackgroundTransparency = 1
headerTitle.Text = "MES DRAGONS"
headerTitle.TextColor3 = Color3.fromRGB(255, 255, 255)
headerTitle.TextSize = 20
headerTitle.Font = Enum.Font.GothamBlack
headerTitle.TextXAlignment = Enum.TextXAlignment.Left
headerTitle.ZIndex = 21
headerTitle.Parent = invModal

-- Bouton Fermer (X)
local closeButton = Instance.new("TextButton")
closeButton.Size = UDim2.new(0, 32, 0, 32)
closeButton.Position = UDim2.new(1, -42, 0, 8)
closeButton.BackgroundColor3 = Color3.fromRGB(220, 60, 60)
closeButton.Text = "✕"
closeButton.TextColor3 = Color3.fromRGB(255, 255, 255)
closeButton.TextSize = 16
closeButton.Font = Enum.Font.GothamBold
closeButton.ZIndex = 22
closeButton.Parent = invModal

local closeCorner = Instance.new("UICorner")
closeCorner.CornerRadius = UDim.new(0, 8)
closeCorner.Parent = closeButton

-- Barre d'état (Slots équipés & Puissance totale de farm)
local statsBar = Instance.new("Frame")
statsBar.Size = UDim2.new(1, -40, 0, 30)
statsBar.Position = UDim2.new(0, 20, 0, 48)
statsBar.BackgroundTransparency = 1
statsBar.ZIndex = 21
statsBar.Parent = invModal

local slotsText = Instance.new("TextLabel")
slotsText.Size = UDim2.new(0.5, 0, 1, 0)
slotsText.BackgroundTransparency = 1
slotsText.Text = "Équipés : 0 / 3"
slotsText.TextColor3 = Color3.fromRGB(180, 210, 255)
slotsText.TextSize = 14
slotsText.Font = Enum.Font.GothamMedium
slotsText.TextXAlignment = Enum.TextXAlignment.Left
slotsText.ZIndex = 21
slotsText.Parent = statsBar

local farmBonusText = Instance.new("TextLabel")
farmBonusText.Size = UDim2.new(0.5, 0, 1, 0)
farmBonusText.Position = UDim2.new(0.5, 0, 0, 0)
farmBonusText.BackgroundTransparency = 1
farmBonusText.Text = "Bonus Farm : +0%"
farmBonusText.TextColor3 = Color3.fromRGB(255, 215, 0)
farmBonusText.TextSize = 14
farmBonusText.Font = Enum.Font.GothamBold
farmBonusText.TextXAlignment = Enum.TextXAlignment.Right
farmBonusText.ZIndex = 21
farmBonusText.Parent = statsBar

-- Conteneur à défilement des cartes de dragons
local scrollingFrame = Instance.new("ScrollingFrame")
scrollingFrame.Size = UDim2.new(1, -40, 1, -95)
scrollingFrame.Position = UDim2.new(0, 20, 0, 85)
scrollingFrame.BackgroundTransparency = 1
scrollingFrame.BorderSizePixel = 0
scrollingFrame.ScrollBarThickness = 6
scrollingFrame.ZIndex = 21
scrollingFrame.Parent = invModal

local gridLayout = Instance.new("UIGridLayout")
gridLayout.CellSize = UDim2.new(0, 160, 0, 190)
gridLayout.CellPadding = UDim2.new(0, 15, 0, 15)
gridLayout.SortOrder = Enum.SortOrder.LayoutOrder
gridLayout.Parent = scrollingFrame

-- =============================================================================
-- GESTION DES DONNÉES LOCALES & RECONSTRUCTION DE L'INVENTAIRE
-- =============================================================================
local localDragons: { [string]: any } = {}
local localEquipped: { string } = {}

local function isEquipped(guid: string): boolean
	for _, id in ipairs(localEquipped) do
		if id == guid then
			return true
		end
	end
	return false
end

-- Création d'une caméra 3D dans un ViewportFrame pour afficher un dragon
local function setupViewportPreview(viewport: ViewportFrame, model: Model)
	viewport.CurrentCamera = nil
	local camera = Instance.new("Camera")
	viewport.CurrentCamera = camera
	camera.Parent = viewport

	model.Parent = viewport
	local primary = model.PrimaryPart or model:FindFirstChildWhichIsA("BasePart")
	if primary then
		camera.CFrame = CFrame.new(primary.Position + Vector3.new(0, 1.2, -4.5), primary.Position)
	end
end

local function refreshInventoryUI()
	-- Nettoyage des anciennes cartes
	for _, child in ipairs(scrollingFrame:GetChildren()) do
		if child:IsA("Frame") then
			child:Destroy()
		end
	end

	local count = 0
	local totalPower = 0

	for guid, dragonRecord in pairs(localDragons) do
		count += 1
		local dragonConfig = Dragons.List[dragonRecord.SpeciesId]
		local rarityConfig = dragonConfig and Rarities.List[dragonConfig.Rarity]
		local rarityColor = rarityConfig and rarityConfig.Color or Color3.fromRGB(200, 200, 200)

		local equipped = isEquipped(guid)
		if equipped and dragonConfig then
			local pwr = StatCalc.getFarmPower(dragonConfig.Rarity, dragonRecord.Stage)
			totalPower += pwr
		end

		-- Carte du dragon
		local card = Instance.new("Frame")
		card.Name = "Card_" .. guid
		card.BackgroundColor3 = Color3.fromRGB(28, 30, 42)
		card.BorderSizePixel = 0
		card.ZIndex = 22

		local cardCorner = Instance.new("UICorner")
		cardCorner.CornerRadius = UDim.new(0, 10)
		cardCorner.Parent = card

		local cardStroke = Instance.new("UIStroke")
		cardStroke.Color = equipped and Color3.fromRGB(80, 220, 100) or rarityColor
		cardStroke.Thickness = equipped and 2.5 or 1.5
		cardStroke.Parent = card

		-- Aperçu 3D ViewportFrame
		local viewport = Instance.new("ViewportFrame")
		viewport.Size = UDim2.new(1, -12, 0, 90)
		viewport.Position = UDim2.new(0, 6, 0, 6)
		viewport.BackgroundTransparency = 1
		viewport.ZIndex = 23
		viewport.Parent = card

		task.spawn(function()
			local previewModel = DragonModels.getModel(dragonRecord.SpeciesId, dragonRecord.Stage)
			setupViewportPreview(viewport, previewModel)
		end)

		-- Nom du dragon
		local nameLabel = Instance.new("TextLabel")
		nameLabel.Size = UDim2.new(1, -10, 0, 18)
		nameLabel.Position = UDim2.new(0, 5, 0, 100)
		nameLabel.BackgroundTransparency = 1
		nameLabel.Text = dragonConfig and dragonConfig.DisplayName or dragonRecord.SpeciesId
		nameLabel.TextColor3 = Color3.fromRGB(255, 255, 255)
		nameLabel.TextSize = 13
		nameLabel.Font = Enum.Font.GothamBold
		nameLabel.ZIndex = 23
		nameLabel.Parent = card

		-- Rareté & Stade
		local rarityLabel = Instance.new("TextLabel")
		rarityLabel.Size = UDim2.new(1, -10, 0, 16)
		rarityLabel.Position = UDim2.new(0, 5, 0, 120)
		rarityLabel.BackgroundTransparency = 1
		rarityLabel.Text = string.format("%s • %s", dragonConfig and dragonConfig.Rarity or "Commun", dragonRecord.Stage or "Bébé")
		rarityLabel.TextColor3 = rarityColor
		rarityLabel.TextSize = 11
		rarityLabel.Font = Enum.Font.GothamMedium
		rarityLabel.ZIndex = 23
		rarityLabel.Parent = card

		-- Bonus de farm individuel
		local powerVal = dragonConfig and StatCalc.getFarmPower(dragonConfig.Rarity, dragonRecord.Stage) or 0.1
		local bonusLabel = Instance.new("TextLabel")
		bonusLabel.Size = UDim2.new(1, -10, 0, 14)
		bonusLabel.Position = UDim2.new(0, 5, 0, 138)
		bonusLabel.BackgroundTransparency = 1
		bonusLabel.Text = string.format("Gain : +%.0f%% Or", powerVal * 100)
		bonusLabel.TextColor3 = Color3.fromRGB(255, 215, 0)
		bonusLabel.TextSize = 11
		bonusLabel.Font = Enum.Font.GothamMedium
		bonusLabel.ZIndex = 23
		bonusLabel.Parent = card

		-- Bouton Équiper / Déséquiper
		local actionBtn = Instance.new("TextButton")
		actionBtn.Size = UDim2.new(1, -16, 0, 26)
		actionBtn.Position = UDim2.new(0, 8, 1, -32)
		actionBtn.BackgroundColor3 = equipped and Color3.fromRGB(200, 60, 60) or Color3.fromRGB(45, 130, 230)
		actionBtn.Text = equipped and "Déséquiper" or "Équiper"
		actionBtn.TextColor3 = Color3.fromRGB(255, 255, 255)
		actionBtn.TextSize = 12
		actionBtn.Font = Enum.Font.GothamBold
		actionBtn.ZIndex = 24
		actionBtn.Parent = card

		local btnCorner = Instance.new("UICorner")
		btnCorner.CornerRadius = UDim.new(0, 6)
		btnCorner.Parent = actionBtn

		actionBtn.MouseButton1Click:Connect(function()
			if equipped then
				unequipPetFunction:InvokeServer(guid)
			else
				equipPetFunction:InvokeServer(guid)
			end
		end)

		card.Parent = scrollingFrame
	end

	-- Mise à jour des compteurs
	invButton.Text = string.format("🎒 Dragons (%d)", count)
	slotsText.Text = string.format("Équipés : %d / 3", #localEquipped)
	farmBonusText.Text = string.format("Bonus Farm : +%.0f%% Or", totalPower * 100)

	-- Ajustement de la taille de défilement
	local rows = math.ceil(count / 3)
	scrollingFrame.CanvasSize = UDim2.new(0, 0, 0, rows * 205)
end

invButton.MouseButton1Click:Connect(function()
	invModal.Visible = not invModal.Visible
	if invModal.Visible then
		refreshInventoryUI()
	end
end)

closeButton.MouseButton1Click:Connect(function()
	invModal.Visible = false
end)

-- =============================================================================
-- 4. ÉCRAN D'ANIMATION D'ÉCLOSION D'ŒUF (Hatch Screen)
-- =============================================================================
local hatchModal = Instance.new("Frame")
hatchModal.Name = "HatchModal"
hatchModal.Size = UDim2.fromScale(1, 1)
hatchModal.BackgroundColor3 = Color3.fromRGB(10, 12, 18)
hatchModal.BackgroundTransparency = 0.35
hatchModal.Visible = false
hatchModal.ZIndex = 50
hatchModal.Parent = screenGui

local hatchCard = Instance.new("Frame")
hatchCard.Name = "HatchCard"
hatchCard.Size = UDim2.new(0, 420, 0, 460)
hatchCard.Position = UDim2.new(0.5, -210, 0.5, -230)
hatchCard.BackgroundColor3 = Color3.fromRGB(24, 26, 38)
hatchCard.BorderSizePixel = 0
hatchCard.ZIndex = 51
hatchCard.Parent = hatchModal

local hatchCardCorner = Instance.new("UICorner")
hatchCardCorner.CornerRadius = UDim.new(0, 16)
hatchCardCorner.Parent = hatchCard

local hatchCardStroke = Instance.new("UIStroke")
hatchCardStroke.Color = Color3.fromRGB(255, 215, 0)
hatchCardStroke.Thickness = 2.5
hatchCardStroke.Parent = hatchCard

-- Icône œuf animé
local eggIcon = Instance.new("TextLabel")
eggIcon.Name = "EggIcon"
eggIcon.Size = UDim2.new(0, 100, 0, 100)
eggIcon.Position = UDim2.new(0.5, -50, 0, 50)
eggIcon.BackgroundTransparency = 1
eggIcon.Text = "🥚"
eggIcon.TextSize = 75
eggIcon.ZIndex = 52
eggIcon.Parent = hatchCard

-- ViewportFrame pour la révélation du dragon
local hatchViewport = Instance.new("ViewportFrame")
hatchViewport.Name = "HatchViewport"
hatchViewport.Size = UDim2.new(0, 260, 0, 200)
hatchViewport.Position = UDim2.new(0.5, -130, 0, 30)
hatchViewport.BackgroundTransparency = 1
hatchViewport.Visible = false
hatchViewport.ZIndex = 53
hatchViewport.Parent = hatchCard

local hatchTitle = Instance.new("TextLabel")
hatchTitle.Name = "HatchTitle"
hatchTitle.Size = UDim2.new(1, -20, 0, 35)
hatchTitle.Position = UDim2.new(0, 10, 0, 240)
hatchTitle.BackgroundTransparency = 1
hatchTitle.Text = "Éclosion en cours..."
hatchTitle.TextColor3 = Color3.fromRGB(255, 255, 255)
hatchTitle.TextSize = 24
hatchTitle.Font = Enum.Font.GothamBlack
hatchTitle.ZIndex = 52
hatchTitle.Parent = hatchCard

local hatchSubtitle = Instance.new("TextLabel")
hatchSubtitle.Name = "HatchSubtitle"
hatchSubtitle.Size = UDim2.new(1, -20, 0, 25)
hatchSubtitle.Position = UDim2.new(0, 10, 0, 280)
hatchSubtitle.BackgroundTransparency = 1
hatchSubtitle.Text = ""
hatchSubtitle.TextColor3 = Color3.fromRGB(255, 215, 0)
hatchSubtitle.TextSize = 16
hatchSubtitle.Font = Enum.Font.GothamBold
hatchSubtitle.ZIndex = 52
hatchSubtitle.Parent = hatchCard

local diamondBonusLabel = Instance.new("TextLabel")
diamondBonusLabel.Name = "DiamondBonusLabel"
diamondBonusLabel.Size = UDim2.new(1, -20, 0, 22)
diamondBonusLabel.Position = UDim2.new(0, 10, 0, 310)
diamondBonusLabel.BackgroundTransparency = 1
diamondBonusLabel.Text = "+1 💎 Diamant découvert !"
diamondBonusLabel.TextColor3 = Color3.fromRGB(80, 220, 255)
diamondBonusLabel.TextSize = 15
diamondBonusLabel.Font = Enum.Font.GothamBold
diamondBonusLabel.Visible = false
diamondBonusLabel.ZIndex = 52
diamondBonusLabel.Parent = hatchCard

local continueBtn = Instance.new("TextButton")
continueBtn.Name = "ContinueButton"
continueBtn.Size = UDim2.new(0, 180, 0, 42)
continueBtn.Position = UDim2.new(0.5, -90, 1, -60)
continueBtn.BackgroundColor3 = Color3.fromRGB(45, 140, 230)
continueBtn.Text = "Super !"
continueBtn.TextColor3 = Color3.fromRGB(255, 255, 255)
continueBtn.TextSize = 16
continueBtn.Font = Enum.Font.GothamBold
continueBtn.Visible = false
continueBtn.ZIndex = 54
continueBtn.Parent = hatchCard

local continueCorner = Instance.new("UICorner")
continueCorner.CornerRadius = UDim.new(0, 10)
continueCorner.Parent = continueBtn

continueBtn.MouseButton1Click:Connect(function()
	hatchModal.Visible = false
	refreshInventoryUI()
end)

-- Animation d'éclosion
hatchResultEvent.OnClientEvent:Connect(function(dragonData)
	if not dragonData then return end

	hatchModal.Visible = true
	eggIcon.Visible = true
	hatchViewport.Visible = false
	continueBtn.Visible = false
	diamondBonusLabel.Visible = false

	hatchTitle.Text = "Éclosion en cours..."
	hatchSubtitle.Text = ""

	-- 1. Animation de tremblement de l'œuf
	local originalPos = UDim2.new(0.5, -50, 0, 50)
	for i = 1, 8 do
		local shakeOffset = (i % 2 == 0 and 15 or -15)
		eggIcon.Position = UDim2.new(0.5, -50 + shakeOffset, 0, 50)
		task.wait(0.08)
	end
	eggIcon.Position = originalPos
	task.wait(0.15)

	-- 2. Révélation du dragon
	eggIcon.Visible = false
	hatchViewport.Visible = true

	local previewModel = DragonModels.getModel(dragonData.DragonId, dragonData.Stage or "Bebe")
	setupViewportPreview(hatchViewport, previewModel)

	local rarityInfo = Rarities.List[dragonData.Rarity]
	local rarityColor = rarityInfo and rarityInfo.Color or Color3.fromRGB(255, 255, 255)

	hatchCardStroke.Color = rarityColor
	hatchTitle.Text = dragonData.DisplayName
	hatchSubtitle.Text = string.format("%s • Élément %s", dragonData.Rarity, dragonData.Element)
	hatchSubtitle.TextColor3 = rarityColor

	if dragonData.DiamondAwarded then
		diamondBonusLabel.Visible = true
	end

	continueBtn.Visible = true
	refreshInventoryUI()
end)

-- =============================================================================
-- SYNCHRONISATION DES DONNÉES EN TEMPS RÉEL
-- =============================================================================
local currentGold = 0
local currentDiamonds = 0
local currentLevel = 1

dataSyncEvent.OnClientEvent:Connect(function(data)
	if not data then return end

	if data.Gold ~= nil then
		if data.Gold > currentGold then
			popAnimation(goldLabel)
		end
		currentGold = data.Gold
		goldLabel.Text = formatNumber(currentGold)
	end

	if data.Diamonds ~= nil then
		if data.Diamonds > currentDiamonds then
			popAnimation(diamondLabel)
		end
		currentDiamonds = data.Diamonds
		diamondLabel.Text = formatNumber(currentDiamonds)
	end

	if data.Level ~= nil then
		currentLevel = data.Level
		levelLabel.Text = "Niv. " .. tostring(currentLevel)
	end

	if data.Dragons then
		localDragons = data.Dragons
	end

	if data.EquippedDragons then
		localEquipped = data.EquippedDragons
	end

	refreshInventoryUI()
end)

-- =============================================================================
-- EFFET VISUEL DE GAIN D'OR FLOTTANT LORS D'UNE FRAPPE
-- =============================================================================
farmHitEffectEvent.OnClientEvent:Connect(function(position: Vector3, goldEarned: number)
	local part = Instance.new("Part")
	part.Size = Vector3.new(0.1, 0.1, 0.1)
	part.Position = position + Vector3.new(math.random(-10, 10) * 0.1, 3 + math.random(0, 10) * 0.1, math.random(-10, 10) * 0.1)
	part.Transparency = 1
	part.Anchored = true
	part.CanCollide = false
	part.Parent = workspace

	local billboard = Instance.new("BillboardGui")
	billboard.Size = UDim2.fromOffset(130, 40)
	billboard.AlwaysOnTop = true
	billboard.Adornee = part

	local text = Instance.new("TextLabel")
	text.Size = UDim2.fromScale(1, 1)
	text.BackgroundTransparency = 1
	text.Text = "+" .. formatNumber(goldEarned) .. " 🪙"
	text.TextColor3 = Color3.fromRGB(255, 230, 80)
	text.TextStrokeColor3 = Color3.fromRGB(100, 70, 0)
	text.TextStrokeTransparency = 0.1
	text.Font = Enum.Font.GothamBlack
	text.TextScaled = true
	text.Parent = billboard

	billboard.Parent = part

	local tweenElevate = TweenService:Create(part, TweenInfo.new(0.8, Enum.EasingStyle.Quad, Enum.EasingDirection.Out), {
		Position = part.Position + Vector3.new(0, 3.5, 0),
	})
	local tweenFade = TweenService:Create(text, TweenInfo.new(0.8, Enum.EasingStyle.Quad, Enum.EasingDirection.In), {
		TextTransparency = 1,
		TextStrokeTransparency = 1,
	})

	tweenElevate:Play()
	tweenFade:Play()

	Debris:AddItem(part, 0.85)
end)

-- =============================================================================
-- SYNCHRONISATION DE LA SANTÉ DU JOUEUR
-- =============================================================================
playerHealthSyncEvent.OnClientEvent:Connect(function(currentHp: number, maxHp: number)
	if healthFill and healthLabel then
		local ratio = math.clamp(currentHp / maxHp, 0, 1)
		TweenService:Create(healthFill, TweenInfo.new(0.2, Enum.EasingStyle.Quad, Enum.EasingDirection.Out), {
			Size = UDim2.new(ratio, 0, 1, 0),
		}):Play()

		-- Changement de couleur selon la santé (vert -> orange -> rouge)
		if ratio <= 0.25 then
			healthFill.BackgroundColor3 = Color3.fromRGB(240, 50, 50)
		elseif ratio <= 0.5 then
			healthFill.BackgroundColor3 = Color3.fromRGB(240, 180, 50)
		else
			healthFill.BackgroundColor3 = Color3.fromRGB(80, 220, 100)
		end

		healthLabel.Text = string.format("%d / %d", math.round(currentHp), math.round(maxHp))
	end
end)

-- =============================================================================
-- EFFET VISUEL DE DÉGÂTS FLOTTANTS EN COMBAT
-- =============================================================================
combatEffectEvent.OnClientEvent:Connect(function(position: Vector3, damage: number, isCrit: boolean, element: string)
	local part = Instance.new("Part")
	part.Size = Vector3.new(0.1, 0.1, 0.1)
	part.Position = position + Vector3.new(math.random(-15, 15) * 0.1, 2.5 + math.random(0, 10) * 0.1, math.random(-15, 15) * 0.1)
	part.Transparency = 1
	part.Anchored = true
	part.CanCollide = false
	part.Parent = workspace

	local billboard = Instance.new("BillboardGui")
	billboard.Size = UDim2.fromOffset(100, 35)
	billboard.AlwaysOnTop = true
	billboard.Adornee = part

	local text = Instance.new("TextLabel")
	text.Size = UDim2.fromScale(1, 1)
	text.BackgroundTransparency = 1
	text.Text = tostring(math.round(damage))
	text.TextColor3 = isCrit and Color3.fromRGB(255, 60, 60) or Color3.fromRGB(255, 150, 50)
	text.TextStrokeColor3 = Color3.fromRGB(60, 10, 10)
	text.TextStrokeTransparency = 0.1
	text.Font = Enum.Font.GothamBlack
	text.TextScaled = true
	text.Parent = billboard

	billboard.Parent = part

	local tweenElevate = TweenService:Create(part, TweenInfo.new(0.7, Enum.EasingStyle.Back, Enum.EasingDirection.Out), {
		Position = part.Position + Vector3.new(0, 2.8, 0),
	})
	local tweenFade = TweenService:Create(text, TweenInfo.new(0.7, Enum.EasingStyle.Quad, Enum.EasingDirection.In), {
		TextTransparency = 1,
		TextStrokeTransparency = 1,
	})

	tweenElevate:Play()
	tweenFade:Play()

	Debris:AddItem(part, 0.75)
end)

-- =============================================================================
-- BOUTON D'APPRIVOISEMENT (Capture d'un dragon sauvage affaibli sous 30 % PV)
-- =============================================================================
local captureBtn = Instance.new("TextButton")
captureBtn.Name = "CaptureButton"
captureBtn.Size = UDim2.new(0, 180, 0, 46)
captureBtn.Position = UDim2.new(0.5, -90, 1, -80)
captureBtn.BackgroundColor3 = Color3.fromRGB(40, 160, 90)
captureBtn.Text = "🎣 Apprivoiser (Appât)"
captureBtn.TextColor3 = Color3.fromRGB(255, 255, 255)
captureBtn.TextSize = 16
captureBtn.Font = Enum.Font.GothamBlack
captureBtn.Visible = false
captureBtn.ZIndex = 30
captureBtn.Parent = screenGui

local captureCorner = Instance.new("UICorner")
captureCorner.CornerRadius = UDim.new(0, 12)
captureCorner.Parent = captureBtn

local captureStroke = Instance.new("UIStroke")
captureStroke.Color = Color3.fromRGB(120, 255, 160)
captureStroke.Thickness = 2
captureStroke.Parent = captureBtn

local currentNearbyWild: Model? = nil

-- Détection de proximité d'un dragon sauvage sous 30 % de PV
task.spawn(function()
	while true do
		task.wait(0.3)
		local char = player.Character
		local root = char and char:FindFirstChild("HumanoidRootPart") :: BasePart?
		local foundLowHpWild: Model? = nil

		if root then
			local wildFolder = workspace:FindFirstChild("WildDragons")
			if wildFolder then
				for _, wildModel in ipairs(wildFolder:GetChildren()) do
					if wildModel:IsA("Model") and wildModel.PrimaryPart then
						local dist = (root.Position - wildModel.PrimaryPart.Position).Magnitude
						if dist <= 20 then
							local billboard = wildModel:FindFirstChild("WildHealthBar")
							local barBg = billboard and billboard:FindFirstChild("Frame")
							local barFill = barBg and barBg:FindFirstChild("Fill") :: Frame?
							if barFill and barFill.Size.X.Scale <= 0.30 then
								foundLowHpWild = wildModel
								break
							end
						end
					end
				end
			end
		end

		currentNearbyWild = foundLowHpWild
		captureBtn.Visible = (currentNearbyWild ~= nil)
	end
end)

captureBtn.MouseButton1Click:Connect(function()
	if currentNearbyWild then
		local success, dragonRec, msg = captureFunction:InvokeServer(currentNearbyWild, 0)
		if success then
			captureBtn.Visible = false
			print("[UIController] Capture réussie !")
		end
	end
end)

print("[UIController] HUD, Inventaire, Combat et Capture initialisés avec succès.")
