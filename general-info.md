# ⚔️ Ashen Realm — AI Dungeon Master

> A grimdark terminal RPG built on Claude Code. Death is permanent. The world does not care if you live.**Stack:** Commands · Subagents · Skills · Python Rules Engine

---

## 🗺️ Project Overview

Ashen Realm is a terminal-based narrative RPG inspired by the atmosphere and tone of Darkest Dungeon — oppressive, sparse, unforgiving. It is not a replication of any game. It is a fleshed-out idea made real through markdown files, Claude agents, and a lightweight Python engine. The player types actions in plain language. The world responds.

The three principles the game is built on:

- **Consequence** — every action costs something, every death is permanent
- **Opacity** — the world does not explain itself, you discover it
- **Persistence** — the world remembers what you did, even after you die

---

## 📁 File Structure

```
ashen-realm/
├── CLAUDE.md                          ← project memory & session rules
├── rules_engine.py                    ← Python CLI — all arithmetic lives here
├── world.json                         ← room graph — topology, connections, contents
├── game/
│   ├── state.md                       ← HP, stamina, position, location, quests
│   ├── inventory.md                   ← gear, durability, weight, equipped slots
│   ├── world-log.md                   ← append-only log of major world events
│   └── graveyard.md                   ← hall of dead characters (permadeath log)
├── .claude/
│   ├── commands/
│   │   ├── dungeon.md                 ← /dungeon — main entry point
│   │   ├── dungeon-combat.md          ← /dungeon-combat — invoked mid-fight
│   │   └── dungeon-map.md             ← /dungeon-map — ASCII fog-of-war map
│   ├── agents/
│   │   ├── dm.md                      ← Dungeon Master — narrator, world owner
│   │   ├── npc.md                     ← NPC agent — isolated voice per character
│   │   └── rules.md                   ← Rules agent — interprets action, calls rules_engine.py
│   └── skills/
│       └── ashen-realm/
│           ├── SKILL.md               ← overview + progressive loading trigger
│           ├── references/
│           │   ├── combat.md          ← action types, position rules, status definitions
│           │   ├── classes.md         ← warrior, sorcerer, wretch stats and gear
│           │   ├── bestiary.md        ← enemies, positions, moves, loot tables
│           │   └── items.md           ← weapons, armor, consumables
│           └── examples/
│               └── sample-turn.md    ← canonical example of a well-executed turn
```

---

## ⚙️ Game Systems

### Attributes

|Attribute|Governs|
|---|---|
|**STR**|Melee damage bonus|
|**DEX**|Stamina pool, turn order|
|**HP**|Hit points — zero means death|
|**SPR**|Mana pool, spell damage bonus|

**Modifier formula:** `floor(stat / 5)` — STR 14 = +2, STR 8 = +1. No lookup tables.

---

### Unified Attack Resolution

Every action — melee, ranged, spell — uses the same formula:

```
Roll 1d20 + Action Bonus  vs  Target Defense
```

The attack type determines which stats feed the bonus and defense:

|Attack Type|Bonus Stat|Defense Stat|
|---|---|---|
|Melee|STR modifier|Target STR modifier|
|Ranged|DEX modifier|Target DEX modifier|
|Spell|SPR modifier|Target SPR modifier|

**Hit thresholds:**

|Result|Outcome|
|---|---|
|Miss by 5+|Full miss — no stamina cost|
|Miss by 1–4|Graze — quarter damage, half stamina cost|
|Meet or beat|Hit — full damage|
|Beat by 5+|Crit — double damage, proc chance doubled|

**Damage formula:**

```
Melee:  weapon_base + STR_mod + 1d6
Ranged: weapon_base + DEX_mod + 1d6
Spell:  spell_base  + SPR_mod + 1d6
```

The `1d6` variance keeps combat tense without being unfair.

---

### Position System

Every combatant — player and enemy — occupies one of two slots:

```
[ FRONT ]   [ BACK ]
```

