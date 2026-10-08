--!strict
-- Monetization.lua
-- Configuration des Game Passes et Developer Products
-- Les identifiants (AssetId / ProductId) sont mis à 0 provisoirement.
-- Remplacer les 0 par les vrais IDs créés dans le Creator Hub Roblox.

export type PassConfig = {
	Id: number,
	Name: string,
	PriceRobux: number,
	RequiresPass: string?,
}

export type ProductConfig = {
	Id: number,
	Name: string,
	PriceRobux: number,
	DurationSeconds: number?,
	Multiplier: number?,
	DiamondsAmount: number?,
}

local Monetization = {}

-- Game Passes (achats permanents)
Monetization.GamePasses = {
	EquipePlus2 = {
		Id = 0, -- À remplacer par l'ID réel du Game Pass
		Name = "Équipe +2",
		PriceRobux = 199,
		Description = "Permet d'équiper jusqu'à 5 dragons simultanément.",
	},
	EquipePlus3 = {
		Id = 0, -- À remplacer par l'ID réel du Game Pass
		Name = "Équipe +3",
		PriceRobux = 399,
		RequiresPass = "EquipePlus2",
		Description = "Permet d'équiper jusqu'à 8 dragons simultanément (nécessite Équipe +2).",
	},
	InventaireX2 = {
		Id = 0, -- À remplacer par l'ID réel du Game Pass
		Name = "Inventaire x2",
		PriceRobux = 249,
		Description = "Double l'espace total de stockage des dragons.",
	},
	EclosionRapideAuto = {
		Id = 0, -- À remplacer par l'ID réel du Game Pass
		Name = "Éclosion rapide et auto",
		PriceRobux = 149,
		Description = "Supprime l'animation d'éclosion et active l'éclosion automatique.",
	},
	OrX2Permanent = {
		Id = 0, -- À remplacer par l'ID réel du Game Pass
		Name = "Or x2 permanent",
		PriceRobux = 499,
		Description = "Multiplie de façon permanente tous les gains d'or par 2.",
	},
	ZoneVIP = {
		Id = 0, -- À remplacer par l'ID réel du Game Pass
		Name = "Zone VIP",
		PriceRobux = 399,
		Description = "Accès à l'île VIP exclusive avec coffres de diamants et bonus de chance.",
	},
}

-- Developer Products (achats consommables / répétables)
Monetization.Products = {
	BoostOr15Min = {
		Id = 0, -- À remplacer par l'ID réel du Developer Product
		Name = "Boost or x2 (15 min)",
		PriceRobux = 25,
		DurationSeconds = 900,
		Multiplier = 2,
	},
	BoostOr30Min = {
		Id = 0, -- À remplacer par l'ID réel du Developer Product
		Name = "Boost or x2 (30 min)",
		PriceRobux = 45,
		DurationSeconds = 1800,
		Multiplier = 2,
	},
	BoostChance15Min = {
		Id = 0, -- À remplacer par l'ID réel du Developer Product
		Name = "Boost chance (15 min)",
		PriceRobux = 49,
		DurationSeconds = 900,
	},
	Pack100Diamants = {
		Id = 0, -- À remplacer par l'ID réel du Developer Product
		Name = "Pack 100 diamants",
		PriceRobux = 49,
		DiamondsAmount = 100,
	},
	Pack500Diamants = {
		Id = 0, -- À remplacer par l'ID réel du Developer Product
		Name = "Pack 500 diamants",
		PriceRobux = 199,
		DiamondsAmount = 500,
	},
	Pack1500Diamants = {
		Id = 0, -- À remplacer par l'ID réel du Developer Product
		Name = "Pack 1 500 diamants",
		PriceRobux = 499,
		DiamondsAmount = 1500,
	},
	OeufExclusifMonde = {
		Id = 0, -- À remplacer par l'ID réel du Developer Product
		Name = "Œuf exclusif du monde",
		PriceRobux = 299,
	},
}

return Monetization
