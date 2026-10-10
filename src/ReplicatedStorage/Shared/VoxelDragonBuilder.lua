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

-- Effet de particules selon l'élément, et attributs communs du modèle
local function addElementFX(model: Model, body: BasePart, data: any, colors: { { any } }, stage: string)
	local element = normElement(data.Element)
	local fx = FX[element]
	if fx then
		local accentColor = Color3.new(1, 1, 1)
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
end

-- Directions des axes du viewer (1:+x 2:-x 3:+y 4:-y 5:+z 6:-z) converties en Roblox : x -> -Z, y -> Y, z -> X
local AXIS_DIR = {
	Vector3.new(0, 0, -1), Vector3.new(0, 0, 1), Vector3.new(0, 1, 0),
	Vector3.new(0, -1, 0), Vector3.new(1, 0, 0), Vector3.new(-1, 0, 0),
}
local AXIS_INDEX = { 1, 1, 2, 2, 3, 3 } -- axe du viewer (1 = x, 2 = y, 3 = z) de chaque direction

--[[
	Modèle « mi-voxel / low poly » : gros blocs et pentes (WedgePart) aux arêtes arrondies, yeux en volume.
	Format LowPoly.Parts : "B,x0,y0,z0,x1,y1,z1,c" (bloc) ou "W,x0,y0,z0,x1,y1,z1,c,a,b" (pente qui coupe l'arête
	entre les faces a et b) ; coordonnées en voxels du viewer, 1 voxel = CELL / 2 studs.
]]
local function makeLowPoly(data: any, stage: string, lp: any): Model
	local vox = CELL / 2 * (data.Giant and GIANT or 1)
	local colors: { { any } } = lp.Colors
	local model = Instance.new("Model")
	model.Name = data.Name

	local parts = {}
	local minV = Vector3.new(math.huge, math.huge, math.huge)
	local maxV = -minV
	for entry in string.gmatch(lp.Parts, "[^;]+") do
		local v = string.split(entry, ",")
		local a = { tonumber(v[2]) :: number, tonumber(v[3]) :: number, tonumber(v[4]) :: number }
		local b = { tonumber(v[5]) :: number, tonumber(v[6]) :: number, tonumber(v[7]) :: number }
		local col = colors[tonumber(v[8]) :: number]
		local role = col[1] :: string
		local p: BasePart
		-- centre et taille en Roblox : viewer (x, y, z) -> (z, y, -x)
		local center = Vector3.new((a[3] + b[3]) / 2, (a[2] + b[2]) / 2, -(a[1] + b[1]) / 2) * vox
		local ext = { (b[1] - a[1]) * vox, (b[2] - a[2]) * vox, (b[3] - a[3]) * vox }
		if v[1] == "W" then
			local ia, ib = tonumber(v[9]) :: number, tonumber(v[10]) :: number
			local ax, bx = AXIS_INDEX[ia], AXIS_INDEX[ib]
			local rx = 6 - ax - bx -- axe restant (1 + 2 + 3 = 6)
			local dirY, dirZ = AXIS_DIR[ia], -AXIS_DIR[ib]
			p = Instance.new("WedgePart")
			p.Size = Vector3.new(ext[rx], ext[ax], ext[bx])
			p.CFrame = CFrame.fromMatrix(center, dirY:Cross(dirZ), dirY, dirZ)
		else
			p = Instance.new("Part")
			p.Size = Vector3.new(ext[3], ext[2], ext[1])
			p.CFrame = CFrame.new(center)
		end
		p.Name = role == "dark" and "pupil" or role
		p.Color = Color3.fromRGB(col[2], col[3], col[4])
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
		p.CastShadow = role ~= "glow" and role ~= "star" and role ~= "eye" and role ~= "hi"
		table.insert(parts, p)
		local box = Vector3.new(ext[3], ext[2], ext[1]) / 2
		minV = minV:Min(center - box); maxV = maxV:Max(center + box)
	end

	-- pieds au sol (y = 0) et corps centré, comme les modèles voxel
	local offset = Vector3.new(-(minV.X + maxV.X) / 2, -minV.Y, -(minV.Z + maxV.Z) / 2)
	local size = maxV - minV
	local body = Instance.new("Part")
	body.Name = "Body"
	body.Size = size
	body.Transparency = 1
	body.CanCollide = false
	body.CanTouch = false
	body.CanQuery = false
	body.Massless = true
	body.Anchored = true
	body.CFrame = CFrame.new(0, size.Y / 2, 0)
	body.Parent = model
	model.PrimaryPart = body
	for _, p in ipairs(parts) do
		p.CFrame = p.CFrame + offset
		p.Parent = model
	end

	addElementFX(model, body, data, colors, stage)
	model:SetAttribute("LowPoly", true)
	return model
