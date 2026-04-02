---
allowed-tools: Read, Bash
description: Render ASCII fog-of-war map from world.json
user-facing: true
---

# /dungeon-map — Fog of War Map

Renders an ASCII map showing only rooms the player has visited. Unvisited rooms are hidden.

## Steps

1. Read `world.json`
2. Read `game/state.md` for current location
3. Filter rooms where `visited: true`
4. Render the map using ASCII art

## Map Layout (full — for reference only)

```
🔥 [Sunken Gate] ──── [Corridor of the Ashen Order] ──── [Forgotten Chapel]
         │                                                        │
   [Hollow Pit]                                          [Vestibule of Ash]
                                                                  │
                                                   🔒 [The Blinded Sanctum]
```

## Rendering Rules

- Only show rooms where `visited: true`
- Mark the player's current room with `[YOU]` suffix or highlight
- Mark bonfire rooms with `🔥`
- Mark locked rooms with `🔒` (if visible because an adjacent room is visited)
- Show connections between visited rooms with `────` (horizontal) or `│` (vertical)
- If a visited room connects to an unvisited room, show `── ???` to hint at unexplored paths
- Keep the spatial layout consistent with the full map topology

## Example Output (early game)

```
🔥 [Sunken Gate] [YOU] ──── ???
         │
       ???
```

## Example Output (mid game)

```
🔥 [Sunken Gate] ──── [Corridor of the Ashen Order] ──── [Forgotten Chapel] [YOU]
         │                                                        │
   [Hollow Pit]                                                 ???
```

## Notes

- This command is read-only — it never modifies game state
- It can be invoked at any time during gameplay
- Do not reveal room contents (enemies, items, NPCs) on the map
