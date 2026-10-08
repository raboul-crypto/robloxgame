--!strict
-- BuildWorld1.server.lua
-- Génère par code le décor du Monde 1 (La Plaine des Aurores) :
-- Sol vert, point d'apparition, rivière en pièces bleues, arbres, village et mannequins de farm.

local Workspace = game:GetService("Workspace")

-- Nettoie l'ancien Monde 1 s'il existe déjà pour garantir une reconstruction complète
local existingWorld = Workspace:FindFirstChild("World1")
if existingWorld then
	existingWorld:Destroy()
end

print("[BuildWorld1] Génération du décor du Monde 1 (La Plaine des Aurores)...")

local worldFolder = Instance.new("Folder")
worldFolder.Name = "World1"
worldFolder.Parent = Workspace

-- =============================================================================
-- 1. SOL PRINCIPAL (Herbe verdoyante)
-- =============================================================================
local ground = Instance.new("Part")
ground.Name = "Ground"
ground.Size = Vector3.new(350, 4, 350)
ground.Position = Vector3.new(0, -2, 0)
ground.Color = Color3.fromRGB(90, 165, 70)
ground.Material = Enum.Material.Grass
ground.Anchored = true
ground.CanCollide = true
ground.Parent = worldFolder

-- =============================================================================
-- 2. VILLAGE DE DÉPART & SPAWN
-- =============================================================================
local villageFolder = Instance.new("Folder")
villageFolder.Name = "Village"
villageFolder.Parent = worldFolder

-- Point d'apparition du joueur
local spawnLocation = Instance.new("SpawnLocation")
spawnLocation.Name = "VillageSpawn"
spawnLocation.Size = Vector3.new(12, 0.6, 12)
spawnLocation.Position = Vector3.new(0, 0.3, 40)
spawnLocation.Color = Color3.fromRGB(220, 205, 175)
spawnLocation.Material = Enum.Material.Cobblestone
spawnLocation.Anchored = true
spawnLocation.CanCollide = true
spawnLocation.Neutral = true
spawnLocation.Duration = 0
spawnLocation.Parent = villageFolder

-- Petite maison décorative
local function createCottage(position: Vector3, rotationY: number)
	local houseModel = Instance.new("Model")
	houseModel.Name = "Cottage"

	-- Murs
	local walls = Instance.new("Part")
	walls.Name = "Walls"
	walls.Size = Vector3.new(14, 10, 14)
	walls.Position = position + Vector3.new(0, 5, 0)
	walls.Color = Color3.fromRGB(240, 230, 210)
	walls.Material = Enum.Material.Plaster
	walls.Anchored = true
	walls.Parent = houseModel

	-- Toit
	local roof = Instance.new("WedgePart")
	roof.Name = "Roof"
	roof.Size = Vector3.new(16, 6, 16)
	roof.Position = position + Vector3.new(0, 13, 0)
	roof.CFrame = CFrame.new(position + Vector3.new(0, 13, 0)) * CFrame.Angles(0, math.rad(rotationY), 0)
	roof.Color = Color3.fromRGB(160, 60, 40)
	roof.Material = Enum.Material.WoodPlanks
	roof.Anchored = true
	roof.Parent = houseModel

	-- Porte
	local door = Instance.new("Part")
	door.Name = "Door"
	door.Size = Vector3.new(3, 6, 0.4)
	door.Position = position + Vector3.new(0, 3, 7.1)
	door.Color = Color3.fromRGB(110, 75, 45)
	door.Material = Enum.Material.Wood
	door.Anchored = true
	door.Parent = houseModel

	houseModel.Parent = villageFolder
end

createCottage(Vector3.new(-30, 0, 45), 0)
createCottage(Vector3.new(30, 0, 45), 0)

-- =============================================================================
-- 3. RIVIÈRE (Eau claire stylisée)
-- =============================================================================
local riverFolder = Instance.new("Folder")
riverFolder.Name = "River"
riverFolder.Parent = worldFolder

