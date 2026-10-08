--!strict
-- Combat.lua
-- Configuration des paramètres de combat : joueur, dragons sauvages, cadences et statuts

export type PlayerCombatConfig = {
	MaxLevel: number,
	BaseHp: number,
	HpPerLevel: number,
	BaseDamage: number,
	DamagePerLevel: number,
	WalkSpeed: number,
	RegenPercentPerSec: number,
	RegenOutOfCombatSeconds: number,
}

local Combat = {}

-- Statistiques et règles du joueur
Combat.Player = {
	MaxLevel = 50,
	BaseHp = 100,
	HpPerLevel = 15,
	BaseDamage = 5,
	DamagePerLevel = 1,
	WalkSpeed = 16,
	RegenPercentPerSec = 0.02,     -- 2 % des PV max par seconde
	RegenOutOfCombatSeconds = 5,   -- 5 secondes sans coup donné ni reçu
}

-- Pourcentage de dégâts infligés au joueur par les dragons sauvages (en % des PV max du joueur)
Combat.WildDamageToPlayerPercent = {
	Bebe = 0.03,    -- 3 % par coup
	Jeune = 0.06,   -- 6 % par coup
	Adulte = 0.10,  -- 10 % par coup
	Elite = 0.15,   -- 15 % par coup
}

-- Règles des dragons du joueur en combat
Combat.PetCombat = {
	BaseSpeed = 100,               -- Vitesse de référence
	BaseAttackInterval = 1.5,      -- 1 attaque toutes les 1.5 s à 100 de vitesse
	KoDurationSeconds = 10,        -- Un dragon à 0 PV est K.O. pendant 10 secondes puis revient
	AttackRange = 25,              -- Distance max d'attaque d'un pet vers sa cible
}

-- Réapparition des dragons sauvages
Combat.WildDragonRespawnSeconds = 60

-- Durées et effets des statuts (synchronisés avec Elements.lua)
Combat.StatusDurations = {
	Brulure = 5,
	Gel = 4,
	Poison = 8,
	Etourdissement = 1.5,
	Peur = 5,
}

-- Calcul de l'intervalle entre deux attaques selon la vitesse
function Combat.getAttackInterval(speed: number): number
	if speed <= 0 then
		speed = 10
	end
	return Combat.PetCombat.BaseAttackInterval * (Combat.PetCombat.BaseSpeed / speed)
end

-- Calcul des PV max du joueur selon son niveau
function Combat.getPlayerMaxHp(level: number): number
	level = math.clamp(level, 1, Combat.Player.MaxLevel)
	return Combat.Player.BaseHp + (level - 1) * Combat.Player.HpPerLevel
end

-- Calcul des dégâts du joueur selon son niveau
function Combat.getPlayerDamage(level: number): number
	level = math.clamp(level, 1, Combat.Player.MaxLevel)
	return Combat.Player.BaseDamage + (level - 1) * Combat.Player.DamagePerLevel
end

return Combat
