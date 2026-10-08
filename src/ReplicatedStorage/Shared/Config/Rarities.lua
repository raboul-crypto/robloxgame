--!strict
-- Rarities.lua
-- Configuration des raretés, multiplicateurs de combat et bonus de farm

export type RarityInfo = {
	Id: string,
	DisplayName: string,
	Tier: number,
	CombatMultiplier: number,
	FarmPower: number,
	StatusChance: number,
	Color: Color3,
}

local Rarities = {}

Rarities.List = {
	Commun = {
		Id = "Commun",
		DisplayName = "Commun",
		Tier = 1,
		CombatMultiplier = 1.0,
		FarmPower = 0.10,
		StatusChance = 0.15,
		Color = Color3.fromRGB(180, 180, 180),
	},
	Rare = {
		Id = "Rare",
		DisplayName = "Rare",
		Tier = 2,
		CombatMultiplier = 1.5,
		FarmPower = 0.25,
		StatusChance = 0.15,
		Color = Color3.fromRGB(50, 150, 255),
	},
	Epique = {
		Id = "Epique",
		DisplayName = "Épique",
		Tier = 3,
		CombatMultiplier = 2.2,
		FarmPower = 0.60,
		StatusChance = 0.30,
		Color = Color3.fromRGB(180, 70, 255),
	},
	Legendaire = {
		Id = "Legendaire",
		DisplayName = "Légendaire",
		Tier = 4,
		CombatMultiplier = 3.3,
		FarmPower = 1.50,
		StatusChance = 0.30,
		Color = Color3.fromRGB(255, 180, 0),
	},
	Mythique = {
		Id = "Mythique",
		DisplayName = "Mythique",
		Tier = 5,
		CombatMultiplier = 5.0,
		FarmPower = 4.00,
		StatusChance = 0.30,
		Color = Color3.fromRGB(255, 40, 80),
	},
	Secret = {
		Id = "Secret",
		DisplayName = "Secret",
		Tier = 6,
		CombatMultiplier = 8.0,
		FarmPower = 10.00,
		StatusChance = 0.30,
		Color = Color3.fromRGB(0, 230, 200),
	},
	Mythe = {
		Id = "Mythe",
		DisplayName = "Mythe",
		Tier = 7,
		CombatMultiplier = 12.0,
		FarmPower = 30.00,
		StatusChance = 0.30,
		Color = Color3.fromRGB(255, 230, 255),
	},
	Exclusif = {
		Id = "Exclusif",
		DisplayName = "Exclusif",
		Tier = 8,
		CombatMultiplier = 6.0,
		FarmPower = 6.00,
		StatusChance = 0.30,
		Color = Color3.fromRGB(255, 100, 200),
	},
}

-- Ordre croissant des raretés standard
Rarities.Tiers = {
	"Commun",
	"Rare",
	"Epique",
	"Legendaire",
	"Mythique",
	"Secret",
	"Mythe",
}

return Rarities
