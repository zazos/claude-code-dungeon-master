# Combat Reference

## Action Types

| Action          | Type   | Stamina Cost | Notes                                    |
|-----------------|--------|-------------|------------------------------------------|
| Melee attack    | attack | 2           | Uses STR modifier                        |
| Ranged attack   | attack | 1           | Uses DEX modifier                        |
| Spell (tier 1)  | attack | 2           | Uses SPR modifier, costs 1 mana          |
| Spell (tier 2+) | attack | 3           | Uses SPR modifier, costs 2-3 mana        |
| Dodge           | dodge  | 1           | Contested DEX roll, avoids next attack   |
| Switch position | —      | 1           | FRONT↔BACK, uses the turn action         |
| Use item        | —      | 1           | Apply item effect                        |
| Flee            | flee   | 2           | Contested DEX, exits combat on success   |

## Unified Attack Resolution

```
Roll 1d20 + Action Bonus  vs  Target Defense (10 + defender modifier)
```

| Attack Type | Bonus Stat    | Defense Stat        |
|-------------|---------------|---------------------|
| Melee       | STR modifier  | Target STR modifier |
| Ranged      | DEX modifier  | Target DEX modifier |
| Spell       | SPR modifier  | Target SPR modifier |

## Hit Thresholds

| Result       | Outcome                                    |
|--------------|---------------------------------------------|
| Miss by 5+   | Full miss — no stamina cost                |
| Miss by 1–4  | Graze — quarter damage, half stamina cost  |
| Meet or beat | Hit — full damage                          |
| Beat by 5+   | Crit — double damage, proc chance doubled  |

## Damage Formula

```
Melee:  weapon_base + STR_mod + 1d6
Ranged: weapon_base + DEX_mod + 1d6
Spell:  spell_base  + SPR_mod + 1d6
```

## Position System

| Position | Can Use             | Takes                                    |
|----------|---------------------|------------------------------------------|
| FRONT    | Melee attacks       | Full melee damage, full ranged/spell     |
| BACK     | Ranged, spells      | Half melee damage, full ranged/spell     |

- Switching position costs 1 stamina and uses the turn action
- Melee from BACK is allowed but deals half damage
- `rules_engine.py` applies position penalties automatically

## Status Effects

| Status      | Trigger                    | Effect                                  | Duration |
|-------------|----------------------------|-----------------------------------------|----------|
| Bleeding    | Bladed weapons on crit     | −2 HP per turn                          | 3 turns  |
| Hollowed    | Curse attacks, dark magic  | SPR halved, spells cost double mana     | 2 turns  |
| Staggered   | Heavy blunt weapons        | Lose next turn entirely                 | 1 turn   |
| Frenzied    | Certain enemy attacks      | Must attack — cannot dodge or flee      | 2 turns  |
| Rotting     | Undead enemies, poison     | −1 HP per turn, healing halved          | 4 turns  |
| Doomed      | Rare boss mechanic         | Death's Door threshold raised to 50%    | Until cleansed |

- Statuses do not stack — second application refreshes duration
- Max 2 active statuses per character at once
- `rules_engine.py` tracks and ticks durations via `status-tick`

## Death's Door

When HP drops to ≤25% of max HP:
- Every incoming hit triggers a death check
- `rules_engine.py death-check` rolls 1d6
- Roll of 1 = instant death regardless of remaining HP
- Doomed status raises the threshold to 50%

## Stamina & Exhaustion

```
Stamina Pool = 4 + DEX modifier
```

At 0 stamina → **Exhausted**:
- Attacks deal half damage
- Defense halved
- Stamina recovers partially on rest, never fully in combat

## Mana

```
Mana Pool = 3 + SPR modifier
```

- Spells cost 1–3 mana by tier
- Mana does not recover in combat
- Partial recovery on rest only

## Turn Order

Highest DEX acts first. Ties broken by `rules_engine.py` coin flip.

## Parameters for rules_engine.py Calls

### attack
`--type`, `--str`/`--dex`/`--spr`, `--weapon`/`--spell`, `--player-position`, `--enemy`, `--enemy-position`, `--enemy-hp`

### enemy-attack
`--enemy`, `--enemy-position`, `--player-position`, `--player-hp`, `--player-str`, `--player-dex`, `--player-spr`, `--exhausted` (flag)

### dodge
`--player-dex`, `--enemy`

### flee
`--player-dex`, `--enemy`

### status-tick
`--statuses` (format: `name:turns,name:turns`), `--hp`

### death-check
`--hp`, `--max-hp`, `--doomed` (flag)

### turn-order
`--player-dex`, `--enemy-dex`