local riverPoints = {
	{ Pos = Vector3.new(-140, 0.1, -10), Size = Vector3.new(80, 0.5, 20), Angle = 10 },
	{ Pos = Vector3.new(-70, 0.1, -5), Size = Vector3.new(80, 0.5, 22), Angle = 5 },
	{ Pos = Vector3.new(0, 0.1, 0), Size = Vector3.new(80, 0.5, 24), Angle = 0 },
	{ Pos = Vector3.new(70, 0.1, 5), Size = Vector3.new(80, 0.5, 22), Angle = -8 },
	{ Pos = Vector3.new(140, 0.1, 15), Size = Vector3.new(80, 0.5, 20), Angle = -12 },
}

for i, pt in ipairs(riverPoints) do
	local waterPart = Instance.new("Part")
	waterPart.Name = "WaterSegment_" .. i
	waterPart.Size = pt.Size
	waterPart.CFrame = CFrame.new(pt.Pos) * CFrame.Angles(0, math.rad(pt.Angle), 0)
	waterPart.Color = Color3.fromRGB(45, 145, 225)
	waterPart.Material = Enum.Material.Glass
	waterPart.Transparency = 0.35
	waterPart.Anchored = true
	waterPart.CanCollide = false
	waterPart.Parent = riverFolder
end

-- =============================================================================
-- 4. ARBRES DECORATIFS
-- =============================================================================
local treesFolder = Instance.new("Folder")
treesFolder.Name = "Trees"
treesFolder.Parent = worldFolder

local function createTree(position: Vector3, scale: number)
	local tree = Instance.new("Model")
	tree.Name = "Tree"

	-- Tronc
	local trunk = Instance.new("Part")
	trunk.Name = "Trunk"
	trunk.Size = Vector3.new(2 * scale, 8 * scale, 2 * scale)
	trunk.Position = position + Vector3.new(0, 4 * scale, 0)
	trunk.Color = Color3.fromRGB(115, 80, 50)
	trunk.Material = Enum.Material.Wood
	trunk.Anchored = true
	trunk.Parent = tree

	-- Feuillage (couronne supérieure)
	local foliage = Instance.new("Part")
	foliage.Name = "Foliage"
	foliage.Shape = Enum.PartType.Ball
	foliage.Size = Vector3.new(8 * scale, 8 * scale, 8 * scale)
	foliage.Position = position + Vector3.new(0, 9 * scale, 0)
	foliage.Color = Color3.fromRGB(60, 140, 50)
	foliage.Material = Enum.Material.Grass
	foliage.Anchored = true
	foliage.Parent = tree

	tree.Parent = treesFolder
end

local treePositions = {
	Vector3.new(-60, 0, 20),
	Vector3.new(-45, 0, 70),
	Vector3.new(50, 0, 70),
	Vector3.new(70, 0, 25),
	Vector3.new(-80, 0, -50),
	Vector3.new(80, 0, -45),
	Vector3.new(-25, 0, -80),
	Vector3.new(30, 0, -80),
}

for _, pos in ipairs(treePositions) do
	createTree(pos, 1.0 + math.random() * 0.4)
end

-- =============================================================================
-- 5. ZONE DE FARM AVEC LES 3 MANNEQUINS D'ENTRAÎNEMENT
-- =============================================================================
local farmFolder = Instance.new("Folder")
farmFolder.Name = "FarmZone"
farmFolder.Parent = worldFolder

-- Terrain de terre battue pour le farm
local arenaFloor = Instance.new("Part")
arenaFloor.Name = "ArenaFloor"
arenaFloor.Size = Vector3.new(70, 0.4, 40)
arenaFloor.Position = Vector3.new(0, 0.2, -40)
arenaFloor.Color = Color3.fromRGB(180, 150, 100)
arenaFloor.Material = Enum.Material.Ground
arenaFloor.Anchored = true
arenaFloor.Parent = farmFolder