|Position|Can use|Takes|
|---|---|---|
|**Front**|Melee attacks|Full melee damage, full ranged/spell damage|
|**Back**|Ranged attacks, spells|Half melee damage, full ranged/spell damage|

**Rules:**

- Switching position costs 1 stamina and consumes your action for the turn
- Melee from Back is allowed — but deals half damage (reaching past your position)
- Enemies have positions too — a Back-row enemy cannot be reached cleanly until Front-row enemies are dealt with
- Position is tracked in `state.md` and resolved by `rules_engine.py`

---

### HP & Death's Door

No death saves. HP reaches 0 → character dies. Permadeath.

**Death's Door:** When HP drops to 25% or below, every incoming hit triggers a death check. `rules_engine.py` rolls 1d6 — on a 1, the character dies regardless of remaining HP. This creates the "one bad roll away from losing everything" tension that defines the tone.

---

### Stamina

```
Stamina Pool = 4 + DEX modifier
```

|Action|Stamina Cost|
|---|---|
|Melee attack|2|
|Ranged attack|1|
|Spell (tier 1)|2|
|Spell (tier 2+)|3|
|Dodge|1|
|Switch position|1|
|Use item|1|
|Flee attempt|2|

At 0 stamina the character is **Exhausted** — attacks deal half damage, defense halved. Stamina recovers partially on rest, never fully.

**Turn order:** highest DEX acts first. Ties broken by `rules_engine.py` coin flip.

---

### Mana

```
Mana Pool = 3 + SPR modifier
```

Spells cost 1–3 mana by tier. Mana does not recover in combat — only on rest, partially. The Sorcerer is a burst class that becomes a liability in long fights.

---

### Status Effects

|Status|Trigger|Effect|Duration|
|---|---|---|---|
|**Bleeding**|Bladed weapons on crit|−2 HP per turn|3 turns|
|**Hollowed**|Curse attacks, dark magic|SPR halved, spells cost double mana|2 turns|
|**Staggered**|Heavy blunt weapons|Lose next turn entirely|1 turn|
|**Frenzied**|Certain enemy attacks|Must attack — cannot dodge or flee|2 turns|
|**Rotting**|Undead enemies, poison|−1 HP per turn, healing halved|4 turns|
|**Doomed**|Rare boss mechanic|Death's Door threshold raised to 50%|Until cleansed|

**Rules:** statuses do not stack — a second application refreshes duration. Max 2 active statuses per character at once. `rules_engine.py` tracks and ticks durations.

---

### Starting Stats by Class

|Class|HP|STR|DEX|SPR|Stamina|Mana|
|---|---|---|---|---|---|---|
|Warrior|24|16|10|6|6|—|
|Sorcerer|14|6|10|18|5|6|
|Wretch|18|12|14|8|6|—|

- **Warrior** — tanks and hits hard, slow in prolonged fights
- **Sorcerer** — highest damage ceiling, fragile, runs dry fast
- **Wretch** — acts first, flees reliably, survives longer than it should

---

## 🌍 World — `world.json`

The room graph is a single JSON file at the project root. The DM and commands read from it — topology is never invented on the fly by Claude.

### Map Layout (MVP — 6 rooms)

```
🔥 [Sunken Gate] ──── [Corridor of the Ashen Order] ──── [Forgotten Chapel]
         │                                                        │
   [Hollow Pit]                                          [Vestibule of Ash]
                                                                  │
                                                   🔒 [The Blinded Sanctum]
```

|Room|Enemy|Item|NPC|Notes|
|---|---|---|---|---|
|Sunken Gate|—|Ember Flask|—|Start room, bonfire|
|Hollow Pit|Rotting Hound|Loot cache|—|Dead end|
|Corridor of the Ashen Order|Hollow Knight|—|—|Connects both wings|
|Forgotten Chapel|—|—|Blind Merchant|No combat|
|Vestibule of Ash|Ashen Sentinel|Iron Key|—|Key unlocks Sanctum|
|The Blinded Sanctum|Boss|—|—|Locked until Iron Key found|

### `world.json` Schema

