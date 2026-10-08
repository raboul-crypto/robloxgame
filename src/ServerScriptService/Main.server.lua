--!strict
-- Init.server.lua
-- Script d'initialisation principal du serveur.
-- Démarre tous les services au lancement de la partie.

local ServerScriptService = game:GetService("ServerScriptService")
local ReplicatedStorage = game:GetService("ReplicatedStorage")

print("==================================================")
print("[Server Init] Démarrage des services de Dragon Pets Simulator...")
print("==================================================")

-- 1. Initialisation du réseau
local Shared = ReplicatedStorage:WaitForChild("Shared")
local Network = require(Shared:WaitForChild("Network")) :: any

-- 2. Chargement de tous les services serveur dans l'ordre de dépendance
local Services = ServerScriptService:WaitForChild("Services")

local DataService = require(Services:WaitForChild("DataService")) :: any
local EconomyService = require(Services:WaitForChild("EconomyService")) :: any
local HatchingService = require(Services:WaitForChild("HatchingService")) :: any
local PetService = require(Services:WaitForChild("PetService")) :: any
local CombatService = require(Services:WaitForChild("CombatService")) :: any
local CaptureService = require(Services:WaitForChild("CaptureService")) :: any
local WorldService = require(Services:WaitForChild("WorldService")) :: any
local BossService = require(Services:WaitForChild("BossService")) :: any
local BreedingService = require(Services:WaitForChild("BreedingService")) :: any
local MonetizationService = require(Services:WaitForChild("MonetizationService")) :: any
local TradeService = require(Services:WaitForChild("TradeService")) :: any

print("==================================================")
print("[Server Init] TOUS LES 11 SERVICES SONT OPÉRATIONNELS !")
print("==================================================")