end

local function makeTemplate(id: string, stage: string): Model?
	local data = getData(id)
	if not data then return nil end
	local st = data[stage] or data.Adulte
	if not st then return nil end
	if st.LowPoly then
		return makeLowPoly(data, stage, st.LowPoly)
	end

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

	-- Si l'espèce a une couche d'yeux détaillée, les anciennes cellules "eye" (trop grossières) prennent la couleur de la peau
	local skinColor: { any }? = nil
	if st.Eyes then
		for _, col in ipairs(colors) do
			if col[1] == "main" then skinColor = col end
		end
	end

	for _, b in ipairs(boxes) do
		local x, y, z, w, h, d, c = b[1], b[2], b[3], b[4], b[5], b[6], b[7]
		local col = colors[c]
		if skinColor and col[1] == "eye" then
			col = skinColor
		end
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

	-- Yeux en volume, lisibles de face, de 3/4 et de profil.
	-- La couche Eyes (x,y,plan,côté,couleur ; x/y/plan en demi-cellules, côté = ±1) sert à localiser chaque œil.
	-- Chaque œil devient un globe qui dépasse de la tête ; la pupille occupe son coin avant-extérieur,
	-- donc elle apparaît à la fois sur la face latérale et sur la face avant, avec un reflet blanc par-dessus.
	if st.Eyes then
		local half = cell / 2
		local eps = cell * 0.03
		local eyeCol, darkCol = nil, nil
		local plates = {}
		for entry in string.gmatch(st.Eyes, "[^;]+") do
			local v = string.split(entry, ",")
			local col = colors[tonumber(v[5]) :: number]
			if col[1] == "eye" then eyeCol = col end
			if col[1] == "dark" then darkCol = col end
			table.insert(plates, {
				x = tonumber(v[1]) :: number, y = tonumber(v[2]) :: number, plane = tonumber(v[3]) :: number,
				side = tonumber(v[4]) :: number, dark = col[1] == "dark",
			})
		end

		-- Regroupe les plaques voisines en yeux (les hydres ont plusieurs têtes)
		local group: { number } = {}
		local function find(i: number): number
			while group[i] ~= i do i = group[i] end
			return i
		end
		for i = 1, #plates do group[i] = i end
		for i = 1, #plates do
			for j = i + 1, #plates do
				local a, b = plates[i], plates[j]
				if a.side == b.side and math.abs(a.x - b.x) <= 1.5 and math.abs(a.y - b.y) <= 1.5 then
					group[find(i)] = find(j)
				end
			end
		end
		local eyes: { [number]: any } = {}
		for i, p in ipairs(plates) do
			local r = find(i)
			local e = eyes[r]
			if not e then
				e = { side = p.side, x0 = p.x, x1 = p.x + 1, y0 = p.y, y1 = p.y + 1, plane = p.plane, d0 = math.huge, d1 = -math.huge }
				eyes[r] = e
			end
			e.x0 = math.min(e.x0, p.x); e.x1 = math.max(e.x1, p.x + 1)
			e.y0 = math.min(e.y0, p.y); e.y1 = math.max(e.y1, p.y + 1)
			e.plane = p.side > 0 and math.max(e.plane, p.plane) or math.min(e.plane, p.plane)
			if p.dark then e.d0 = math.min(e.d0, p.y); e.d1 = math.max(e.d1, p.y + 1) end
		end

		local function eyePart(name: string, col: { any }, neon: boolean, xa: number, xb: number, ya: number, yb: number, za: number, zb: number)
			local p = Instance.new("Part")
			p.Name = name
			p.Size = Vector3.new(math.abs(xb - xa), yb - ya, zb - za)
			p.CFrame = CFrame.new((xa + xb) / 2, (ya + yb) / 2, (za + zb) / 2)
			p.Color = Color3.fromRGB(col[2], col[3], col[4])
			p.Material = neon and Enum.Material.Neon or Enum.Material.SmoothPlastic
			p.TopSurface = Enum.SurfaceType.Smooth
			p.BottomSurface = Enum.SurfaceType.Smooth
			p.CanCollide = false
			p.CanTouch = false
			p.CanQuery = false
			p.Massless = true
			p.Anchored = true
			p.CastShadow = false
			p.Parent = model
		end

		-- Occupation des cellules, pour trouver la vraie surface de la tête sur toute l'emprise de l'œil
		local occ: { [number]: boolean } = {}
		local function key(x: number, y: number, z: number): number
			return ((x + 300) * 600 + (y + 300)) * 600 + (z + 300)
		end
		for _, b in ipairs(boxes) do
			for i = b[1], b[1] + b[4] - 1 do
				for j = b[2], b[2] + b[5] - 1 do
					for k = b[3], b[3] + b[6] - 1 do
						occ[key(i, j, k)] = true
					end
				end
			end
		end
		-- Couche latérale extérieure contiguë au-dessus de l'emprise [xa, xb[ × [ya, yb[ (en cellules)
		local function outerSurface(xa: number, xb: number, ya: number, yb: number, plane: number, side: number): number
			local layer = side > 0 and plane - 1 or plane
			local function layerHit(l: number): boolean
				for i = xa, xb - 1 do
					for j = ya, yb - 1 do
						if occ[key(i, j, l)] then return true end
					end
				end
				return false
			end
			while layerHit(layer + side) do
				layer += side
			end
			return side > 0 and layer + 1 or layer
		end

		local white = { "hi", 255, 255, 255 }
		local dark = darkCol or { "dark", 10, 10, 14 }
		local iris = eyeCol or { "eye", 255, 220, 60 }
		for _, e in pairs(eyes) do
			local s = e.side
			-- dimensions du globe (studs) ; viewer x -> Roblox -Z (l'avant de la tête est vers -Z)
			local w = math.max((e.x1 - e.x0) * half, cell * 1.5)
			local h = math.max((e.y1 - e.y0) * half, cell * 1.25)
			local zMid = -((e.x0 + e.x1) / 2) * half
			local yMid = ((e.y0 + e.y1) / 2) * half
			local front, back = zMid - w / 2, zMid + w / 2
			local bottom, top = yMid - h / 2, yMid + h / 2
			local plane = math.round(e.plane / 2) -- en cellules
			plane = outerSurface(math.floor(-back / cell), math.ceil(-front / cell), math.floor(bottom / cell), math.ceil(top / cell), plane, s)
			local surface = plane * cell
			local bulge = math.max(cell * 0.75, w * 0.45) -- dépassement hors de la tête
			local inner = surface - s * cell * 0.5
			local outer = surface + s * bulge
			eyePart("eye", iris, true, inner, outer, bottom, top, front, back)

			-- pupille au coin avant-extérieur : visible de face, de 3/4 et de profil
			local pd0 = e.d0 < math.huge and e.d0 * half or bottom + h * 0.15
			local pd1 = e.d1 > -math.huge and e.d1 * half or top - h * 0.2
			local ph = math.clamp(pd1 - pd0, h * 0.45, h * 0.75)
			local pyMid = math.clamp((pd0 + pd1) / 2, bottom + ph / 2, top - ph / 2)
			local pw = w * 0.55
			local pdep = bulge * 0.7
			eyePart("pupil", dark, false, outer - s * pdep, outer + s * eps,
				pyMid - ph / 2, pyMid + ph / 2, front - eps, front + pw)

			-- reflet en haut du coin de la pupille
			local hs = math.min(pw, ph, pdep) * 0.45
			local hyTop = pyMid + ph / 2
			eyePart("hi", white, true, outer - s * hs, outer + s * eps * 2,
				hyTop - hs, hyTop, front - eps * 2, front + hs)
		end
	end

	addElementFX(model, body, data, colors, stage)
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
