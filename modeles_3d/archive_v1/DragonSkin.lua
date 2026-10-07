--!strict
-- Recolore un modele de dragon selon le nom de ses pieces.
-- Exemple : DragonSkin.apply(model, {Skin = Color3.fromRGB(220,60,45), Belly = Color3.fromRGB(255,215,150)})
local DragonSkin = {}

export type Palette = {Skin: Color3?, Belly: Color3?, Wing: Color3?, Horn: Color3?, Spike: Color3?}

local function role(name: string): string
	if name:find("Pupils") then return "Pupil" end
	if name:find("Eyes") then return "Eye" end
	if name:find("Belly") then return "Belly" end
	if name:find("Horns") or name:find("Claws") then return "Horn" end
	if name:find("Spikes") then return "Spike" end
	if name:find("Bones") then return "Skin" end
	if name:find("Fins") or name:match("^Wing[LR]$") then return "Wing" end
	return "Skin"
end

function DragonSkin.apply(model: Model, palette: Palette)
	for _, part in model:GetDescendants() do
		if part:IsA("MeshPart") then
			local r = role(part.Name)
			local c = (palette :: any)[r]
			if r == "Eye" then c = Color3.new(1, 1, 1) end
			if r == "Pupil" then c = Color3.fromRGB(18, 15, 22) end
			if c then part.Color = c end
		end
	end
end

return DragonSkin
