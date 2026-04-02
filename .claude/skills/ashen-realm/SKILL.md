---
name: ashen-realm
description: >
  Rulebook and lore bible for the Ashen Realm grimdark RPG.
  Always load SKILL.md.
  Load references/combat.md during combat only.
  Load references/bestiary.md when an enemy is encountered.
  Load references/items.md when looting or trading.
  Load references/classes.md during character creation only.
  Load examples/sample-turn.md when output format is uncertain.
---

# Ashen Realm — Game Reference

A grimdark terminal RPG. Death is permanent. The world does not care if you live.

## Core Principles

- **Consequence** — every action costs something, every death is permanent
- **Opacity** — the world does not explain itself, you discover it
- **Persistence** — the world remembers what you did, even after you die

## Attributes

| Attribute | Governs                   |
|-----------|---------------------------|
| **STR**   | Melee damage bonus        |
| **DEX**   | Stamina pool, turn order  |
| **HP**    | Hit points — zero = death |
| **SPR**   | Mana pool, spell damage   |

**Modifier:** `floor(stat / 5)` — STR 14 = +2, STR 8 = +1

## Key Mechanics

- **Stamina** — every action costs stamina. At 0: Exhausted (half damage, half defense)
- **Mana** — spells cost mana. Does not recover in combat. Partial recovery on rest.
- **Position** — FRONT or BACK. Affects what deals full damage.
- **Death's Door** — at ≤25% HP, every hit triggers a 1d6 check. Roll 1 = instant death.
- **Permadeath** — HP 0 = dead. Character goes to the graveyard. World persists.

## All arithmetic is handled by `rules_engine.py`

Claude never computes dice rolls, damage, modifiers, or stat checks. The Rules agent calls the Python script and forwards JSON results.

## Reference Loading

Load only what is needed per turn:

| File                        | Load when                     |
|-----------------------------|-------------------------------|
| `SKILL.md`                  | Always                        |
| `references/combat.md`     | Combat is active              |
| `references/bestiary.md`   | An enemy is encountered       |
| `references/items.md`      | Looting or trading            |
| `references/classes.md`    | Character creation only       |
| `examples/sample-turn.md`  | Output format is uncertain    |
