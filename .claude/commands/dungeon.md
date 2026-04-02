---
allowed-tools: Read, Write, Edit, Bash, Agent, Glob, Grep, Skill
description: Main entry point for Ashen Realm — start a new game or resume
user-facing: true
---

# /dungeon — Ashen Realm

You are running the Ashen Realm, a grimdark terminal RPG. This command handles session start and the turn loop.

## Usage

- `/dungeon new` — create a new character and start the game
- `/dungeon resume` — continue from saved state

## On `/dungeon new`

### Step 0: Check for a living character

Before anything else, read `game/state.md`. If `Name` is not `—`:

1. A living character exists. Inform the player:
   > "[Name] the [Class] still walks the Realm. Starting a new game will abandon them. Continue? (yes/no)"
2. If the player says **no**: stop. Resume with `/dungeon resume`.
3. If the player says **yes**:
   - Append an abandoned entry to `game/graveyard.md`:
     ```
     ### [Name] — [Class]
     Cause of death: Abandoned
     Position at death: [position] | HP: [hp]/[max] | Gold lost: [gold]
     Epitaph: [one line, understated]
     ```
   - Append to `game/world-log.md`: `[Name] was abandoned. Run [N] ends.`
   - Reset all visited flags to `false` in `world.json` — a true fresh start means true fog of war
   - Proceed with character creation below

### Step 1: Character creation

1. Load the `ashen-realm` skill (always load `SKILL.md`, load `references/classes.md` for creation)
2. Ask the player for a **name** and **class** (Warrior, Sorcerer, or Wretch)
3. Write initial `game/state.md` with starting stats from `references/classes.md`:

   | Class    | HP | STR | DEX | SPR | Stamina | Mana | Starting Gear                              |
   |----------|----|----|-----|-----|---------|------|--------------------------------------------|
   | Warrior  | 24 | 16 | 10  | 6   | 6       | —    | Iron sword, wooden shield, 2 ember flasks  |
   | Sorcerer | 14 | 6  | 10  | 18  | 5       | 6    | Staff of ash, 5 soul fragments, 1 ember flask |
   | Wretch   | 18 | 12 | 14  | 8   | 6       | —    | Broken dagger, tattered cloth, 10 gold     |

4. Write initial `game/inventory.md` with starting gear
5. Set location to `sunken_gate`, mark it visited in `world.json`
6. Use the DM agent to narrate the opening scene using the `description_seed` from `world.json`
7. Append to `game/world-log.md`: `[Name] arrived at the Sunken Gate. Run [N].`

### Step 2 note: Death vs Abandonment

- **Death** (HP = 0): keep `world.json` visited flags — the world remembers
- **Abandonment** (`/dungeon new` override): reset `world.json` visited flags — true fresh start

## On `/dungeon resume`

1. Read `game/state.md` — if character name is `—`, tell the player to start a new game
2. Read `game/world-log.md` for context
3. Read `world.json` for current room
4. Use the DM agent to set the scene at the player's current location
5. Resume the turn loop

## Turn Loop

Each turn:

1. Read `game/state.md` and `world.json`
2. Receive player input as plain text
3. Load relevant skill references:
   - Always: `SKILL.md`
   - If combat: `references/combat.md`
   - If enemy present: `references/bestiary.md`
   - If looting/trading: `references/items.md`
4. Call the **Rules agent** to interpret the action and execute `rules_engine.py`
5. Call the **DM agent** to narrate the result
6. Write updated state to `game/state.md`
7. If entering a new room: update `visited` in `world.json`
8. If significant event: append to `game/world-log.md`
9. Print the status bar at the end

## Combat Trigger

When the player enters a room with an enemy (check `world.json` → `contains.enemy`), invoke `/dungeon-combat` with:
- Player stats from `game/state.md`
- Enemy id from `world.json`
- Both starting positions

## Movement

When the player wants to move:
1. Check `world.json` for valid connections from current room
2. If the target room is locked, call `rules_engine.py unlock` to check for the key
3. If valid, update location in `game/state.md` and `visited` in `world.json`
4. Narrate the new room via the DM agent
5. If the new room has an enemy, trigger combat
6. If the new room has an NPC, note their presence (player must choose to interact)

## NPC Interaction

When the player interacts with an NPC:
1. Call the **NPC agent** with character info, disposition, and player context
2. The DM agent incorporates the NPC's returned dialogue into the scene
3. Never let the DM speak as the NPC directly

## Rest (at bonfire only)

When the player rests at a bonfire room:
1. Check they have ember flasks > 0
2. Call `rules_engine.py rest` with current stats
3. Update `game/state.md` with recovered values
4. Clear expired status effects
5. Set `Last Bonfire` to current room

## Death

If at any point the Rules agent returns `dead: true` or `player_dead: true`:
1. Let the DM agent narrate the death
2. Write to `game/graveyard.md`
3. Increment `Runs`, reset `game/state.md`
4. Keep `world-log.md` and `world.json` visited flags intact
5. Prompt: "The ash takes another. /dungeon new to try again."

## Rules

- **Never compute arithmetic** — all math goes through `rules_engine.py` via the Rules agent
- **Never invent topology** — room connections come from `world.json` only
- **Never speak as NPCs** — delegate to the NPC agent
- **Always read state before acting, always write state after acting**