local function createTrainingDummy(index: number, position: Vector3)
	local dummy = Instance.new("Model")
	dummy.Name = "TrainingDummy_" .. index
	dummy:SetAttribute("TargetType", "FarmDummy")
	dummy:SetAttribute("TargetId", "Dummy_" .. index)
	dummy:SetAttribute("WorldId", 1)

	-- Poteau support
	local pole = Instance.new("Part")
	pole.Name = "Pole"
	pole.Size = Vector3.new(0.8, 6, 0.8)
	pole.Position = position + Vector3.new(0, 3, 0)
	pole.Color = Color3.fromRGB(100, 70, 45)
	pole.Material = Enum.Material.Wood
	pole.Anchored = true
	pole.Parent = dummy

	-- Corps (sac de paille)
	local body = Instance.new("Part")
	body.Name = "Body"
	body.Size = Vector3.new(2.5, 3.5, 2)
	body.Position = position + Vector3.new(0, 3.8, 0)
	body.Color = Color3.fromRGB(215, 185, 120)
	body.Material = Enum.Material.Fabric
	body.Anchored = true
	body.Parent = dummy

	-- Tête (casque / paille)
	local head = Instance.new("Part")
	head.Name = "Head"
	head.Shape = Enum.PartType.Ball
	head.Size = Vector3.new(1.8, 1.8, 1.8)
	head.Position = position + Vector3.new(0, 6, 0)
	head.Color = Color3.fromRGB(190, 160, 100)
	head.Material = Enum.Material.Fabric
	head.Anchored = true
	head.Parent = dummy

	-- Bras horizontaux
	local arms = Instance.new("Part")
	arms.Name = "Arms"
	arms.Size = Vector3.new(4.5, 0.8, 0.8)
	arms.Position = position + Vector3.new(0, 4.5, 0)
	arms.Color = Color3.fromRGB(100, 70, 45)
	arms.Material = Enum.Material.Wood
	arms.Anchored = true
	arms.Parent = dummy

	dummy.PrimaryPart = body

	-- ProximityPrompt pour interaction (clavier E ou bouton mobile)
	local prompt = Instance.new("ProximityPrompt")
	prompt.Name = "HitPrompt"
	prompt.ActionText = "Frapper"
	prompt.ObjectText = "Mannequin d'entraînement"
	prompt.HoldDuration = 0
	prompt.MaxActivationDistance = 14
	prompt.RequiresLineOfSight = false
	prompt.Parent = body

	-- ClickDetector pour frapper au clic souris direct
	local clickDetector = Instance.new("ClickDetector")
	clickDetector.MaxActivationDistance = 14
	clickDetector.Parent = body

	-- Étiquette au-dessus du mannequin
	local billboard = Instance.new("BillboardGui")
	billboard.Name = "Tag"
	billboard.Size = UDim2.fromOffset(180, 45)
	billboard.StudsOffset = Vector3.new(0, 4, 0)
	billboard.AlwaysOnTop = true
	billboard.Adornee = head

	local title = Instance.new("TextLabel")
	title.Size = UDim2.fromScale(1, 0.6)
	title.BackgroundTransparency = 1
	title.Text = "Mannequin #" .. index
	title.TextColor3 = Color3.fromRGB(255, 255, 255)
	title.TextStrokeTransparency = 0.2
	title.TextScaled = true
	title.Font = Enum.Font.GothamBold
	title.Parent = billboard

	local subtitle = Instance.new("TextLabel")
	subtitle.Size = UDim2.fromScale(1, 0.4)
	subtitle.Position = UDim2.fromScale(0, 0.6)
	subtitle.BackgroundTransparency = 1
	subtitle.Text = "[Clic ou E pour récolter l'or]"
	subtitle.TextColor3 = Color3.fromRGB(255, 215, 0)
	subtitle.TextStrokeTransparency = 0.4
	subtitle.TextScaled = true
	subtitle.Font = Enum.Font.GothamMedium
	subtitle.Parent = billboard

	billboard.Parent = head
	dummy.Parent = farmFolder
