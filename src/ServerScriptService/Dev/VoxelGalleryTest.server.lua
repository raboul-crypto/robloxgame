--[[
	VoxelGalleryTest (SCRIPT DE TEST, à désactiver avant le lancement)
	Affiche les dragons voxel en 3 rangées (Bébé, Jeune, Adulte) devant le point (0, 0, 60).
]]

local ENABLED = true
if not ENABLED then
	return
end

local ReplicatedStorage = game:GetService("ReplicatedStorage")
local Shared = ReplicatedStorage:WaitForChild("Shared")
local Dragons = require(Shared.Config.Dragons) :: any
local VoxelDragonBuilder = require(Shared.VoxelDragonBuilder) :: any

local folder = Instance.new("Folder")
folder.Name = "VoxelGallery"
folder.Parent = workspace

local ids = {}
for id in pairs(Dragons.List) do
	if VoxelDragonBuilder.has(id) then table.insert(ids, id) end
end
table.sort(ids, function(a, b)
	local da, db = Dragons.List[a], Dragons.List[b]
	if da.World ~= db.World then return da.World < db.World end
	return a < b
end)

local SPACING_X, SPACING_Z = 12, 14
local ORIGIN = Vector3.new(0, 0.5, 60)
for row, stage in ipairs({ "Bebe", "Jeune", "Adulte" }) do
	for i, id in ipairs(ids) do
		local m = VoxelDragonBuilder.build(id, stage)
		if m then
			local x = (i - 1) * SPACING_X - ((#ids - 1) * SPACING_X) / 2
			local h = m.PrimaryPart and m.PrimaryPart.Size.Y or 0
			m:PivotTo(CFrame.new(ORIGIN + Vector3.new(x, h / 2, (row - 1) * SPACING_Z)))
			m.Parent = folder
		end
	end
	task.wait()
end
print(("[VoxelGallery] %d espèces × 3 stades"):format(#ids))