```json
{
  "rooms": {
    "sunken_gate": {
      "name": "The Sunken Gate",
      "description_seed": "A collapsed archway. Ash drifts through cracks in the stone.",
      "connections": ["corridor_of_order", "hollow_pit"],
      "locked": false,
      "lock_requires": null,
      "contains": { "enemy": null, "item": "ember_flask", "npc": null },
      "bonfire": true,
      "visited": false
    },
    "corridor_of_order": {
      "name": "Corridor of the Ashen Order",
      "description_seed": "Long. Dark. The portraits have had their faces scratched out.",
      "connections": ["sunken_gate", "forgotten_chapel"],
      "locked": false,
      "lock_requires": null,
      "contains": { "enemy": "hollow_knight", "item": null, "npc": null },
      "bonfire": false,
      "visited": false
    },
    "hollow_pit": {
      "name": "The Hollow Pit",
      "description_seed": "A drop into darkness. Something has been eating down here.",
      "connections": ["sunken_gate"],
      "locked": false,
      "lock_requires": null,
      "contains": { "enemy": "rotting_hound", "item": "loot_cache", "npc": null },
      "bonfire": false,
      "visited": false
    },
    "forgotten_chapel": {
      "name": "The Forgotten Chapel",
      "description_seed": "Pews overturned. A single candle still burns. Someone tends it.",
      "connections": ["corridor_of_order", "vestibule_of_ash"],
      "locked": false,
      "lock_requires": null,
      "contains": { "enemy": null, "item": null, "npc": "blind_merchant" },
      "bonfire": false,
      "visited": false
    },
    "vestibule_of_ash": {
      "name": "Vestibule of Ash",
      "description_seed": "Grey snow falls upward here. A sentinel stands motionless at the far door.",
      "connections": ["forgotten_chapel", "blinded_sanctum"],
      "locked": false,
      "lock_requires": null,
      "contains": { "enemy": "ashen_sentinel", "item": "iron_key", "npc": null },
      "bonfire": false,
      "visited": false
    },
    "blinded_sanctum": {
      "name": "The Blinded Sanctum",
      "description_seed": "The air is wrong here. Whatever was worshipped here does not want to be remembered.",
      "connections": ["vestibule_of_ash"],
      "locked": true,
      "lock_requires": "iron_key",
      "contains": { "enemy": "sanctum_boss", "item": null, "npc": null },
      "bonfire": false,
      "visited": false
    }
  },
  "start": "sunken_gate"
}
```

**Key design rules:**

- `description_seed` is a prompt fragment — the DM narrates from it, never copies it
- `visited` flips to `true` on entry — `/dungeon-map` reads this for fog of war
- `lock_requires` holds the item id — checked by `rules_engine.py`, not Claude
- Enemy and item ids must match entries in `rules_engine.py`'s config files

---

## ⚡ Commands

Commands are **entry points** — user-invoked prompt templates in `.claude/commands/`. They inject context and orchestrate which agents to call.

### `/dungeon` — `dungeon.md`

The main command. Handles session start and the turn loop.

**What it does:**

- `new` — character creation (name, class), writes initial `state.md` and `inventory.md`, opens at `sunken_gate`
- `resume` — reads `state.md` + `world-log.md`, reconstructs context, drops player at last known location
- Each turn — reads player input → calls Rules agent → calls DM agent → writes updated state files

**Key instructions:**

```
Always read game/state.md and world.json before each turn.
Always write updated state back to game/state.md after each turn.
Call the rules agent before resolving any player action.
Never invent mechanics or room topology — adjudication goes to rules agent,
room data comes from world.json only.
If player HP reaches 0, trigger the death routine.
```

**How to invoke:**

```bash
claude
/dungeon new
/dungeon resume
```

---

### `/dungeon-combat` — `dungeon-combat.md`

Invoked automatically by the DM when an enemy is encountered. Keeps the combat loop isolated from the main session.

**What it does:**

- Receives player stats, enemy stats, and starting positions
- Calls Rules agent with combat skill loaded
- Loops until resolved: enemy dead, player dead, or fled
- Returns outcome summary to DM to narrate

