--!strict
--[[
	DragonModelBuilder
	Construit un dragon de TEST à partir de pièces Roblox (aucun asset externe).
	Sert de modèle provisoire jusqu'à ce que de vrais modèles 3D existent.

	Utilisation :
		local Builder = require(ReplicatedStorage.Shared.DragonModelBuilder)
		local dragon = Builder.build({
			Name = "Braisillon",
			Element = "Feu",        -- Feu, Eau, Plante, Terre, Vol, Tenebres, Mineral
			Rarity = "Commun",      -- Commun, Rare, Epique, Legendaire, Mythique, Secret, Mythe, Exclusif
			Stage = "Adulte",       -- Bebe, Jeune, Adulte
			Archetype = "Rapide",   -- Equilibre, Rapide, Tank, Brute
		})
		dragon.Parent = workspace
		dragon:PivotTo(CFrame.new(0, 5, 0))

	Le dragon regarde vers -Z (devant du modèle). Le PrimaryPart est "Body".
	Toutes les pièces sont soudées (WeldConstraint), non ancrées, sans collision.
]]

local Builder = {}

export type DragonConfig = {
	Name: string?,
	Element: string?,
	Rarity: string?,
	Stage: string?,
	Archetype: string?,
}

-- Couleurs par élément (couleur principale, couleur d'accent)
local ELEMENT_COLORS: { [string]: { Main: Color3, Accent: Color3 } } = {
	Feu = { Main = Color3.fromRGB(214, 84, 48), Accent = Color3.fromRGB(255, 176, 64) },
	Eau = { Main = Color3.fromRGB(52, 134, 201), Accent = Color3.fromRGB(150, 220, 245) },
	Plante = { Main = Color3.fromRGB(84, 160, 76), Accent = Color3.fromRGB(196, 228, 112) },
	Terre = { Main = Color3.fromRGB(150, 112, 72), Accent = Color3.fromRGB(214, 184, 124) },
	Vol = { Main = Color3.fromRGB(150, 190, 230), Accent = Color3.fromRGB(245, 245, 245) },
	Tenebres = { Main = Color3.fromRGB(62, 48, 92), Accent = Color3.fromRGB(170, 96, 230) },
	Mineral = { Main = Color3.fromRGB(110, 196, 208), Accent = Color3.fromRGB(255, 216, 92) },
}

-- Échelle globale selon le stade
local STAGE_SCALE: { [string]: number } = { Bebe = 0.55, Jeune = 0.85, Adulte = 1.25 }

-- Proportions selon le stade (tête plus grosse chez le bébé, ailes seulement à partir de jeune)
local STAGE_SHAPE: { [string]: { Head: number, Tail: number, Wing: number } } = {
	Bebe = { Head = 1.45, Tail = 0.6, Wing = 0 },
	Jeune = { Head = 1.15, Tail = 0.85, Wing = 0.6 },
	Adulte = { Head = 1.0, Tail = 1.0, Wing = 1.0 },
}

-- Proportions selon l'archétype
local ARCHETYPE_SHAPE: { [string]: { Width: number, Length: number, Head: number, Leg: number, Tail: number } } = {
	Equilibre = { Width = 1.0, Length = 1.0, Head = 1.0, Leg = 1.0, Tail = 1.0 },
	Rapide = { Width = 0.8, Length = 1.15, Head = 0.9, Leg = 1.1, Tail = 1.35 },
	Tank = { Width = 1.3, Length = 0.95, Head = 1.0, Leg = 1.25, Tail = 0.8 },
	Brute = { Width = 1.1, Length = 1.0, Head = 1.3, Leg = 1.0, Tail = 0.9 },
}

-- Rang de rareté (sert à ajouter cornes, pics, lueur, particules)
local RARITY_RANK: { [string]: number } = {
	Commun = 1, Rare = 2, Epique = 3, Legendaire = 4, Mythique = 5, Secret = 6, Mythe = 7, Exclusif = 5,
}
local HORN_COUNT: { [string]: number } = {
	Commun = 0, Rare = 2, Epique = 2, Legendaire = 4, Mythique = 4, Secret = 4, Mythe = 6, Exclusif = 4,
}

local function makePart(
	model: Model,
	body: BasePart?,
	name: string,
	shape: Enum.PartType,
	size: Vector3,
	color: Color3,
	material: Enum.Material?,
	cf: CFrame
): Part
	local part = Instance.new("Part")
	part.Name = name
	part.Shape = shape
	part.Size = size
	part.Color = color
	part.Material = material or Enum.Material.SmoothPlastic
	part.TopSurface = Enum.SurfaceType.Smooth
	part.BottomSurface = Enum.SurfaceType.Smooth
	part.CanCollide = false
	part.CanTouch = false
	part.CanQuery = false
	part.Massless = true
	part.Anchored = false
	part.CFrame = cf
	part.Parent = model
	if body then
		local weld = Instance.new("WeldConstraint")
		weld.Part0 = body
		weld.Part1 = part
		weld.Parent = part
	end
	return part
end

-- Construit un dragon centré sur l'origine. Retourne un Model (non parenté).
function Builder.build(config: DragonConfig): Model
	local element = config.Element or "Feu"
	local rarity = config.Rarity or "Commun"
	local stage = config.Stage or "Adulte"
	local archetype = config.Archetype or "Equilibre"

	local colors = ELEMENT_COLORS[element] or ELEMENT_COLORS.Feu
	local stageScale = STAGE_SCALE[stage] or 1
	local stageShape = STAGE_SHAPE[stage] or STAGE_SHAPE.Adulte
	local arch = ARCHETYPE_SHAPE[archetype] or ARCHETYPE_SHAPE.Equilibre
	local rank = RARITY_RANK[rarity] or 1
	local hornCount = HORN_COUNT[rarity] or 0

	local model = Instance.new("Model")
	model.Name = config.Name or "Dragon"

	-- Dimensions de base (en studs) multipliées par l'échelle du stade
	local s = stageScale
	local bodyD = 2.0 * s * arch.Width -- diamètre du corps
	local bodyL = 3.4 * s * arch.Length -- longueur du corps
	local headD = 1.5 * s * stageShape.Head * arch.Head
	local legH = 1.1 * s * arch.Leg
	local legD = 0.55 * s * arch.Width

	-- Corps : cylindre couché le long de Z
	local origin = CFrame.new(0, 0, 0)
	local alongZ = CFrame.Angles(0, math.rad(90), 0)
	local body = makePart(model, nil, "Body", Enum.PartType.Cylinder, Vector3.new(bodyL, bodyD, bodyD), colors.Main, nil, origin * alongZ)
	model.PrimaryPart = body

	-- Ventre (accent)
	makePart(model, body, "Belly", Enum.PartType.Cylinder, Vector3.new(bodyL * 0.8, bodyD * 0.7, bodyD * 0.7),
		colors.Accent, nil, origin * CFrame.new(0, -bodyD * 0.18, 0) * alongZ)

	-- Tête (sphère) devant le corps, un peu relevée
	local headPos = CFrame.new(0, bodyD * 0.45, -(bodyL / 2 + headD * 0.25))
	makePart(model, body, "Head", Enum.PartType.Ball, Vector3.new(headD, headD, headD), colors.Main, nil, origin * headPos)

	-- Museau
	makePart(model, body, "Snout", Enum.PartType.Block, Vector3.new(headD * 0.6, headD * 0.4, headD * 0.55),
		colors.Accent, nil, origin * headPos * CFrame.new(0, -headD * 0.12, -headD * 0.5))

	-- Yeux (blanc + pupille)
	for _, side in ipairs({ -1, 1 }) do
		local eyeD = headD * (stage == "Bebe" and 0.3 or 0.22)
		local eyeCF = origin * headPos * CFrame.new(side * headD * 0.27, headD * 0.12, -headD * 0.38)
		makePart(model, body, "Eye", Enum.PartType.Ball, Vector3.new(eyeD, eyeD, eyeD), Color3.fromRGB(255, 255, 255), nil, eyeCF)
		makePart(model, body, "Pupil", Enum.PartType.Ball, Vector3.new(eyeD * 0.5, eyeD * 0.5, eyeD * 0.5),
			Color3.fromRGB(20, 20, 20), nil, eyeCF * CFrame.new(0, 0, -eyeD * 0.35))
	end

	-- Cornes (selon rareté)
	if hornCount > 0 then
		local hornH = headD * 0.55
		local pairs_ = math.floor(hornCount / 2)
		for i = 1, pairs_ do
			local spread = (i == 1) and 0.28 or 0.42
			local back = (i - 1) * headD * 0.18
			for _, side in ipairs({ -1, 1 }) do
				local hornCF = origin * headPos * CFrame.new(side * headD * spread, headD * 0.5, headD * 0.05 + back)
					* CFrame.Angles(math.rad(25), 0, math.rad(-side * 12))
				makePart(model, body, "Horn", Enum.PartType.Block,
					Vector3.new(headD * 0.14, hornH, headD * 0.14), colors.Accent,
					Enum.Material.SmoothPlastic, hornCF)
			end
		end
	end

	-- Pattes
	local legX = bodyD * 0.38
	local legZ = bodyL * 0.3
	for _, sx in ipairs({ -1, 1 }) do
		for _, sz in ipairs({ -1, 1 }) do
			local legCF = origin * CFrame.new(sx * legX, -(bodyD / 2) - legH / 2 + legD * 0.3, sz * legZ)
				* CFrame.Angles(0, 0, math.rad(90)) -- le cylindre devient vertical
			makePart(model, body, "Leg", Enum.PartType.Cylinder, Vector3.new(legH, legD, legD), colors.Main, nil, legCF)
		end
	end

	-- Queue : 4 sphères de plus en plus petites
	local tailLen = 4
	local tailScale = stageShape.Tail * arch.Tail
	local zCursor = bodyL / 2
	for i = 1, tailLen do
		local d = bodyD * (0.85 - (i - 1) * 0.17) * (0.85 + 0.15 * math.min(tailScale, 1))
		local step = d * 0.7 * math.max(tailScale, 0.5)
		zCursor += step
		local tailCF = origin * CFrame.new(0, (i - 1) * 0.12 * s, zCursor - d * 0.2)
		makePart(model, body, "Tail" .. i, Enum.PartType.Ball, Vector3.new(d, d, d),
			(i == tailLen) and colors.Accent or colors.Main, nil, tailCF)
	end

	-- Ailes (à partir du stade Jeune) : deux plaques inclinées
	if stageShape.Wing > 0 then
		local span = 2.6 * s * stageShape.Wing * (1 + (rank - 1) * 0.06)
		local chord = 1.6 * s * stageShape.Wing
		for _, side in ipairs({ -1, 1 }) do
			local wingCF = origin * CFrame.new(side * (bodyD / 2 + span * 0.42), bodyD * 0.45 + span * 0.18, -bodyL * 0.05)
				* CFrame.Angles(0, 0, math.rad(side * 32))
			makePart(model, body, "Wing", Enum.PartType.Block, Vector3.new(span, 0.12 * s, chord), colors.Accent,
				Enum.Material.SmoothPlastic, wingCF)
		end
	end

	-- Pics dorsaux (Épique et plus)
	if rank >= 3 then
		local count = math.min(2 + rank, 6)
		for i = 1, count do
			local z = -bodyL * 0.4 + (i - 1) * (bodyL * 0.8 / (count - 1))
			local spike = 0.3 * s * (1 + rank * 0.08)
			makePart(model, body, "Spike", Enum.PartType.Block, Vector3.new(spike, spike, spike), colors.Accent, nil,
				origin * CFrame.new(0, bodyD / 2, z) * CFrame.Angles(math.rad(45), 0, math.rad(45)))
		end
	end

	-- Lueur et effets pour les hautes raretés
	if rank >= 4 then
		local light = Instance.new("PointLight")
		light.Color = colors.Accent
		light.Range = 8 + rank
		light.Brightness = 0.6 + rank * 0.15
		light.Parent = body
	end
	if rank >= 5 then
		-- Accents lumineux (Neon) pour Mythique et au-delà
		for _, d in ipairs(model:GetDescendants()) do
			if d:IsA("Part") and (d.Name == "Horn" or d.Name == "Spike" or d.Name == "Wing") then
				d.Material = Enum.Material.Neon
			end
		end
	end
	if rank >= 7 then
		local emitter = Instance.new("ParticleEmitter")
		emitter.Color = ColorSequence.new(colors.Accent)
		emitter.Size = NumberSequence.new(0.35, 0)
		emitter.Lifetime = NumberRange.new(1, 1.6)
		emitter.Rate = 12
		emitter.Speed = NumberRange.new(0.5, 1.5)
		emitter.LightEmission = 1
		emitter.Parent = body
	end

	-- Attributs pratiques pour le reste du jeu
	model:SetAttribute("Element", element)
	model:SetAttribute("Rarity", rarity)
	model:SetAttribute("Stage", stage)
	model:SetAttribute("Archetype", archetype)

	return model
end

-- Ancre ou libère toutes les pièces (utile pour une galerie de test)
function Builder.setAnchored(model: Model, anchored: boolean)
	for _, d in ipairs(model:GetDescendants()) do
		if d:IsA("BasePart") then
			d.Anchored = anchored
		end
	end
end

return Builder
