--!strict
-- DragonModels.lua
-- Passerelle centrale pour l'obtention des modèles 3D de dragons.
-- Utilise en priorité les modèles voxel (VoxelDragonBuilder + Shared/VoxelDragons),
-- et retombe sur le constructeur de test (DragonModelBuilder) si l'espèce n'a pas encore de données voxel.

local ReplicatedStorage = game:GetService("ReplicatedStorage")
local Shared = ReplicatedStorage:WaitForChild("Shared")
local Config = Shared:WaitForChild("Config")

local Dragons = require(Config:WaitForChild("Dragons")) :: any
local DragonModelBuilder = require(Shared:WaitForChild("DragonModelBuilder")) :: any
local VoxelDragonBuilder = require(Shared:WaitForChild("VoxelDragonBuilder")) :: any

local DragonModels = {}

--[[
	Génère ou instancie le modèle 3D d'un dragon selon son espèce et son stade.

	@param dragonId string Identifiant du dragon (ex: "Sillon", "Pousse")
	@param stage string? Stade ("Bebe", "Jeune", "Adulte"). Défaut : "Bebe"
	@return Model Le modèle 3D du dragon
]]
function DragonModels.getModel(dragonId: string, stage: string?): Model
	stage = stage or "Bebe"
	local dragonData = Dragons.List[dragonId]

	if VoxelDragonBuilder.has(dragonId) then
		local voxel = VoxelDragonBuilder.build(dragonId, stage)
		if voxel then
			voxel.Name = dragonData and dragonData.DisplayName or dragonId
			if dragonData then
				voxel:SetAttribute("Rarity", dragonData.Rarity)
				voxel:SetAttribute("Archetype", dragonData.Archetype)
			end
			return voxel
		end
	end

	if not dragonData then
		warn("[DragonModels] Dragon inconnu dans la configuration : " .. tostring(dragonId))
		-- Modèle de secours par défaut
		return DragonModelBuilder.build({
			Name = dragonId,
			Element = "Plante",
			Rarity = "Commun",
			Stage = stage,
			Archetype = "Equilibre",
		})
	end

	local model = DragonModelBuilder.build({
		Name = dragonData.DisplayName,
		Element = dragonData.Element,
		Rarity = dragonData.Rarity,
		Stage = stage,
		Archetype = dragonData.Archetype,
	})

	return model
end

-- Hauteur des dragons sauvages par stade, en studs (personnage Roblox R15 ≈ 5,5 studs) :
-- bébé à hauteur de genou, jeune un peu plus petit que le joueur, adulte 2 fois le joueur.
-- Les familiers (PetFollowController) gardent la taille de base de getModel.
local WILD_HEIGHT: { [string]: number } = {
	Bebe = 2.2,
	Jeune = 4.5,
	Adulte = 11,
}
local wildScaleCache: { [string]: number } = {}

-- Facteur d'échelle d'une espèce à un stade donné pour atteindre WILD_HEIGHT.
function DragonModels.getWildScale(dragonId: string, stage: string?): number
	local s = stage or "Bebe"
	local key = dragonId .. "_" .. s
	local cached = wildScaleCache[key]
	if cached then
		return cached
	end
	local model = DragonModels.getModel(dragonId, s)
	local _, size = model:GetBoundingBox()
	model:Destroy()
	local target = WILD_HEIGHT[s] or WILD_HEIGHT.Adulte
	local scale = size.Y > 0 and target / size.Y or 1
	wildScaleCache[key] = scale
	return scale
end

--[[
	Modèle d'un dragon sauvage à la taille de son stade. Le pivot reste au centre du Body :
	utiliser getGroundOffset pour poser le dragon au sol.
]]
function DragonModels.getWildModel(dragonId: string, stage: string?): Model
	local model = DragonModels.getModel(dragonId, stage)
	model:ScaleTo(DragonModels.getWildScale(dragonId, stage))
	return model
end

-- Décalage vertical entre le sol et le pivot pour que les pattes touchent le sol.
function DragonModels.getGroundOffset(model: Model): number
	local pivot = model:GetPivot()
	local cf, size = model:GetBoundingBox()
	return pivot.Position.Y - (cf.Position.Y - size.Y / 2)
end

return DragonModels