**Key instructions:**

```
Load references/combat.md from the ashen-realm skill.
Call rules_engine.py for all rolls, damage, proc checks, and position logic.
Never compute arithmetic directly.
Track positions (FRONT/BACK) for both player and enemy each turn.
On player death: write to game/graveyard.md, return PLAYER_DEAD.
On enemy death: call rules_engine.py loot, return ENEMY_DEAD + loot.
```

---

### `/dungeon-map` — `dungeon-map.md`

Renders an ASCII map of visited rooms only. Unvisited rooms are hidden — fog of war.

**What it does:**

- Reads `world.json`, filters rooms where `visited: true`
- Renders ASCII graph with room names and connection lines
- Marks current location with `[YOU]`, bonfires with `🔥`, locked rooms with `🔒`

**Example output:**

```
🔥 [Sunken Gate] ──── [Corridor of the Ashen Order]
        │
  [Hollow Pit]
```

---

### Future Commands

|Command|Purpose|
|---|---|
|`/dungeon-inspect`|Deep-inspect item or enemy — lore, weaknesses, history|
|`/dungeon-rest`|Bonfire rest sequence — HP/stamina/mana recovery, resource cost|
|`/dungeon-trade`|Merchant NPC flow with inventory management|
|`/dungeon-recap`|Session summary — useful after long runs|

---

## 🤖 Agents

Agents are **autonomous actors** in fresh, isolated contexts. They communicate only through structured outputs passed by commands.

### Dungeon Master — `dm.md`

The narrator. Owns the world, drives the story forward.

**Persona:**

```
You are the Dungeon Master of the Ashen Realm — a dying world of grey ash,
hollow knights, and forgotten gods. You narrate in terse, oppressive prose.
No heroic flourishes. No comfort. The world is indifferent to whether you live.
```

**Responsibilities:**

- Describes environments using `description_seed` from `world.json` as a foundation — never copies it verbatim
- Reads `state.md` and `world-log.md` at the start of every turn
- Appends to `world-log.md` after significant events
- Flips `visited: true` in `world.json` when the player enters a new room
- Delegates all mechanical resolution to the Rules agent
- Calls the NPC agent whenever a named character speaks
- Never invents topology — room connections come from `world.json` only

**Tone rules:**

- Max 3 sentences per scene description
- Never reassure the player
- Silence is valid — not every room needs tension
- Death narration: poetic, not dramatic

---

### NPC Agent — `npc.md`

Voices individual characters. Runs with `context: fork` — each NPC gets a clean isolated context, their voice stays consistent without accumulating in the DM's context window.

**Input per invocation:**

```
NPC: Maren the Hollow Merchant
Disposition: Suspicious
Last player action: Attempted to pickpocket her
Player reputation: -12 (feared)
Speak one line of dialogue only.
```

**Output:**

```
Dialogue: "I know what you are. Touch my wares again and I'll call the Ashen Guard."
Mood: Hostile
```

**Why forked context:** After 10 NPC interactions, the DM's context would be full of stale dialogue. Forked context means the DM only ever sees the returned line — never the reasoning behind it.

---

### Rules Agent — `rules.md`

The interpreter and dispatcher. Reads a player action, determines what check is needed, constructs the `rules_engine.py` call, and returns structured JSON to the DM. Never does arithmetic itself.

**Responsibility split:**

|Concern|Handled by|
|---|---|
|Parse player intent|Rules agent|
|Determine action type (melee / ranged / spell / check)|Rules agent|
|Determine current positions (player + enemy)|Rules agent|
|All dice rolls, damage, proc checks, stamina costs|`rules_engine.py`|
|Position legality and penalty (melee from Back = half damage)|`rules_engine.py`|
|Status effect tick and duration|`rules_engine.py`|
|Death's Door check|`rules_engine.py`|
|Format result as JSON for DM|Rules agent|

**Example call:**

