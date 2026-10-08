--!strict
-- BuildLobby.server.lua
-- Génère le lobby (converti depuis le schématique Minecraft lobby.litematic) au lancement du serveur
-- et fait apparaître les joueurs directement dedans.
--
-- Pour le garder en dur dans la place (sans le régénérer à chaque Play) :
--   1. Lance Play, attends le message "[LobbyBuilder] ... pièces construites"
--   2. Dans l'Explorer, copie Workspace > Lobby (Ctrl+C)
--   3. Stop, colle dans Workspace (Ctrl+V). Le script verra qu'il existe et ne le reconstruira pas.

local Workspace = game:GetService("Workspace")
local ServerScriptService = game:GetService("ServerScriptService")

local LobbyBuilder = require(ServerScriptService:WaitForChild("Lobby"):WaitForChild("LobbyBuilder")) :: any

-- Position du centre du lobby dans la map (bas du build).
local LOBBY_ORIGIN = Vector3.new(0, 0, 0)

-- Point d'apparition, relatif au centre du lobby : sur la grande place, à ~56 blocs du centre,
-- à hauteur du sol principal (67 blocs * 3 studs = 201 studs), tourné vers le pilier central.
local SPAWN_OFFSET = Vector3.new(165, 201, 29)

-- 1. Le spawn est créé AVANT le lobby : le joueur qui arrive pendant la construction
--    tient debout sur la plateforme au lieu de tomber dans le vide.
local function setupSpawn()
	-- Désactive les autres points d'apparition éventuellement enregistrés dans la place
	for _, inst in Workspace:GetDescendants() do
		if inst:IsA("SpawnLocation") and inst.Name ~= "LobbySpawn" then
			inst.Enabled = false
		end
	end

	if Workspace:FindFirstChild("LobbySpawn") then
		return
	end

	local pos = LOBBY_ORIGIN + SPAWN_OFFSET + Vector3.new(0, 0.5, 0)
	local lookAt = Vector3.new(LOBBY_ORIGIN.X, pos.Y, LOBBY_ORIGIN.Z)

	local spawn = Instance.new("SpawnLocation")
	spawn.Name = "LobbySpawn"
	spawn.Size = Vector3.new(10, 1, 10)
	spawn.CFrame = CFrame.lookAt(pos, lookAt)
	spawn.Anchored = true
	spawn.Neutral = true
	spawn.Duration = 0 -- pas de bouclier ForceField à l'apparition
	spawn.Color = Color3.fromRGB(205, 85, 25)
	spawn.Material = Enum.Material.Neon
	spawn.Transparency = 0.6
	spawn.TopSurface = Enum.SurfaceType.Smooth
	-- enlève le logo de spawn par défaut
	local decal = spawn:FindFirstChildOfClass("Decal")
	if decal then
		decal:Destroy()
	end
	spawn.Parent = Workspace
end

setupSpawn()

-- 2. Construction du lobby (sauf s'il a déjà été collé dans la place)
if Workspace:FindFirstChild("Lobby") then
	print("[BuildLobby] Lobby déjà présent dans Workspace, génération ignorée.")
	return
end

print("[BuildLobby] Génération du lobby...")
LobbyBuilder.build(LOBBY_ORIGIN, Workspace)
