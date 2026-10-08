--!strict
-- BuildLobby.server.lua
-- Génère le lobby (converti depuis le schématique Minecraft lobby.litematic) au lancement du serveur.
--
-- Pour le garder en dur dans la place (sans le régénérer à chaque Play) :
--   1. Lance Play, attends le message "[LobbyBuilder] ... pièces construites"
--   2. Dans l'Explorer, copie Workspace > Lobby (Ctrl+C)
--   3. Stop, colle dans Workspace (Ctrl+V), puis désactive ce script (propriété Enabled = false)

local Workspace = game:GetService("Workspace")
local ServerScriptService = game:GetService("ServerScriptService")

local LobbyBuilder = require(ServerScriptService:WaitForChild("Lobby"):WaitForChild("LobbyBuilder")) :: any

-- Position du centre du lobby dans la map. Décale-la si le lobby chevauche un monde.
local LOBBY_ORIGIN = Vector3.new(0, 0, 0)

-- Si un Lobby existe déjà dans Workspace (collé à la main), on ne le reconstruit pas.
if Workspace:FindFirstChild("Lobby") then
	print("[BuildLobby] Lobby déjà présent dans Workspace, génération ignorée.")
	return
end

print("[BuildLobby] Génération du lobby...")
LobbyBuilder.build(LOBBY_ORIGIN, Workspace)