```bash
python rules_engine.py attack \
  --type melee \
  --str 16 \
  --weapon "iron_sword" \
  --player-position FRONT \
  --enemy "hollow_knight" \
  --enemy-position FRONT
```

**Example return:**

```json
{
  "roll": 17,
  "hit": true,
  "damage": 9,
  "bleeding_triggered": false,
  "enemy_hp_remaining": 11,
  "stamina_cost": 2,
  "position_penalty": false
}
```

---

### Future Agents

|Agent|Purpose|
|---|---|
|`lore.md`|World history oracle — answers in cryptic fragments|
|`echo.md`|Plays dead characters as hostile shades from `graveyard.md`|
|`merchant.md`|Trading loop with economy rules|
|`qa.md`|Second Claude reviewing each turn for mechanical consistency|

---

## 🧠 Skill — `ashen-realm`

The game's rulebook and lore bible. Folder-based, progressively disclosed — agents only load what they need per turn.

### `SKILL.md` — Trigger and overview

Always loaded. Tells agents what the skill contains and when to pull each reference file.

```
name: ashen-realm
description: >
  Load this skill for any Ashen Realm game session.
  Always load SKILL.md.
  Load references/combat.md during combat only.
  Load references/bestiary.md when an enemy is encountered.
  Load references/items.md when looting or trading.
  Load references/classes.md during character creation only.
  Load examples/sample-turn.md when output format is uncertain.
```

---

### `references/combat.md`

Action definitions and position rules. Does **not** contain formulas — those live in `rules_engine.py`. This file tells the Rules agent what actions exist and what parameters to pass to the script.

**Contains:**

- Action type catalogue (melee, ranged, spell, dodge, switch position, flee, use item)
- Parameters each action requires for the `rules_engine.py` call
- Position rules — Front/Back effects, melee reach penalty
- Status effect definitions — mechanical effect and narrative flavour
- Death's Door rule description

---

### `references/classes.md`

Starting archetypes. Loaded during character creation only.

|Class|HP|STR|DEX|SPR|Stamina|Mana|Starting Gear|
|---|---|---|---|---|---|---|---|
|Warrior|24|16|10|6|6|—|Iron sword, wooden shield, 2 ember flasks|
|Sorcerer|14|6|10|18|5|6|Staff of ash, 5 soul fragments, 1 ember flask|
|Wretch|18|12|14|8|6|—|Broken dagger, tattered cloth, 10 gold|

---

### `references/bestiary.md`

All enemies with stats, default positions, and loot. Loaded when an enemy is encountered.

**Entry format:**

```markdown
## Hollow Knight
HP: 20 | STR: 12 | DEX: 8 | Default Position: FRONT
Moves: Shield bash (Staggered proc), Overhead cleave (high damage), Retreat (switches to BACK)
Weakness: SPR attacks (+4 damage)
Loot: 1d6 × 10 gold | iron shard 40% | hollow core 15%
Lore: Once a knight of the Ashen Order. Now just hunger in armour.
```

---

### `references/items.md`

All gear with stats. Loaded when looting or trading.

**Entry format:**

```markdown
## Cursed Blade
Type: Weapon | Slot: Main hand | Attack Type: Melee
Base ATK: 5 | Bleeding proc on crit: yes
Curse effect: −2 max HP per rest (requires NPC ritual to remove)
Value: 120 gold
```

---

### `examples/sample-turn.md`

The most important file in the skill. Claude anchors output format to examples more reliably than to instructions alone. Shows a complete turn with position tracking and status bar.

```markdown
## Sample Turn

**Player input:** I move to the back and cast Ashen Bolt at the hollow knight.

**Rules agent call:**
python rules_engine.py attack --type spell --spr 18 --spell "ashen_bolt"
  --player-position BACK --enemy "hollow_knight" --enemy-position FRONT

**Rules agent output:**
{ "roll": 15, "hit": true, "damage": 11, "enemy_hp_remaining": 9,
  "stamina_cost": 3, "mana_cost": 1, "position_penalty": false }

**DM narration:**
The bolt tears through the corridor. The knight staggers, one gauntlet raised too late.
From the back you are harder to reach — but the mana it cost leaves a hollow feeling.
[HP: 14/24 | Stamina: 2/6 | Mana: 4/6 | Position: BACK | Room: Corridor of the Ashen Order]
```