end

-- Création des 3 mannequins espacés
createTrainingDummy(1, Vector3.new(-18, 0.2, -40))
createTrainingDummy(2, Vector3.new(0, 0.2, -40))
createTrainingDummy(3, Vector3.new(18, 0.2, -40))

-- =============================================================================
-- 6. STAND BOUTIQUE D'ŒUFS
-- =============================================================================
local shopFolder = Instance.new("Folder")
shopFolder.Name = "EggShop"
shopFolder.Parent = worldFolder

local function createEggShopStand(position: Vector3)
	local stand = Instance.new("Model")
	stand.Name = "CommonEggStand"

	-- Comptoir
	local counter = Instance.new("Part")
	counter.Name = "Counter"
	counter.Size = Vector3.new(8, 3.5, 4)
	counter.Position = position + Vector3.new(0, 1.75, 0)
	counter.Color = Color3.fromRGB(130, 90, 50)
	counter.Material = Enum.Material.WoodPlanks
	counter.Anchored = true
	counter.Parent = stand

	-- Toit / Auvent rayé
	local roof = Instance.new("Part")
	roof.Name = "Roof"
	roof.Size = Vector3.new(9, 0.8, 5)
	roof.Position = position + Vector3.new(0, 7, 0)
	roof.Color = Color3.fromRGB(220, 60, 60)
	roof.Material = Enum.Material.Fabric
	roof.Anchored = true
	roof.Parent = stand

	-- Piliers du toit
	local function createPillar(offset: Vector3)
		local pillar = Instance.new("Part")
		pillar.Name = "Pillar"
		pillar.Size = Vector3.new(0.6, 4, 0.6)
		pillar.Position = position + Vector3.new(0, 5, 0) + offset
		pillar.Color = Color3.fromRGB(100, 70, 40)
		pillar.Material = Enum.Material.Wood
		pillar.Anchored = true
		pillar.Parent = stand
	end
	createPillar(Vector3.new(-3.6, 0, -1.8))
	createPillar(Vector3.new(3.6, 0, -1.8))
	createPillar(Vector3.new(-3.6, 0, 1.8))
	createPillar(Vector3.new(3.6, 0, 1.8))

	-- Œuf géant décoratif sur le comptoir
	local eggPart = Instance.new("Part")
	eggPart.Name = "DecorativeEgg"
	eggPart.Shape = Enum.PartType.Ball
	eggPart.Size = Vector3.new(2.4, 3.2, 2.4)
	eggPart.Position = position + Vector3.new(0, 4.8, 0)
	eggPart.Color = Color3.fromRGB(255, 230, 120)
	eggPart.Material = Enum.Material.SmoothPlastic
	eggPart.Anchored = true
	eggPart.Parent = stand

	-- ProximityPrompt pour achat
	local prompt = Instance.new("ProximityPrompt")
	prompt.Name = "HatchPrompt"
	prompt.ActionText = "Faire éclore (100 🪙)"
	prompt.ObjectText = "Œuf Commun"
	prompt.HoldDuration = 0
	prompt.MaxActivationDistance = 14
	prompt.RequiresLineOfSight = false
	prompt.Parent = counter

	-- Enseigne
	local billboard = Instance.new("BillboardGui")
	billboard.Name = "ShopSign"
	billboard.Size = UDim2.fromOffset(200, 50)
	billboard.StudsOffset = Vector3.new(0, 3, 0)
	billboard.AlwaysOnTop = true
	billboard.Adornee = roof

	local signText = Instance.new("TextLabel")
	signText.Size = UDim2.fromScale(1, 0.6)
	signText.BackgroundTransparency = 1
	signText.Text = "🥚 NID D'ŒUFS"
	signText.TextColor3 = Color3.fromRGB(255, 255, 255)
	signText.TextStrokeTransparency = 0.2
	signText.TextScaled = true
	signText.Font = Enum.Font.GothamBlack
	signText.Parent = billboard

	local priceText = Instance.new("TextLabel")
	priceText.Size = UDim2.fromScale(1, 0.4)
	priceText.Position = UDim2.fromScale(0, 0.6)
	priceText.BackgroundTransparency = 1
	priceText.Text = "Prix : 100 Or"
	priceText.TextColor3 = Color3.fromRGB(255, 215, 0)
	priceText.TextStrokeTransparency = 0.3
	priceText.TextScaled = true
	priceText.Font = Enum.Font.GothamBold
	priceText.Parent = billboard

	billboard.Parent = roof
	stand.Parent = shopFolder

	-- Liaison de l'action d'achat avec HatchingService
	local ServerScriptService = game:GetService("ServerScriptService")
	task.spawn(function()
		local Services = ServerScriptService:WaitForChild("Services", 10)
		if Services then
			local HatchingService = require(Services:WaitForChild("HatchingService", 10)) :: any
			if HatchingService then
				prompt.Triggered:Connect(function(player)
					HatchingService.purchaseEgg(player, 1, "Common")
				end)
			end
		end
	end)
