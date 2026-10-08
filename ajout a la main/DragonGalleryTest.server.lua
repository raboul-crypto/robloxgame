--[[
	DragonGalleryTest (SCRIPT DE TEST, à supprimer ou désactiver avant le lancement)
	Au lancement du jeu dans Studio, affiche 4 rangées de dragons de test :
	  1. les 7 éléments
	  2. les 8 raretés
	  3. les 3 stades
	  4. les 4 archétypes
	Les dragons sont ancrés devant le point (0, 0, -60) pour les voir facilement.
]]

local ReplicatedStorage = game:GetService("ReplicatedStorage")
local Builder = require(ReplicatedStorage.Shared.DragonModelBuilder)

local ENABLED = true -- passer à false pour désactiver la galerie
if not ENABLED then
	return
end

local folder = Instance.new("Folder")
folder.Name = "DragonGallery"
folder.Parent = workspace

local SPACING = 9
local ORIGIN = Vector3.new(0, 4, -60)

local function addLabel(model: Model, text: string)
	local primary = model.PrimaryPart
	if not primary then
		return
	end
	local gui = Instance.new("BillboardGui")
	gui.Size = UDim2.fromOffset(140, 30)
	gui.StudsOffset = Vector3.new(0, 4.5, 0)
	gui.AlwaysOnTop = true
	gui.Adornee = primary
	local label = Instance.new("TextLabel")
	label.Size = UDim2.fromScale(1, 1)
	label.BackgroundTransparency = 1
	label.TextColor3 = Color3.new(1, 1, 1)
	label.TextStrokeTransparency = 0.4
	label.TextScaled = true
	label.Font = Enum.Font.GothamMedium
	label.Text = text
	label.Parent = gui
	gui.Parent = primary
end

local function placeRow(rowIndex: number, configs: { { [string]: string } })
	for i, cfg in ipairs(configs) do
		local dragon = Builder.build({
			Name = cfg.Label,
			Element = cfg.Element,
			Rarity = cfg.Rarity,
			Stage = cfg.Stage,
			Archetype = cfg.Archetype,
		})
		dragon.Parent = folder
		Builder.setAnchored(dragon, true)
		local x = (i - 1) * SPACING - ((#configs - 1) * SPACING) / 2
		dragon:PivotTo(CFrame.new(ORIGIN + Vector3.new(x, 0, (rowIndex - 1) * -SPACING)))
		addLabel(dragon, cfg.Label)
	end
end

local elements = { "Feu", "Eau", "Plante", "Terre", "Vol", "Tenebres", "Mineral" }
local rarities = { "Commun", "Rare", "Epique", "Legendaire", "Mythique", "Secret", "Mythe", "Exclusif" }
local stages = { "Bebe", "Jeune", "Adulte" }
local archetypes = { "Equilibre", "Rapide", "Tank", "Brute" }

local rowElements, rowRarities, rowStages, rowArchetypes = {}, {}, {}, {}
for _, e in ipairs(elements) do
	table.insert(rowElements, { Label = e, Element = e, Rarity = "Rare", Stage = "Adulte", Archetype = "Equilibre" })
end
for _, r in ipairs(rarities) do
	table.insert(rowRarities, { Label = r, Element = "Feu", Rarity = r, Stage = "Adulte", Archetype = "Equilibre" })
end
for _, st in ipairs(stages) do
	table.insert(rowStages, { Label = st, Element = "Eau", Rarity = "Epique", Stage = st, Archetype = "Equilibre" })
end
for _, a in ipairs(archetypes) do
	table.insert(rowArchetypes, { Label = a, Element = "Plante", Rarity = "Rare", Stage = "Adulte", Archetype = a })
end

placeRow(1, rowElements)
placeRow(2, rowRarities)
placeRow(3, rowStages)
placeRow(4, rowArchetypes)
