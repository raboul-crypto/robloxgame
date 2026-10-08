--!strict
-- Worlds.lua
-- Configuration des 5 mondes, prix, statistiques de base, conditions et boss

export type TransitionBoss = {
	Name: string,
	Hp: number,
}

export type TransitionReqs = {
	RequiredUniqueDragons: number,
	RequiredPlayerLevel: number,
	RequiredTeamAvgLevel: number,
}

export type WorldInfo = {
	Id: number,
	Name: string,
	Description: string,
	Elements: { string },
	BaseHp: number,
	BaseDamage: number,
	EggPrices: {
		Common: number?,
		Rng: number?,
		Diamond: number?,
	},
	TargetEggTimeMinutes: number,
	WildStages: { string },
	WildHp: { [string]: number },
	ZoneDragonId: string,
	ZoneDragonRespawnSeconds: number,
	TransitionBoss: TransitionBoss,
	TransitionRequirements: TransitionReqs,
	UnlocksRebirth: boolean?,
}

local Worlds = {}

Worlds.List = {
	[1] = {
		Id = 1,
		Name = "La Plaine des Aurores",
		Description = "Plaine verdoyante, village paisible, rivière claire et forêt douce (tutoriel).",
		Elements = { "Plante", "Terre" },
		BaseHp = 100,
		BaseDamage = 10,
		EggPrices = {
			Common = 100,
			Rng = nil,
			Diamond = 150,
		},
		TargetEggTimeMinutes = 1,
		WildStages = { "Bebe" },
		WildHp = {
			Bebe = 80,
		},
		ZoneDragonId = "Aurore",
		ZoneDragonRespawnSeconds = 1800, -- 30 minutes
		TransitionBoss = {
			Name = "Gardien de la Plaine",
			Hp = 1500,
		},
		TransitionRequirements = {
			RequiredUniqueDragons = 5,
			RequiredPlayerLevel = 3,
			RequiredTeamAvgLevel = 5,
		},
		UnlocksRebirth = false,
	},
	[2] = {
		Id = 2,
		Name = "Les Dunes Ardentes",
		Description = "Désert brûlant, canyons escarpés, oasis secrètes et temple ensablé.",
		Elements = { "Feu", "Terre" },
		BaseHp = 400,
		BaseDamage = 40,
		EggPrices = {
			Common = 400,
			Rng = 5000,
			Diamond = 200,
		},
		TargetEggTimeMinutes = 2,
		WildStages = { "Bebe", "Jeune" },
		WildHp = {
			Bebe = 250,
			Jeune = 600,
		},
		ZoneDragonId = "Solaris",
		ZoneDragonRespawnSeconds = 1800,
		TransitionBoss = {
			Name = "Seigneur des Dunes",
			Hp = 8000,
		},
		TransitionRequirements = {
			RequiredUniqueDragons = 12,
			RequiredPlayerLevel = 10,
			RequiredTeamAvgLevel = 12,
		},
		UnlocksRebirth = false,
	},
	[3] = {
		Id = 3,
		Name = "L'Archipel des Palmiers",
		Description = "Plages paradisiaques, cocotiers, lagon turquoise et îles reliées par des ponts.",
		Elements = { "Eau", "Plante" },
		BaseHp = 1600,
		BaseDamage = 160,
		EggPrices = {
			Common = 50000,
			Rng = 800000,
			Diamond = 250,
		},
		TargetEggTimeMinutes = 4,
		WildStages = { "Bebe", "Jeune" },
		WildHp = {
			Bebe = 1000,
			Jeune = 2500,
		},
		ZoneDragonId = "Neptyr",
		ZoneDragonRespawnSeconds = 1800,
		TransitionBoss = {
			Name = "Kraken de Corail",
			Hp = 50000,
		},
		TransitionRequirements = {
			RequiredUniqueDragons = 20,
			RequiredPlayerLevel = 20,
			RequiredTeamAvgLevel = 22,
		},
		UnlocksRebirth = true,
	},
	[4] = {
		Id = 4,
		Name = "La Flotte du Typhon",
		Description = "Flotille de navires amarrés au cœur d'un typhon tourbillonnant.",
		Elements = { "Eau", "Vol", "Tenebres" },
		BaseHp = 7000,
		BaseDamage = 700,
		EggPrices = {
			Common = 2000000000, -- 2 milliards
			Rng = 40000000000,   -- 40 milliards
			Diamond = 300,
		},
		TargetEggTimeMinutes = 8,
		WildStages = { "Jeune", "Adulte" },
		WildHp = {
			Jeune = 10000,
			Adulte = 35000,
		},
		ZoneDragonId = "Leviathan",
		ZoneDragonRespawnSeconds = 1800,
		TransitionBoss = {
			Name = "Capitaine Typhon",
			Hp = 400000,
		},
		TransitionRequirements = {
			RequiredUniqueDragons = 28,
			RequiredPlayerLevel = 32,
			RequiredTeamAvgLevel = 35,
		},
		UnlocksRebirth = false,
	},
	[5] = {
		Id = 5,
		Name = "L'Abysse de l'Épave",
		Description = "Grotte abyssale ténébreuse, cristaux scintillants et carcasse d'un dragon colossal.",
		Elements = { "Tenebres", "Terre", "Mineral" },
		BaseHp = 30000,
		BaseDamage = 3000,
		EggPrices = {
			Common = 500000000000,  -- 500 milliards
			Rng = 10000000000000,   -- 10 000 milliards
			Diamond = 400,
		},
		TargetEggTimeMinutes = 18,
		WildStages = { "Adulte", "Elite" },
		WildHp = {
			Adulte = 120000,
			Elite = 600000,
		},
		ZoneDragonId = "Quartz",
		ZoneDragonRespawnSeconds = 1800,
		TransitionBoss = {
			Name = "Gardien de l'Épave",
			Hp = 5000000,
		},
		TransitionRequirements = {
			RequiredUniqueDragons = 35,
			RequiredPlayerLevel = 45,
			RequiredTeamAvgLevel = 45,
		},
		UnlocksRebirth = false,
	},
}

Worlds.MaxWorld = 5

return Worlds