end

createEggShopStand(Vector3.new(22, 0, 18))

-- Stand des Œufs aux Diamants
local function createDiamondEggStand(position: Vector3)
	local stand = Instance.new("Model")
	stand.Name = "DiamondEggStand"

	local counter = Instance.new("Part")
	counter.Name = "Counter"
	counter.Size = Vector3.new(8, 3.5, 4)
	counter.Position = position + Vector3.new(0, 1.75, 0)
	counter.Color = Color3.fromRGB(30, 45, 65)
	counter.Material = Enum.Material.Cobblestone
	counter.Anchored = true
	counter.Parent = stand

	local roof = Instance.new("Part")
	roof.Name = "Roof"
	roof.Size = Vector3.new(9, 0.8, 5)
	roof.Position = position + Vector3.new(0, 7, 0)
	roof.Color = Color3.fromRGB(40, 180, 240)
	roof.Material = Enum.Material.Glass
	roof.Anchored = true
	roof.Parent = stand

	local eggPart = Instance.new("Part")
	eggPart.Name = "DecorativeEgg"
	eggPart.Shape = Enum.PartType.Ball
	eggPart.Size = Vector3.new(2.4, 3.2, 2.4)
	eggPart.Position = position + Vector3.new(0, 4.8, 0)
	eggPart.Color = Color3.fromRGB(80, 220, 255)
	eggPart.Material = Enum.Material.Glass
	eggPart.Anchored = true
	eggPart.Parent = stand

	local prompt = Instance.new("ProximityPrompt")
	prompt.Name = "DiamondHatchPrompt"
	prompt.ActionText = "Faire éclore (150 💎)"
	prompt.ObjectText = "Œuf aux Diamants"
	prompt.HoldDuration = 0
	prompt.MaxActivationDistance = 14
	prompt.RequiresLineOfSight = false
	prompt.Parent = counter

	local billboard = Instance.new("BillboardGui")
	billboard.Name = "ShopSign"
	billboard.Size = UDim2.fromOffset(200, 50)
	billboard.StudsOffset = Vector3.new(0, 3, 0)
	billboard.AlwaysOnTop = true
	billboard.Adornee = roof

	local signText = Instance.new("TextLabel")
	signText.Size = UDim2.fromScale(1, 0.6)
	signText.BackgroundTransparency = 1
	signText.Text = "💎 NID DE DIAMANTS"
	signText.TextColor3 = Color3.fromRGB(120, 230, 255)
	signText.TextStrokeTransparency = 0.2
	signText.TextScaled = true
	signText.Font = Enum.Font.GothamBlack
	signText.Parent = billboard

	local priceText = Instance.new("TextLabel")
	priceText.Size = UDim2.fromScale(1, 0.4)
	priceText.Position = UDim2.fromScale(0, 0.6)
	priceText.BackgroundTransparency = 1
	priceText.Text = "Prix : 150 Diamants"
	priceText.TextColor3 = Color3.fromRGB(80, 210, 255)
	priceText.TextStrokeTransparency = 0.3
	priceText.TextScaled = true
	priceText.Font = Enum.Font.GothamBold
	priceText.Parent = billboard

	billboard.Parent = roof
	stand.Parent = shopFolder

	local ServerScriptService = game:GetService("ServerScriptService")
	task.spawn(function()
		local Services = ServerScriptService:WaitForChild("Services", 10)
		if Services then
			local HatchingService = require(Services:WaitForChild("HatchingService", 10)) :: any
			if HatchingService then
				prompt.Triggered:Connect(function(player)
					HatchingService.purchaseEgg(player, 1, "Diamond")
				end)
			end
		end
	end)
