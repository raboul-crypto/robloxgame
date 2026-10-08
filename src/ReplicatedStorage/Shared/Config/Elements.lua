--!strict
-- Elements.lua
-- Configuration des éléments, forces, faiblesses et statuts

export type StatusEffect = {
	Name: string,
	DisplayName: string,
	Duration: number,
	SourceElement: string,
	Description: string,
}

export type ElementInfo = {
	Id: string,
	DisplayName: string,
	StrongAgainst: { [string]: boolean },
	WeakAgainst: { [string]: boolean },
}

local Elements = {}

-- Table des éléments avec leurs interactions
Elements.List = {
	Feu = {
		Id = "Feu",
		DisplayName = "Feu",
		StrongAgainst = { Plante = true },
		WeakAgainst = { Eau = true, Terre = true },
	},
	Eau = {
		Id = "Eau",
		DisplayName = "Eau",
		StrongAgainst = { Feu = true, Terre = true, Mineral = true },
		WeakAgainst = { Plante = true },
	},
	Plante = {
		Id = "Plante",
		DisplayName = "Plante",
		StrongAgainst = { Eau = true, Terre = true },
		WeakAgainst = { Feu = true, Vol = true },
	},
	Terre = {
		Id = "Terre",
		DisplayName = "Terre",
		StrongAgainst = { Feu = true, Vol = true },
		WeakAgainst = { Eau = true, Plante = true },
	},
	Vol = {
		Id = "Vol",
		DisplayName = "Vol",
		StrongAgainst = { Plante = true },
		WeakAgainst = { Terre = true, Tenebres = true, Mineral = true },
	},
	Tenebres = {
		Id = "Tenebres",
		DisplayName = "Ténèbres",
		StrongAgainst = { Vol = true },
		WeakAgainst = { Mineral = true },
	},
	Mineral = {
		Id = "Mineral",
		DisplayName = "Minéral",
		StrongAgainst = { Tenebres = true, Vol = true },
		WeakAgainst = { Eau = true },
	},
}

-- Multiplicateurs de dégâts élémentaires
Elements.Multipliers = {
	Strong = 1.5,
	Weak = 0.75,
	Neutral = 1.0,
	SameElement = 0.75,
}

-- Statuts applicables par élément
Elements.Statuses = {
	Brulure = {
		Name = "Brulure",
		DisplayName = "Brûlure",
		Duration = 5,
		SourceElement = "Feu",
		DamagePercentPerSec = 0.03,
		Description = "3 % des PV max par seconde",
	},
	Gel = {
		Name = "Gel",
		DisplayName = "Gel",
		Duration = 4,
		SourceElement = "Eau",
		SpeedReductionPercent = 0.40,
		Description = "Vitesse de déplacement et d'attaque -40 %",
	},
	Poison = {
		Name = "Poison",
		DisplayName = "Poison",
		Duration = 8,
		SourceElement = "Plante",
		DamagePercentPerSec = 0.02,
		NoStack = true,
		Description = "2 % des PV max par seconde, ne se cumule pas",
	},
	Etourdissement = {
		Name = "Etourdissement",
		DisplayName = "Étourdissement",
		Duration = 1.5,
		SourceElement = "Terre",
		Stunned = true,
		Description = "Cible immobilisée",
	},
	Peur = {
		Name = "Peur",
		DisplayName = "Peur",
		Duration = 5,
		SourceElement = "Tenebres",
		DamageReductionPercent = 0.25,
		Description = "Dégâts infligés -25 %",
	},
}

-- Chances d'application des statuts selon la rareté
Elements.StatusChances = {
	Default = 0.15,
	HighRarity = 0.30, -- Pour Épique et supérieur
}

return Elements
