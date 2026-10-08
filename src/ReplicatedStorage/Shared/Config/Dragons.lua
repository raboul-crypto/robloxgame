--!strict
-- Dragons.lua
-- Référentiel des 40 dragons du jeu + 2 exclusifs payants

export type DragonData = {
	Id: string,
	DisplayName: string,
	Element: string,
	Rarity: string,
	Archetype: string,
	World: number,
	IsExclusive: boolean?,
}

local Dragons = {}

Dragons.List = {
	-- =========================================================================
	-- MONDE 1 : La Plaine des Aurores (8 dragons)
	-- =========================================================================
	Pousse = {
		Id = "Pousse",
		DisplayName = "Pousse",
		Element = "Plante",
		Rarity = "Commun",
		Archetype = "Equilibre",
		World = 1,
	},
	Mottin = {
		Id = "Mottin",
		DisplayName = "Mottin",
		Element = "Terre",
		Rarity = "Commun",
		Archetype = "Tank",
		World = 1,
	},
	Brindille = {
		Id = "Brindille",
		DisplayName = "Brindille",
		Element = "Plante",
		Rarity = "Commun",
		Archetype = "Rapide",
		World = 1,
	},
	Galet = {
		Id = "Galet",
		DisplayName = "Galet",
		Element = "Terre",
		Rarity = "Commun",
		Archetype = "Brute",
		World = 1,
	},
	Trefle = {
		Id = "Trefle",
		DisplayName = "Trèfle",
		Element = "Plante",
		Rarity = "Rare",
		Archetype = "Equilibre",
		World = 1,
	},
	Bruyere = {
		Id = "Bruyere",
		DisplayName = "Bruyère",
		Element = "Terre",
		Rarity = "Rare",
		Archetype = "Tank",
		World = 1,
	},
	Sillon = {
		Id = "Sillon",
		DisplayName = "Sillon",
		Element = "Terre",
		Rarity = "Rare",
		Archetype = "Brute",
		World = 1,
	},
	Aurore = {
		Id = "Aurore",
		DisplayName = "Aurore",
		Element = "Plante",
		Rarity = "Epique",
		Archetype = "Equilibre",
		World = 1,
	},

	-- =========================================================================
	-- MONDE 2 : Les Dunes Ardentes (8 dragons)
	-- =========================================================================
	Braisillon = {
		Id = "Braisillon",
		DisplayName = "Braisillon",
		Element = "Feu",
		Rarity = "Commun",
		Archetype = "Rapide",
		World = 2,
	},
	Cendron = {
		Id = "Cendron",
		DisplayName = "Cendron",
		Element = "Feu",
		Rarity = "Commun",
		Archetype = "Equilibre",
		World = 2,
	},
	Dune = {
		Id = "Dune",
		DisplayName = "Dune",
		Element = "Terre",
		Rarity = "Commun",
		Archetype = "Tank",
		World = 2,
	},
	Escarbille = {
		Id = "Escarbille",
		DisplayName = "Escarbille",
		Element = "Feu",
		Rarity = "Rare",
		Archetype = "Brute",
		World = 2,
	},
	Sirocco = {
		Id = "Sirocco",
		DisplayName = "Sirocco",
		Element = "Feu",
		Rarity = "Rare",
		Archetype = "Rapide",
		World = 2,
	},
	Magma = {
		Id = "Magma",
		DisplayName = "Magma",
		Element = "Feu",
		Rarity = "Epique",
		Archetype = "Brute",
		World = 2,
	},
	Mirage = {
		Id = "Mirage",
		DisplayName = "Mirage",
		Element = "Terre",
		Rarity = "Epique",
		Archetype = "Equilibre",
		World = 2,
	},
	Solaris = {
		Id = "Solaris",
		DisplayName = "Solaris",
		Element = "Feu",
		Rarity = "Legendaire",
		Archetype = "Equilibre",
		World = 2,
	},

	-- =========================================================================
	-- MONDE 3 : L'Archipel des Palmiers (8 dragons)
	-- =========================================================================
	Ecume = {
		Id = "Ecume",
		DisplayName = "Écume",
		Element = "Eau",
		Rarity = "Commun",
		Archetype = "Rapide",
		World = 3,
	},
	Corail = {
		Id = "Corail",
		DisplayName = "Corail",
		Element = "Eau",
		Rarity = "Commun",
		Archetype = "Tank",
		World = 3,
	},
	Palmier = {
		Id = "Palmier",
		DisplayName = "Palmier",
		Element = "Plante",
		Rarity = "Commun",
		Archetype = "Equilibre",
		World = 3,
	},
	Maree = {
		Id = "Maree",
		DisplayName = "Marée",
		Element = "Eau",
		Rarity = "Rare",
		Archetype = "Equilibre",
		World = 3,
	},
	Lagon = {
		Id = "Lagon",
		DisplayName = "Lagon",
		Element = "Eau",
		Rarity = "Rare",
		Archetype = "Rapide",
		World = 3,
	},
	Perle = {
		Id = "Perle",
		DisplayName = "Perle",
		Element = "Eau",
		Rarity = "Epique",
		Archetype = "Tank",
		World = 3,
	},
	Liane = {
		Id = "Liane",
		DisplayName = "Liane",
		Element = "Plante",
		Rarity = "Epique",
		Archetype = "Brute",
		World = 3,
	},
	Neptyr = {
		Id = "Neptyr",
		DisplayName = "Neptyr",
		Element = "Eau",
		Rarity = "Legendaire",
		Archetype = "Equilibre",
		World = 3,
	},

	-- =========================================================================
	-- MONDE 4 : La Flotte du Typhon (8 dragons)
	-- =========================================================================
	Goeland = {
		Id = "Goeland",
		DisplayName = "Goéland",
		Element = "Vol",
		Rarity = "Commun",
		Archetype = "Rapide",
		World = 4,
	},
	Mousse = {
		Id = "Mousse",
		DisplayName = "Mousse",
		Element = "Eau",
		Rarity = "Commun",
		Archetype = "Tank",
		World = 4,
	},
	Rafale = {
		Id = "Rafale",
		DisplayName = "Rafale",
		Element = "Vol",
		Rarity = "Rare",
		Archetype = "Rapide",
		World = 4,
	},
	Boussole = {
		Id = "Boussole",
		DisplayName = "Boussole",
		Element = "Eau",
		Rarity = "Rare",
		Archetype = "Equilibre",
		World = 4,
	},
	Tempete = {
		Id = "Tempete",
		DisplayName = "Tempête",
		Element = "Vol",
		Rarity = "Epique",
		Archetype = "Brute",
		World = 4,
	},
	Typhon = {
		Id = "Typhon",
		DisplayName = "Typhon",
		Element = "Eau",
		Rarity = "Legendaire",
		Archetype = "Brute",
		World = 4,
	},
	Brume = {
		Id = "Brume",
		DisplayName = "Brume",
		Element = "Tenebres",
		Rarity = "Legendaire",
		Archetype = "Rapide",
		World = 4,
	},
	Leviathan = {
		Id = "Leviathan",
		DisplayName = "Léviathan",
		Element = "Eau",
		Rarity = "Mythique",
		Archetype = "Tank",
		World = 4,
	},

	-- =========================================================================
	-- MONDE 5 : L'Abysse de l'Épave (8 dragons)
	-- =========================================================================
	Stalactite = {
		Id = "Stalactite",
		DisplayName = "Stalactite",
		Element = "Mineral",
		Rarity = "Rare",
		Archetype = "Tank",
		World = 5,
	},
	Ombrelame = {
		Id = "Ombrelame",
		DisplayName = "Ombrelame",
		Element = "Tenebres",
		Rarity = "Epique",
		Archetype = "Rapide",
		World = 5,
	},
	Quartz = {
		Id = "Quartz",
		DisplayName = "Quartz",
		Element = "Mineral",
		Rarity = "Legendaire",
		Archetype = "Equilibre",
		World = 5,
	},
	Pepite = {
		Id = "Pepite",
		DisplayName = "Pépite",
		Element = "Mineral",
		Rarity = "Mythique",
		Archetype = "Brute",
		World = 5,
	},
	Brillant = {
		Id = "Brillant",
		DisplayName = "Brillant",
		Element = "Mineral",
		Rarity = "Mythique",
		Archetype = "Tank",
		World = 5,
	},
	Revenant = {
		Id = "Revenant",
		DisplayName = "Revenant",
		Element = "Tenebres",
		Rarity = "Secret",
		Archetype = "Brute",
		World = 5,
	},
	Neant = {
		Id = "Neant",
		DisplayName = "Néant",
		Element = "Tenebres",
		Rarity = "Secret",
		Archetype = "Rapide",
		World = 5,
	},
	Aion = {
		Id = "Aion",
		DisplayName = "Aïon",
		Element = "Tenebres",
		Rarity = "Mythe",
		Archetype = "Equilibre",
		World = 5,
	},

	-- =========================================================================
	-- DRAGONS EXCLUSIFS (2 emplacements)
	-- =========================================================================
	Exclusif1 = {
		Id = "Exclusif1",
		DisplayName = "Dragon Flamboyant",
		Element = "Feu",
		Rarity = "Exclusif",
		Archetype = "Equilibre",
		World = 0,
		IsExclusive = true,
	},
	Exclusif2 = {
		Id = "Exclusif2",
		DisplayName = "Dragon du Crépuscule",
		Element = "Tenebres",
		Rarity = "Exclusif",
		Archetype = "Equilibre",
		World = 0,
		IsExclusive = true,
	},
}

-- Récupère la liste des dragons appartenant à un monde donné
function Dragons.getByWorld(worldId: number): { DragonData }
	local result = {}
	for _, dragon in pairs(Dragons.List) do
		if dragon.World == worldId then
			table.insert(result, dragon)
		end
	end
	return result
end

-- Récupère la liste des dragons selon une rareté et un monde
function Dragons.getByRarityAndWorld(rarity: string, worldId: number): { DragonData }
	local result = {}
	for _, dragon in pairs(Dragons.List) do
		if dragon.Rarity == rarity and dragon.World == worldId then
			table.insert(result, dragon)
		end
	end
	return result
end

return Dragons