---

### Future Skill Expansions

|File|Contents|
|---|---|
|`references/factions.md`|The Ashen Order, the Hollow Court, the Ember Cult — reputation effects|
|`references/spells.md`|Sorcerer spell list with tier, mana cost, and effect|
|`references/rituals.md`|NPC services — curse removal, resurrection attempt, item upgrade|
|`references/economy.md`|Shop price tables, item rarity, merchant disposition modifiers|

---

## 🎮 Game State Files

### `game/state.md`

Read at the start of every turn. Written back after every turn.

```markdown
## Character
Name: Aldric the Burnt
Class: Warrior
Runs: 2

## Vitals
HP: 14 / 24
Stamina: 4 / 6
Mana: — / —
Position: FRONT

## Resources
Gold: 45
Ember Flasks: 1 / 2

## Location
Current: corridor_of_order
Last Bonfire: sunken_gate

## Active Quests
- Find the source of the ash storm (lead: the blind merchant knows)
- Reach the Blinded Sanctum (need: iron key — Vestibule of Ash)

## Status Effects
- Bleeding (2 turns remaining)
```

---

### `game/graveyard.md`

Append-only permadeath log. Never deleted. Future Echo agent reads this to voice dead characters as shades.

```markdown
## The Graveyard

### Aldric the First — Warrior
Cause of death: Hollow Knight, overhead cleave, Corridor of the Ashen Order
Position at death: FRONT | HP: 0/24 | Gold lost: 120
Epitaph: He thought the shield would hold.

### Mira of the Ash — Wretch
Cause of death: Death's Door check failed (roll: 1), Hollow Pit
Position at death: BACK | HP: 3/18 | Gold lost: 340
Epitaph: She almost made it out.
```

---

## 🔁 A Full Turn — Step by Step

```
Player types: "I move to the back and attack the hollow knight with my bow"

1. /dungeon reads the input
2. /dungeon-combat is invoked (combat is active)
3. Rules Agent identifies: position switch + ranged attack
   → Step 1: position switch — costs 1 stamina, player moves FRONT → BACK
   → Step 2: constructs attack call:
     python rules_engine.py attack --type ranged --dex 14 --weapon "shortbow"
       --player-position BACK --enemy "hollow_knight" --enemy-position FRONT
   → Script: rolls d20 + DEX mod vs enemy DEX mod, calculates damage, checks procs
   → Returns: { roll: 13, hit: true, damage: 7, enemy_hp: 13, stamina_cost: 1,
                position_penalty: false }
4. Rules Agent forwards JSON to DM — no further math, ever
5. DM narrates:
   "You fall back into shadow. The arrow finds a gap in the pauldron.
    The knight turns — slower now, but angrier."
6. DM writes state.md: position BACK, stamina 6→4, enemy HP noted
7. Enemy turn: Rules Agent calls rules_engine.py with enemy params
   → Knight FRONT attacking player BACK — melee damage is halved
8. Status tick: rules_engine.py status-tick runs at end of turn
9. Turn output printed with full status bar
```

---

## 🐍 `rules_engine.py` — The Math Layer

All game arithmetic lives here. Claude never computes numbers. The Rules agent calls the script via bash and reads JSON back.

**Subcommands:**

|Subcommand|Computes|
|---|---|
|`attack`|d20 roll, modifiers, damage, proc checks, position penalty, stamina cost|
|`dodge`|Contested DEX roll, stamina cost|
|`flee`|Contested DEX vs enemy DEX, stamina cost|
|`check`|Generic d20 skill check vs stat threshold|
|`loot`|Random drop from bestiary probability table|
|`rest`|Partial HP/stamina/mana recovery from resources spent|
|`status-tick`|Ticks active status durations, applies per-turn damage|
|`death-check`|Death's Door 1d6 roll when HP ≤ 25%|
|`turn-order`|Compares DEX values, returns who acts first|

