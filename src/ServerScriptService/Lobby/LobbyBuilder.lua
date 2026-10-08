--!strict
-- LobbyBuilder.lua
-- Construit le lobby à partir de LobbyData (converti depuis lobby.litematic).
-- Les blocs identiques ont été fusionnés en grands pavés : ~42 000 Parts au lieu de 275 000 blocs.
--
-- Usage :
--   local LobbyBuilder = require(path.to.LobbyBuilder)
--   local model = LobbyBuilder.build(Vector3.new(0, 0, 0), workspace)

local LobbyData = require(script.Parent:WaitForChild("LobbyData")) :: any

local LobbyBuilder = {}

-- 1 bloc Minecraft = 3 studs (un perso Roblox fait ~5 studs, un perso Minecraft ~1,8 bloc)
LobbyBuilder.STUDS_PER_BLOCK = 3
local U = LobbyBuilder.STUDS_PER_BLOCK / 2 -- taille d'une sous-cellule (demi-bloc)

type Style = {
	color: Color3,
	material: Enum.Material,
	transparency: number?,
	collide: boolean?,
	shadow: boolean?,
}

-- Apparence de chaque bloc Minecraft côté Roblox. Modifie ici pour changer le rendu.
local STYLES: { [string]: Style } = {
	deepslate = { color = Color3.fromRGB(72, 72, 80), material = Enum.Material.Brick },
	netherbrick = { color = Color3.fromRGB(60, 28, 34), material = Enum.Material.Brick },
	tinted_glass = { color = Color3.fromRGB(60, 45, 78), material = Enum.Material.Glass, transparency = 0.45 },
	magma = { color = Color3.fromRGB(205, 85, 25), material = Enum.Material.CrackedLava },
	glowstone = { color = Color3.fromRGB(240, 200, 95), material = Enum.Material.Neon },
	barrier = { color = Color3.fromRGB(255, 0, 0), material = Enum.Material.SmoothPlastic, transparency = 1, shadow = false },
	black_glass = { color = Color3.fromRGB(20, 20, 24), material = Enum.Material.Glass, transparency = 0.4 },
	glass = { color = Color3.fromRGB(200, 230, 240), material = Enum.Material.Glass, transparency = 0.7 },
	redstone = { color = Color3.fromRGB(190, 30, 20), material = Enum.Material.SmoothPlastic },
}

local function newPart(style: Style, size: Vector3, cf: CFrame, parent: Instance): Part
	local p = Instance.new("Part")
	p.Anchored = true
	p.Size = size
	p.CFrame = cf
	p.Color = style.color
	p.Material = style.material
	p.Transparency = style.transparency or 0
	p.CanCollide = if style.collide == nil then true else style.collide
	p.CastShadow = if style.shadow == nil then true else style.shadow
	p.TopSurface = Enum.SurfaceType.Smooth
	p.BottomSurface = Enum.SurfaceType.Smooth
	p.Parent = parent
	return p
end

local function numbers(s: string): { number }
	local out = {}
	for _, v in string.split(s, ",") do
		table.insert(out, tonumber(v) :: number)
	end
	return out
end

-- Petite pause régulière pour ne pas bloquer le serveur pendant la construction
local built = 0
local function tick()
	built += 1
	if built % 3000 == 0 then
		task.wait()
	end
end

local function buildBoxes(origin: Vector3, model: Model)
	for kind, encoded in LobbyData.boxes :: { [string]: string } do
		local style = STYLES[kind] or STYLES.deepslate
		local folder = Instance.new("Folder")
		folder.Name = kind
		folder.Parent = model
		local n = numbers(encoded)
		for i = 1, #n, 6 do
			local x, y, z, w, h, d = n[i], n[i + 1], n[i + 2], n[i + 3], n[i + 4], n[i + 5]
			local size = Vector3.new(w, h, d) * U
			local center = origin + Vector3.new(x + w / 2, y + h / 2, z + d / 2) * U
			newPart(style, size, CFrame.new(center), folder)
			tick()
		end
	end
end

local ROD_STYLE: Style = { color = Color3.fromRGB(245, 240, 228), material = Enum.Material.Neon, collide = false, shadow = false }

