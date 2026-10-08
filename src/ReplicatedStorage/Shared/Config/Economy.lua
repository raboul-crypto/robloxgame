--!strict
-- Economy.lua
-- Configuration de l'économie : taux d'œufs, rebirth, diamants, capture et pénalités

export type EggRate = { [string]: number }

local Economy = {}

-- Taux d'obtention des œufs (probabilités cumulées ou pondérées)
Economy.EggRates = {
	-- Œuf commun de base
	Common = {
		Commun = 0.60,
		Rare = 0.30,
		Epique = 0.09,
		Legendaire = 0.01,
	},
	-- Œuf RNG standard (Mondes 1 à 3)
	RngStandard = {
		Rare = 0.45,
		Epique = 0.35,
		Legendaire = 0.17,
		Mythique = 0.03,
	},
	-- Œuf RNG avancé (Mondes 4 et 5)
	RngAdvanced = {
		Rare = 0.45,
		Epique = 0.35,
		Legendaire = 0.16,
		Mythique = 0.04,
	},
	-- Œuf aux diamants
	Diamond = {
		Epique = 0.60,
		Legendaire = 0.38,
		Mythique = 0.02,
	},
	-- Œuf caché dans le décor
	Hidden = {
		Commun = 0.70,
		Rare = 0.30,
	},
	-- Œuf de combat (chute sur dragon sauvage)
	CombatDrop = {
		Commun = 0.80,
		Rare = 0.20,
	},
}

-- Probabilités et seuils spéciaux
Economy.SpecialRates = {
	-- Chance de drop d'un œuf en battant un dragon sauvage (5 % à 15 %)
	CombatEggMinDropChance = 0.05,
	CombatEggMaxDropChance = 0.15,

	-- Chance d'obtenir 1 diamant (~12 %)
	DiamondChanceOnKill = 0.12,
	DiamondChanceOnHatch = 0.12,

	-- Chance d'œuf mutant en croisement (0.1 %)
	MutantEggChance = 0.001,

	-- Seuil de dégâts minimum pour recevoir l'œuf du dragon de zone (5 %)
	ZoneDragonMinDamagePercent = 0.05,
	ZoneDragonRewardCooldownSeconds = 3600, -- 1 heure max entre 2 récompenses
}

-- Paramètres du Rebirth
Economy.Rebirth = {
	MinWorldRequired = 3,
	MaxRebirths = 20,
	GoldBonusPerRebirth = 0.10,    -- +10 % d'or par rebirth
	LuckBonusPerRebirth = 0.02,    -- +2 % de chance de rareté supérieure par rebirth
	BaseCost = 5000000,            -- Coût du 1er rebirth (5M d'or)
	CostMultiplierPerLevel = 2.5,  -- Multiplicateur de coût par rebirth additionnel
}

-- Pénalité de mort
Economy.DeathPenalty = {
	GoldLossPercent = 0.05,        -- 5 % de l'or porté
	MaxGoldLoss = 500000,          -- Plafond de perte
	RespawnProtectionDuration = 3, -- 3 secondes d'invulnérabilité
}

-- Système d'apprivoisement (Capture)
Economy.Capture = {
	HpThresholdPercent = 0.30,     -- Nécessite moins de 30 % des PV max
	BaseSuccessRate = 0.25,        -- 25 % de base
	BaitTierBonusRate = 0.10,      -- +10 % par niveau d'appât
	FailureHealPercent = 0.50,     -- En cas d'échec, le dragon récupère 50 % de ses PV
	AllowedStages = {
		Bebe = true,
		Jeune = true,
	},
}

-- Slots d'équipement de dragons
Economy.EquipmentSlots = {
	Default = 3,
	WithPassTeamPlus2 = 5,
	WithPassTeamPlus3 = 8,
}

-- Base d'or générée par frappe sur mannequin de farm (Monde 1)
Economy.BaseFarmGold = {
	[1] = 5,
	[2] = 25,
	[3] = 120,
	[4] = 600,
	[5] = 3000,
}

-- Délai anti-spam minimum entre deux frappes de farm (en secondes)
Economy.FarmHitCooldown = 0.25
Economy.FarmMaxDistance = 20 -- Distance maximale en studs

return Economy
