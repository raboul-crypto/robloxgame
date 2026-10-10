--!strict
--[[
	VoxelDragonBuilder
	Construit les dragons voxel (générés depuis "Dragons Voxel.html") en Parts Roblox.
	Les données sont dans Shared/VoxelDragons/<Id>.lua (boîtes fusionnées, 1 cellule = 2 voxels du viewer).

		local VoxelDragonBuilder = require(ReplicatedStorage.Shared.VoxelDragonBuilder)
		if VoxelDragonBuilder.has("Pousse") then
			local m = VoxelDragonBuilder.build("Pousse", "Adulte")
			m.Parent = workspace
			m:PivotTo(CFrame.new(0, 5, 0))
		end

	Même convention que DragonModelBuilder : le dragon regarde vers -Z, PrimaryPart = "Body",
	pièces sans collision, massless. Les parts sont ancrées par défaut (le PetFollowController les ancre aussi).
	Chaque modèle (espèce + stade) est construit une seule fois puis cloné.
]]

local VoxelDragonBuilder = {}

local CELL = 0.16 -- taille d'une cellule en studs (adulte ≈ 8 studs de long)
local GIANT = 1.35

local folder = script.Parent:WaitForChild("VoxelDragons")
local cache: { [string]: Model } = {}
local dataCache: { [string]: any } = {}

local NEON = { eye = true, glow = true, star = true }
local MEM = { mem = true }

-- Effets élémentaires (mêmes familles que dans le viewer)
local FX: { [string]: { Color: string, Rate: number, Speed: NumberRange, Accel: Vector3, Size: number, Light: number } } = {
	Plante = { Color = "acc", Rate = 4, Speed = NumberRange.new(0.3, 0.8), Accel = Vector3.new(0, -0.6, 0), Size = 0.18, Light = 0 },
	Terre = { Color = "acc", Rate = 3, Speed = NumberRange.new(0.2, 0.5), Accel = Vector3.new(0, -0.2, 0), Size = 0.16, Light = 0 },
	Feu = { Color = "glow", Rate = 10, Speed = NumberRange.new(0.6, 1.4), Accel = Vector3.new(0, 1.2, 0), Size = 0.14, Light = 1 },
	Eau = { Color = "glow", Rate = 6, Speed = NumberRange.new(0.4, 0.9), Accel = Vector3.new(0, 0.8, 0), Size = 0.16, Light = 0.6 },
	Vol = { Color = "acc", Rate = 4, Speed = NumberRange.new(1.5, 2.5), Accel = Vector3.new(0, 0, 0), Size = 0.12, Light = 0.3 },
	Tenebres = { Color = "glow", Rate = 7, Speed = NumberRange.new(0.2, 0.6), Accel = Vector3.new(0, 0.4, 0), Size = 0.15, Light = 1 },
	Mineral = { Color = "acc", Rate = 5, Speed = NumberRange.new(0.2, 0.5), Accel = Vector3.new(0, 0.3, 0), Size = 0.14, Light = 0.8 },
}

local function normElement(e: string): string
	if e == "Ténèbres" then return "Tenebres" end
	if e == "Minéral" then return "Mineral" end
	return e
end

local function getData(id: string): any?
	if dataCache[id] ~= nil then
		return dataCache[id]
	end
	local mod = folder:FindFirstChild(id)
	if not mod or not mod:IsA("ModuleScript") then
		dataCache[id] = false
		return nil
	end
	local ok, data = pcall(require, mod)
	dataCache[id] = ok and data or false
	return ok and data or nil
end

function VoxelDragonBuilder.has(id: string): boolean
	return getData(id) ~= nil
end