**Example calls:**

```bash
# Melee attack
python rules_engine.py attack --type melee --str 16 --weapon "iron_sword" \
  --player-position FRONT --enemy "hollow_knight" --enemy-position FRONT

# Ranged from back row
python rules_engine.py attack --type ranged --dex 14 --weapon "shortbow" \
  --player-position BACK --enemy "hollow_knight" --enemy-position FRONT

# Spell cast
python rules_engine.py attack --type spell --spr 18 --spell "ashen_bolt" \
  --player-position BACK --enemy "hollow_knight" --enemy-position FRONT

# Status tick at end of turn
python rules_engine.py status-tick --statuses "bleeding:2,rotting:3" --hp 14

# Death's Door check
python rules_engine.py death-check --hp 3 --max-hp 24

# Turn order
python rules_engine.py turn-order --player-dex 14 --enemy-dex 8
```

**All outputs are JSON. Always.**

**Key design rules:**

- Pure Python, `random` module — deterministic given a seed, testable in isolation
- Reads enemy and item stats from flat JSON config files co-located with the script
- Expand by adding subcommands — never by modifying agent prompts
- Test entirely without Claude: pipe params in, verify JSON out

**Future expansion:**

```bash
python rules_engine.py craft --recipe "iron_shard+ember_core"
python rules_engine.py reputation --faction "ashen_order" --delta -5
python rules_engine.py unlock --room "blinded_sanctum" --item "iron_key"
```

---

## 🏆 Gamification Layer

|System|Implementation|
|---|---|
|**Permadeath**|HP = 0 → write `graveyard.md`, reset `state.md`, keep `world-log.md` and `world.json` visited flags|
|**Death's Door**|At ≤25% HP every hit triggers `death-check` — roll 1 on 1d6 = instant death|
|**Position tactics**|FRONT/BACK slot changes what actions deal full damage — every turn is a decision|
|**Fog of war**|`world.json` visited flags — `/dungeon-map` only shows discovered rooms|
|**Echoes**|Dead characters become NPC shades — Echo agent reads `graveyard.md` for voice|
|**Stamina economy**|Every action costs stamina — Exhaustion halves damage and defense|
|**Mana scarcity**|Mana never fully recovers — Sorcerer burns bright and fades fast|
|**Run counter**|`Runs` field in `state.md` — the world remembers every life you've lived|

---

## 🚀 MVP Build Order

Build in this sequence — each phase is independently playable before the next begins.

**Phase 1 — Skeleton**

- [ ] `rules_engine.py` — `attack`, `check`, `death-check`, `status-tick`, `turn-order` subcommands
- [ ] `world.json` — all 6 rooms defined with full schema
- [ ] `state.md` schema with position field
- [ ] `/dungeon new` — character creation, writes state.md, opens at sunken_gate
- [ ] Rules agent — calls `rules_engine.py`, forwards JSON to DM
- [ ] DM agent — narration, reads `world.json` description seeds, never invents topology
- [ ] One enemy: Hollow Knight in corridor_of_order
- [ ] Permadeath → write to `graveyard.md`

**Phase 2 — Skill & Map**

- [ ] Full `ashen-realm` skill folder structure
- [ ] Progressive loading wired and tested
- [ ] `sample-turn.md` written and validated
- [ ] `/dungeon-map` command reading `world.json` visited flags

**Phase 3 — NPC & Exploration**

- [ ] `npc.md` with `context: fork`
- [ ] Blind Merchant in forgotten_chapel
- [ ] Iron Key drop in vestibule_of_ash, unlock logic via `rules_engine.py`
- [ ] `loot` and `rest` subcommands in `rules_engine.py`

**Phase 4 — Expansion**

- [ ] Echo agent (dead characters as shades)
- [ ] Full bestiary: Rotting Hound, Ashen Sentinel, Boss
- [ ] Reputation system in `state.md`
- [ ] Merchant trading flow + `economy.md`