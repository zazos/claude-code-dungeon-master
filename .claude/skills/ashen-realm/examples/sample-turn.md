# Sample Turn — Canonical Format

This file anchors the output format for Ashen Realm turns. Claude should match this structure.

---

## Example 1: Spell Attack from Back Row

**Player input:** I move to the back and cast Ashen Bolt at the hollow knight.

**Rules agent interpretation:**
- Step 1: Position switch FRONT → BACK (1 stamina)
- Step 2: Spell attack

**Rules agent call:**
```bash
python rules_engine.py attack --type spell --spr 18 --spell "ashen_bolt" \
  --player-position BACK --enemy "hollow_knight" --enemy-position FRONT \
  --enemy-hp 20
```

**Rules agent output:**
```json
{
  "roll": 15,
  "attack_total": 18,
  "defense": 10,
  "outcome": "hit",
  "damage": 11,
  "enemy_hp_remaining": 9,
  "enemy_dead": false,
  "stamina_cost": 2,
  "mana_cost": 1,
  "position_penalty": false
}
```

**DM narration:**
The bolt tears through the corridor. The knight staggers, one gauntlet raised too late. From the back you are harder to reach — but the mana it cost leaves a hollow feeling.

[HP: 14/14 | Stamina: 2/5 | Mana: 4/6 | Position: BACK | Room: Corridor of the Ashen Order]

---

## Example 2: Melee Attack with Proc

**Player input:** I swing my iron sword at the hollow knight.

**Rules agent call:**
```bash
python rules_engine.py attack --type melee --str 16 --weapon "iron_sword" \
  --player-position FRONT --enemy "hollow_knight" --enemy-position FRONT \
  --enemy-hp 20
```

**Rules agent output:**
```json
{
  "roll": 18,
  "attack_total": 21,
  "defense": 12,
  "outcome": "crit",
  "damage": 18,
  "enemy_hp_remaining": 2,
  "enemy_dead": false,
  "stamina_cost": 2,
  "position_penalty": false,
  "proc_triggered": "bleeding"
}
```

**DM narration:**
The blade finds the gap between pauldron and gorget. Blood — thick, dark, wrong — spills down rusted plate. The knight does not scream. It bleeds.

[HP: 24/24 | Stamina: 4/6 | Mana: —/— | Position: FRONT | Room: Corridor of the Ashen Order]

---

## Example 3: Enemy Turn

**Rules agent call:**
```bash
python rules_engine.py enemy-attack --enemy "hollow_knight" --enemy-position FRONT \
  --player-position FRONT --player-hp 24 --player-str 16 --player-dex 10 --player-spr 6
```

**Rules agent output:**
```json
{
  "move_used": "Shield Bash",
  "roll": 14,
  "attack_total": 16,
  "defense": 13,
  "outcome": "hit",
  "damage": 7,
  "position_penalty": false,
  "player_hp_remaining": 17,
  "player_dead": false,
  "proc_triggered": "staggered"
}
```

**DM narration:**
The shield catches you across the jaw. Your vision splits. For a moment there are two knights. Both want you dead. You stagger.

[HP: 17/24 | Stamina: 4/6 | Mana: —/— | Position: FRONT | Status: Staggered (1 turn) | Room: Corridor of the Ashen Order]

---

## Example 4: Death

**Rules agent output (death-check):**
```json
{
  "triggered": true,
  "roll": 1,
  "dead": true,
  "hp": 4,
  "threshold_hp": 6
}
```

**DM narration:**
The blade finds you again. Your knees fold. The stone is cold against your cheek. You had thought there would be more time.

**Graveyard entry:**
```
### Aldric the Burnt — Warrior
Cause of death: Hollow Knight, overhead cleave, Corridor of the Ashen Order
Position at death: FRONT | HP: 0/24 | Gold lost: 45
Epitaph: He thought the shield would hold.
```

The ash takes another. `/dungeon new` to try again.

---

## Format Rules

1. DM narration is always **max 3 sentences**
2. Status bar appears after every turn in brackets
3. Status bar format: `[HP: cur/max | Stamina: cur/max | Mana: cur/max | Position: X | Room: Name]`
4. Add `Status: effect (N turns)` to bar when active
5. Never show the JSON to the player — only the narration and status bar
6. Never copy `description_seed` verbatim
