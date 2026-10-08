--!strict
-- Network.lua
-- Gestionnaire centralisé des RemoteEvents et RemoteFunctions.
-- Évite les blocages et les yields infinis sur WaitForChild.

local ReplicatedStorage = game:GetService("ReplicatedStorage")
local RunService = game:GetService("RunService")

local isServer = RunService:IsServer()

local eventsFolder = ReplicatedStorage:FindFirstChild("Events")
if not eventsFolder then
	if isServer then
		eventsFolder = Instance.new("Folder")
		eventsFolder.Name = "Events"
		eventsFolder.Parent = ReplicatedStorage
	else
		eventsFolder = ReplicatedStorage:WaitForChild("Events", 10) :: Folder
	end
end

local Network = {}

local REMOTE_EVENTS = {
	"DataSync",
	"FarmHitEffect",
	"HatchResult",
	"CombatDamageEffect",
	"PlayerHealthSync",
	"SelectCombatTarget",
	"Notification",
}

local REMOTE_FUNCTIONS = {
	"BuyEgg",
	"EquipPet",
	"UnequipPet",
	"AttemptCapture",
	"RebirthRequest",
	"BreedingStart",
	"BreedingClaim",
	"ChangeWorld",
	"FightBoss",
}

-- Initialisation côté serveur de tous les Remotes
if isServer and eventsFolder then
	for _, name in ipairs(REMOTE_EVENTS) do
		if not eventsFolder:FindFirstChild(name) then
			local event = Instance.new("RemoteEvent")
			event.Name = name
			event.Parent = eventsFolder
		end
	end

	for _, name in ipairs(REMOTE_FUNCTIONS) do
		if not eventsFolder:FindFirstChild(name) then
			local func = Instance.new("RemoteFunction")
			func.Name = name
			func.Parent = eventsFolder
		end
	end
end

function Network.getEvent(name: string): RemoteEvent
	if not eventsFolder then
		eventsFolder = ReplicatedStorage:WaitForChild("Events", 5) :: Folder
	end
	assert(eventsFolder, "[Network] Dossier Events introuvable")

	local event = eventsFolder:FindFirstChild(name)
	if not event then
		if isServer then
			event = Instance.new("RemoteEvent")
			event.Name = name
			event.Parent = eventsFolder
		else
			event = eventsFolder:WaitForChild(name, 5) :: RemoteEvent
		end
	end
	return event :: RemoteEvent
end

function Network.getFunction(name: string): RemoteFunction
	if not eventsFolder then
		eventsFolder = ReplicatedStorage:WaitForChild("Events", 5) :: Folder
	end
	assert(eventsFolder, "[Network] Dossier Events introuvable")

	local func = eventsFolder:FindFirstChild(name)
	if not func then
		if isServer then
			func = Instance.new("RemoteFunction")
			func.Name = name
			func.Parent = eventsFolder
		else
			func = eventsFolder:WaitForChild(name, 5) :: RemoteFunction
		end
	end
	return func :: RemoteFunction
end

return Network