end

createDiamondEggStand(Vector3.new(34, 0, 18))

-- =============================================================================
-- 7. ŒUFS CACHÉS DANS LE DÉCOR DU MONDE 1
-- =============================================================================
local hiddenEggsFolder = Instance.new("Folder")
hiddenEggsFolder.Name = "HiddenEggs"
hiddenEggsFolder.Parent = worldFolder

local hiddenEggSpots = {
	Vector3.new(28, 0.6, 2),    -- Près de la berge de la rivière
	Vector3.new(-75, 0.6, -45), -- Derrière un bosquet d'arbres
	Vector3.new(72, 0.6, 68),   -- À la lisière de la colline
	Vector3.new(-32, 0.6, 54),  -- Caché derrière un cottage
}

local function spawnHiddenEgg(spot: Vector3)
	local egg = Instance.new("Part")
	egg.Name = "HiddenEgg"
	egg.Shape = Enum.PartType.Ball
	egg.Size = Vector3.new(1.8, 2.4, 1.8)
	egg.Position = spot
	egg.Color = Color3.fromRGB(255, 230, 90)
	egg.Material = Enum.Material.Neon
	egg.Anchored = true
	egg.CanCollide = false
	egg.Parent = hiddenEggsFolder

	local prompt = Instance.new("ProximityPrompt")
	prompt.Name = "PickupPrompt"
	prompt.ActionText = "Ramasser"
	prompt.ObjectText = "Œuf Secret Découvert !"
	prompt.HoldDuration = 0
	prompt.MaxActivationDistance = 10
	prompt.RequiresLineOfSight = false
	prompt.Parent = egg

	prompt.Triggered:Connect(function(player)
		local ServerScriptService = game:GetService("ServerScriptService")
		local Services = ServerScriptService:WaitForChild("Services")
		local DataService = require(Services:WaitForChild("DataService")) :: any
		local Dragons = require(game:GetService("ReplicatedStorage"):WaitForChild("Shared"):WaitForChild("Config"):WaitForChild("Dragons")) :: any

		-- Tirage d'un dragon Commun ou Rare
		local dropRarity = math.random() <= 0.7 and "Commun" or "Rare"
		local candidates = Dragons.getByRarityAndWorld(dropRarity, 1)
		if #candidates > 0 then
			local foundDragon = candidates[math.random(1, #candidates)]
			DataService.addDragon(player, foundDragon.Id, "Bebe")
			print(string.format("[HiddenEgg] %s a trouvé l'œuf caché : %s (%s) !", player.Name, foundDragon.DisplayName, dropRarity))
		end

		egg:Destroy()

		-- Réapparition après 120 secondes
		task.delay(120, function()
			spawnHiddenEgg(spot)
		end)
	end)
end

for _, spot in ipairs(hiddenEggSpots) do
	spawnHiddenEgg(spot)
end

print("[BuildWorld1] Monde 1 généré avec succès !")