local function makeTemplate(id: string, stage: string): Model?
	local data = getData(id)
	if not data then return nil end
	local st = data[stage] or data.Adulte
	if not st then return nil end

	local cell = CELL * (data.Giant and GIANT or 1)
	local colors: { { any } } = st.Colors
	local model = Instance.new("Model")
	model.Name = data.Name

	-- Parse des boîtes : x,y,z,w,h,d,couleur ; (axe x du viewer = avant)
	local boxes = {}
	local minX, maxX, maxY, minZ, maxZ = math.huge, -math.huge, 0, math.huge, -math.huge
	for entry in string.gmatch(st.Boxes, "[^;]+") do
		local v = string.split(entry, ",")
		local x, y, z, w, h, d, c = tonumber(v[1]) :: number, tonumber(v[2]) :: number, tonumber(v[3]) :: number,
			tonumber(v[4]) :: number, tonumber(v[5]) :: number, tonumber(v[6]) :: number, tonumber(v[7]) :: number
		table.insert(boxes, { x, y, z, w, h, d, c })
		minX = math.min(minX, x); maxX = math.max(maxX, x + w)
		minZ = math.min(minZ, z); maxZ = math.max(maxZ, z + d)
		maxY = math.max(maxY, y + h)
	end

	local height = maxY * cell
	local body = Instance.new("Part")
	body.Name = "Body"
	body.Size = Vector3.new((maxZ - minZ) * cell, height, (maxX - minX) * cell)
	body.Transparency = 1
	body.CanCollide = false
	body.CanTouch = false
	body.CanQuery = false
	body.Massless = true
	body.Anchored = true
	body.CFrame = CFrame.new(0, height / 2, 0)
	body.Parent = model
	model.PrimaryPart = body

	local accentColor = Color3.new(1, 1, 1)
	for _, b in ipairs(boxes) do
		local x, y, z, w, h, d, c = b[1], b[2], b[3], b[4], b[5], b[6], b[7]
		local col = colors[c]
		local role = col[1] :: string
		local color = Color3.fromRGB(col[2], col[3], col[4])
		local p = Instance.new("Part")
		p.Name = role
		p.Size = Vector3.new(d * cell, h * cell, w * cell)
		-- viewer (x, y, z) -> Roblox (z, y, -x) : la tête (+x) regarde vers -Z
		p.CFrame = CFrame.new((z + d / 2) * cell, (y + h / 2) * cell, -(x + w / 2) * cell)
		p.Color = color
		p.Material = NEON[role] and Enum.Material.Neon or Enum.Material.SmoothPlastic
		if MEM[role] and data.FinAlpha then p.Transparency = 0.25 end
		if data.Metal and (role == "main" or role == "main2" or role == "acc" or role == "acc2") then p.Reflectance = 0.15 end
		p.TopSurface = Enum.SurfaceType.Smooth
		p.BottomSurface = Enum.SurfaceType.Smooth
		p.CanCollide = false
		p.CanTouch = false
		p.CanQuery = false
		p.Massless = true
		p.Anchored = true
		p.CastShadow = role ~= "glow" and role ~= "star"
		p.Parent = model
	end

	-- Couleur d'accent pour les effets
	local element = normElement(data.Element)
	local fx = FX[element]
	if fx then
		for _, col in ipairs(colors) do
			if col[1] == fx.Color then accentColor = Color3.fromRGB(col[2], col[3], col[4]) end
		end
		local att = Instance.new("Attachment")
		att.Name = "FX"
		att.Parent = body
		local e = Instance.new("ParticleEmitter")
		e.Name = "ElementFX"
		e.Color = ColorSequence.new(accentColor)
		e.LightEmission = fx.Light
		e.Size = NumberSequence.new({ NumberSequenceKeypoint.new(0, fx.Size * (stage == "Bebe" and 0.7 or 1)), NumberSequenceKeypoint.new(1, 0) })
		e.Transparency = NumberSequence.new(0.1, 1)
		e.Lifetime = NumberRange.new(1.2, 2.2)
		e.Rate = fx.Rate * (stage == "Adulte" and 1.5 or 1)
		e.Speed = fx.Speed
		e.SpreadAngle = Vector2.new(180, 180)
		e.Acceleration = fx.Accel
		e.Shape = Enum.ParticleEmitterShape.Box
		e.Parent = att
	end

	model:SetAttribute("Element", element)
	model:SetAttribute("Stage", stage)
	model:SetAttribute("Voxel", true)
	return model
end

-- Retourne un nouveau Model (non parenté) pour l'espèce et le stade demandés, ou nil si pas de données.
function VoxelDragonBuilder.build(id: string, stage: string?): Model?
	local s = stage or "Bebe"
	local key = id .. "_" .. s
	local tpl = cache[key]
	if not tpl then
		local built = makeTemplate(id, s)
		if not built then return nil end
		tpl = built
		cache[key] = built
	end
	return tpl:Clone()
end

-- Ancre ou libère toutes les pièces
function VoxelDragonBuilder.setAnchored(model: Model, anchored: boolean)
	for _, d in ipairs(model:GetDescendants()) do
		if d:IsA("BasePart") then d.Anchored = anchored end
	end
end

return VoxelDragonBuilder