local function buildRods(origin: Vector3, model: Model)
	local folder = Instance.new("Folder")
	folder.Name = "end_rods"
	folder.Parent = model
	local n = numbers(LobbyData.rods)
	local thick = LobbyBuilder.STUDS_PER_BLOCK / 6
	for i = 1, #n, 5 do
		local axis, x, y, z, len = n[i], n[i + 1], n[i + 2], n[i + 3], n[i + 4]
		-- (x,y,z) = coin du premier bloc en sous-cellules ; une barre traverse "len" blocs
		local c = Vector3.new(x + 1, y + 1, z + 1)
		local size: Vector3
		if axis == 1 then
			c += Vector3.new(len - 1, 0, 0)
			size = Vector3.new(len * LobbyBuilder.STUDS_PER_BLOCK, thick, thick)
		elseif axis == 3 then
			c += Vector3.new(0, 0, len - 1)
			size = Vector3.new(thick, thick, len * LobbyBuilder.STUDS_PER_BLOCK)
		else
			c += Vector3.new(0, len - 1, 0)
			size = Vector3.new(thick, len * LobbyBuilder.STUDS_PER_BLOCK, thick)
		end
		newPart(ROD_STYLE, size, CFrame.new(origin + c * U), folder)
		tick()
	end
end

local FACING: { [string]: Vector3 } = {
	north = Vector3.new(0, 0, -1),
	south = Vector3.new(0, 0, 1),
	east = Vector3.new(1, 0, 0),
	west = Vector3.new(-1, 0, 0),
}

local function buildProps(origin: Vector3, model: Model)
	local folder = Instance.new("Folder")
	folder.Name = "props"
	folder.Parent = model
	local B = LobbyBuilder.STUDS_PER_BLOCK
	for _, p in LobbyData.props :: { { any } } do
		local name, x, y, z, facing = p[1], p[2], p[3], p[4], p[5]
		local center = origin + Vector3.new(x + 1, y + 1, z + 1) * U
		local dir = FACING[facing] or Vector3.new(0, 0, -1)
		if name == "chest" then
			local chest = newPart({ color = Color3.fromRGB(160, 110, 50), material = Enum.Material.WoodPlanks },
				Vector3.new(B * 0.875, B * 0.875, B * 0.875), CFrame.new(center - Vector3.new(0, B / 16, 0)), folder)
			chest.Name = "Chest"
		elseif name == "wall_torch" then
			-- la torche est accrochée au mur situé à l'opposé de "facing"
			local pos = center - dir * (B * 0.3) + Vector3.new(0, B * 0.1, 0)
			local torch = newPart({ color = Color3.fromRGB(255, 205, 90), material = Enum.Material.Neon, collide = false, shadow = false },
				Vector3.new(B / 8, B * 0.6, B / 8), CFrame.lookAt(pos, pos + dir) * CFrame.Angles(math.rad(-20), 0, 0), folder)
			torch.Name = "Torch"
			local light = Instance.new("PointLight")
			light.Color = Color3.fromRGB(255, 190, 110)
			light.Range = 14
			light.Brightness = 1.2
			light.Parent = torch
		elseif name == "vine" then
			-- liane plaquée sur la face indiquée du bloc
			local pos = center + dir * (B / 2 - 0.05)
			local size = if dir.X ~= 0 then Vector3.new(0.1, B, B) else Vector3.new(B, B, 0.1)
			local vine = newPart({ color = Color3.fromRGB(60, 120, 45), material = Enum.Material.Grass, collide = false, shadow = false, transparency = 0.15 },
				size, CFrame.new(pos), folder)
			vine.Name = "Vine"
		end
		tick()
	end
end

--[[
	Construit tout le lobby.
	origin : position du centre du plancher principal, au niveau du bas du build.
	Retourne le Model créé (parenté à `parent` seulement à la fin, c'est beaucoup plus rapide).
]]
function LobbyBuilder.build(origin: Vector3, parent: Instance): Model
	built = 0
	local t0 = os.clock()
	local model = Instance.new("Model")
	model.Name = "Lobby"
	buildBoxes(origin, model)
	buildRods(origin, model)
	buildProps(origin, model)
	model.Parent = parent
	print(string.format("[LobbyBuilder] %d pièces construites en %.1f s", built, os.clock() - t0))
	return model
end

return LobbyBuilder
