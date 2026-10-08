--!strict
-- DragonModels.lua
-- Passerelle centrale pour l'obtention des modèles 3D de dragons.
-- Fait le lien entre la configuration (Dragons.lua) et le constructeur (DragonModelBuilder.lua).
-- Plus tard, les vrais modèles 3D (MeshParts/FBX) remplaceront ce module sans impacter le reste du code.

local ReplicatedStorage = game:GetService("ReplicatedStorage")
local Shared = ReplicatedStorage:WaitForChild("Shared")
local Config = Shared:WaitForChild("Config")

local Dragons = require(Config:WaitForChild("Dragons")) :: any
local DragonModelBuilder = require(Shared:WaitForChild("DragonModelBuilder")) :: any

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

return DragonModels
