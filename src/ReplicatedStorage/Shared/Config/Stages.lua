--!strict
-- Stages.lua
-- Configuration des stades d'évolution des dragons

export type StageInfo = {
	Id: string,
	DisplayName: string,
	MinLevel: number,
	MaxLevel: number,
	StatMultiplier: number,
	FarmPowerMultiplier: number,
}

local Stages = {}

Stages.List = {
	Bebe = {
		Id = "Bebe",
		DisplayName = "Bébé",
		MinLevel = 1,
		MaxLevel = 14,
		StatMultiplier = 0.4,
		FarmPowerMultiplier = 0.5,
	},
	Jeune = {
		Id = "Jeune",
		DisplayName = "Jeune",
		MinLevel = 15,
		MaxLevel = 34,
		StatMultiplier = 0.7,
		FarmPowerMultiplier = 0.8,
	},
	Adulte = {
		Id = "Adulte",
		DisplayName = "Adulte",
		MinLevel = 35,
		MaxLevel = 50,
		StatMultiplier = 1.0,
		FarmPowerMultiplier = 1.0,
	},
}

Stages.MaxLevel = 50

-- Détermine le stade correspondant à un niveau donné
function Stages.getStageFromLevel(level: number): string
	if level >= 35 then
		return "Adulte"
	elseif level >= 15 then
		return "Jeune"
	else
		return "Bebe"
	end
end

return Stages
