--!strict
-- Archetypes.lua
-- Profils d'équilibrage des statistiques (PV, dégâts, vitesse)

export type ArchetypeInfo = {
	Id: string,
	DisplayName: string,
	HpMultiplier: number,
	DamageMultiplier: number,
	SpeedMultiplier: number,
}

local Archetypes = {}

Archetypes.List = {
	Equilibre = {
		Id = "Equilibre",
		DisplayName = "Équilibré",
		HpMultiplier = 1.0,
		DamageMultiplier = 1.0,
		SpeedMultiplier = 1.0,
	},
	Rapide = {
		Id = "Rapide",
		DisplayName = "Rapide",
		HpMultiplier = 0.8,
		DamageMultiplier = 0.8,
		SpeedMultiplier = 1.3,
	},
	Tank = {
		Id = "Tank",
		DisplayName = "Tank",
		HpMultiplier = 1.4,
		DamageMultiplier = 0.8,
		SpeedMultiplier = 0.8,
	},
	Brute = {
		Id = "Brute",
		DisplayName = "Brute",
		HpMultiplier = 0.8,
		DamageMultiplier = 1.4,
		SpeedMultiplier = 0.8,
	},
}

return Archetypes
