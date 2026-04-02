---
allowed-tools: Read, Write, Edit, Bash, Agent, Skill
description: Combat loop for Ashen Realm — handles fight resolution
user-facing: false
---

# /dungeon-combat — Combat Loop

Handles combat encounters in the Ashen Realm. Invoked by the DM when an enemy is encountered. Loops until resolved.

## Setup

1. Load the `ashen-realm` skill — specifically `references/combat.md` and `references/bestiary.md`
2. Read `game/state.md` for player stats, position, status effects
3. Identify the enemy from `world.json` → `contains.enemy`
4. Call `rules_engine.py turn-order` to determine who acts first

## Combat Round

Each round:

### 1. Turn Order
Call `rules_engine.py turn-order --player-dex <dex> --enemy-dex <dex>` to determine who acts first.

### 2. First Actor's Turn
If player goes first:
- Receive player input (attack, dodge, flee, switch position, use item)
- Call the **Rules agent** to interpret and execute via `rules_engine.py`
- Call the **DM agent** to narrate the result

If enemy goes first:
- Call `rules_engine.py enemy-attack` with enemy and player stats
- If hit, check if player HP ≤ 25% → call `rules_engine.py death-check`
- Call the **DM agent** to narrate the enemy's action

### 3. Second Actor's Turn
Same as above for the other combatant.

### 4. End of Round
- Call `rules_engine.py status-tick` for active statuses on the player
- Check for death conditions
- Print status bar
- If the enemy's move was "Retreat", switch enemy position to BACK

## Player Actions in Combat

| Action           | What happens                                                        |
|------------------|---------------------------------------------------------------------|
| Melee attack     | `rules_engine.py attack --type melee` — costs 2 stamina            |
| Ranged attack    | `rules_engine.py attack --type ranged` — costs 1 stamina           |
| Cast spell       | `rules_engine.py attack --type spell` — costs stamina + mana       |
| Dodge            | `rules_engine.py dodge` — costs 1 stamina, avoids next attack      |
| Switch position  | Change FRONT↔BACK — costs 1 stamina, uses the turn action          |
| Use item         | Apply item effect — costs 1 stamina                                |
| Flee             | `rules_engine.py flee` — costs 2 stamina, exits combat if success  |

## Exhaustion

When player stamina reaches 0:
- Player is **Exhausted**
- Attacks deal half damage
- Defense is halved
- Pass `--exhausted` flag on enemy attack calls

## Death's Door

After any hit that puts player HP ≤ 25% of max:
- Call `rules_engine.py death-check --hp <current> --max-hp <max>`
- Add `--doomed` flag if player has the Doomed status
- If `dead: true` → trigger death routine

## Resolution

Combat ends when one of these occurs:

### Enemy Dead
1. Call `rules_engine.py loot --enemy "<enemy_id>"`
2. Add loot to `game/inventory.md` and gold to `game/state.md`
3. Remove enemy from `world.json` → `contains.enemy` (set to `null`)
4. Append to `game/world-log.md`: `[Player] defeated [Enemy] in [Room]`
5. Return to the main turn loop

### Player Dead
1. DM narrates the death
2. Write death entry to `game/graveyard.md`
3. Increment `Runs` in `game/state.md`
4. Reset `game/state.md` to defaults
5. Append to `game/world-log.md`: `[Player] fell to [Enemy] in [Room]`
6. Return `PLAYER_DEAD` to caller

### Player Fled
1. Move player back to previous room
2. Append to `game/world-log.md`: `[Player] fled from [Enemy] in [Room]`
3. Enemy remains in the room (not removed from `world.json`)
4. Return to main turn loop

## Rules

- **Never compute arithmetic** — all math goes through `rules_engine.py`
- **Track positions** for both player and enemy every turn
- **One action per turn** — the player cannot attack and dodge in the same turn
- **Always run status-tick** at end of each round
- **Always check death-check** when HP drops to ≤ 25%
