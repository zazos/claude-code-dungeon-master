# Ashen Realm — Project Memory

A grimdark terminal RPG. Commands orchestrate, agents interpret, Python computes, skills provide lore.

---

## Project Structure

```
ashen-realm/
├── CLAUDE.md
├── rules_engine.py        ← ALL arithmetic lives here — never in agents
├── world.json             ← room graph — topology, connections, lock states, visited flags
├── game/
│   ├── state.md           ← read/write every turn
│   ├── inventory.md       ← gear management
│   ├── world-log.md       ← append-only event log
│   └── graveyard.md       ← append-only death log
└── .claude/
    ├── commands/          ← /dungeon, /dungeon-combat, /dungeon-map
    ├── agents/            ← dm, npc, rules
    └── skills/
        └── ashen-realm/
```

---

## Core Rules

- Always read `game/state.md` and `world.json` before processing any player turn
- Always write updated state back to `game/state.md` after every turn
- **Never compute arithmetic directly** — all dice rolls, damage, procs, position checks, and stat math go through `rules_engine.py`
- **Never invent room topology** — all connections and contents come from `world.json` only
- Never delete from `game/graveyard.md` or `game/world-log.md` — append only
- The rules agent speaks JSON only — never prose
- The DM agent speaks prose only — never JSON
- The NPC agent always runs with `context: fork` — never inline

---

## Agent Responsibilities

|Agent|Owns|Never Does|
|---|---|---|
|`dm`|Narration, world state, file writes, visited flags|Invent mechanics, invent topology, do math, speak for NPCs|
|`rules`|Interpret action, determine positions, call `rules_engine.py`, forward JSON|Narrate, compute numbers directly|
|`npc`|Character dialogue and mood state|Make mechanical decisions|

---

## Rules Engine — `rules_engine.py`

All game arithmetic is handled by this Python script. The rules agent calls it via bash tool and reads JSON back.

**Call pattern:**

```bash
python rules_engine.py <subcommand> [--params]
```

**Subcommands:**

|Subcommand|Computes|
|---|---|
|`attack`|d20 + modifiers vs defense, damage, proc checks, position penalty, stamina cost|
|`dodge`|Contested DEX roll, stamina cost|
|`flee`|Contested DEX vs enemy DEX, stamina cost|
|`check`|Generic d20 skill check vs stat threshold|
|`loot`|Random drop from bestiary probability table|
|`rest`|Partial HP/stamina/mana recovery from resources|
|`status-tick`|Tick active status durations, apply per-turn damage|
|`death-check`|Death's Door 1d6 roll when HP ≤ 25%|
|`turn-order`|Compare DEX values, return who acts first|

**Output is always JSON** — the rules agent forwards it to the DM without modification.

---

## Position System

Every combatant holds a FRONT or BACK slot. Tracked in `state.md` for the player, in combat context for enemies.

|Position|Can use|Takes|
|---|---|---|
|FRONT|Melee|Full melee, full ranged/spell damage|
|BACK|Ranged, spells|Half melee, full ranged/spell damage|

- Switching costs 1 stamina and uses the turn action
- Melee from BACK is allowed — deals half damage
- `rules_engine.py` applies position penalties — Claude never calculates them

---

## World Graph — `world.json`

Six rooms for MVP. All topology is defined here — never improvised.

```
🔥 [sunken_gate] ── [corridor_of_order] ── [forgotten_chapel]
        │                                          │
  [hollow_pit]                             [vestibule_of_ash]
                                                   │
                                          🔒 [blinded_sanctum]
```

|Room id|Enemy|NPC|Item|Locked|
|---|---|---|---|---|
|sunken_gate|—|—|ember_flask|No (bonfire)|
|hollow_pit|rotting_hound|—|loot_cache|No|
|corridor_of_order|hollow_knight|—|—|No|
|forgotten_chapel|—|blind_merchant|—|No|
|vestibule_of_ash|ashen_sentinel|—|iron_key|No|
|blinded_sanctum|sanctum_boss|—|—|Yes (iron_key)|

- `visited` flags flip to `true` on entry — DM writes this back to `world.json`
- Lock checks are handled by `rules_engine.py unlock` — not by Claude

---

## State File Format

`game/state.md` must always contain these exact fields:

```
## Character
Name, Class, Runs (death count)

## Vitals
HP: current / max
Stamina: current / max
Mana: current / max  (or — if class has no mana)
Position: FRONT or BACK

## Resources
Gold
Ember Flasks: current / max

## Location
Current: room_id
Last Bonfire: room_id

## Active Quests
- Quest name (lead or status)

## Status Effects
- StatusName (N turns remaining) or None
```

---

## Death Routine

When `rules_engine.py` returns `dead: true` (HP = 0 or Death's Door check failed):

1. Write to `game/graveyard.md`:
    
    ```
    ### [Name] — [Class]Cause of death: [how]Position at death: [FRONT/BACK] | HP: 0/[max] | Gold lost: [amount]Epitaph: [one sentence, poetic, understated]
    ```
    
2. Increment `Runs` counter
3. Reset `game/state.md` to new character defaults
4. Keep `game/world-log.md` intact — the world persists
5. Keep `world.json` visited flags intact — the world remembers
6. Print death screen to terminal

---

## Skill Loading Rules

The `ashen-realm` skill uses progressive disclosure — load only what is needed per turn:

|File|Load when|
|---|---|
|`SKILL.md`|Always|
|`references/combat.md`|Combat is active|
|`references/bestiary.md`|An enemy is encountered|
|`references/items.md`|Looting or trading|
|`references/classes.md`|Character creation only|
|`examples/sample-turn.md`|Output format is uncertain|

---

## Tone & Style

- DM prose: terse, oppressive, max 3 sentences per scene description
- `description_seed` in `world.json` is a foundation — never copy it verbatim, narrate from it
- Never reassure the player
- NPCs are guarded, suspicious, or broken — not helpful
- Silence is valid — not every room needs tension or an enemy
- Death narration: poetic, not dramatic

---

## Commands Reference

|Command|Usage|
|---|---|
|`/dungeon new`|Start a fresh character|
|`/dungeon resume`|Continue from `state.md`|
|`/dungeon-combat`|Invoked automatically by DM when combat begins|
|`/dungeon-map`|Render ASCII fog-of-war map from `world.json` visited flags|

---

## Development Notes

- **Build and test `rules_engine.py` first** — run every subcommand in isolation before touching any agent
- Simulate 10 combats via the script alone to verify balance before wiring Claude in
- Write `examples/sample-turn.md` before testing the DM agent — it anchors output format
- Test the rules agent second — give it a plain-text action, verify it returns clean JSON
- Verify `context: fork` is set on the NPC agent before running any NPC dialogue
- `rules_engine.py` reads enemy and item stats from JSON config files — keep these in sync with `bestiary.md` and `items.md`
- Commit `state.md` and `world.json` after each test session — use `/rewind` to recover cleanly if something breaks