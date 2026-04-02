#!/usr/bin/env python3
"""Ashen Realm — Rules Engine

All game arithmetic lives here. Claude never computes numbers.
Called via: python rules_engine.py <subcommand> [--params]
Output is always JSON.
"""

import argparse
import json
import math
import os
import random
import sys

# ---------------------------------------------------------------------------
# Config loading
# ---------------------------------------------------------------------------

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

def load_config(name: str) -> dict:
    path = os.path.join(SCRIPT_DIR, "data", f"{name}.json")
    with open(path) as f:
        return json.load(f)

def get_enemy(enemy_id: str) -> dict:
    bestiary = load_config("bestiary")
    if enemy_id not in bestiary:
        error_exit(f"Unknown enemy: {enemy_id}")
    return bestiary[enemy_id]

def get_weapon(weapon_id: str) -> dict:
    items = load_config("items")
    if weapon_id not in items:
        error_exit(f"Unknown item: {weapon_id}")
    return items[weapon_id]

def get_spell(spell_id: str) -> dict:
    spells = load_config("spells")
    if spell_id not in spells:
        error_exit(f"Unknown spell: {spell_id}")
    return spells[spell_id]

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def modifier(stat: int) -> int:
    """floor(stat / 5)"""
    return stat // 5

def roll_d(sides: int) -> int:
    return random.randint(1, sides)

def output(data: dict):
    print(json.dumps(data))
    sys.exit(0)

def error_exit(msg: str):
    print(json.dumps({"error": msg}))
    sys.exit(1)

# ---------------------------------------------------------------------------
# Subcommands
# ---------------------------------------------------------------------------

def cmd_attack(args):
    """Unified attack resolution: melee, ranged, or spell."""
    enemy = get_enemy(args.enemy)

    # Determine bonus and defense stats
    if args.type == "melee":
        atk_mod = modifier(args.str_stat)
        def_mod = modifier(enemy.get("str", 10))
        weapon = get_weapon(args.weapon)
        base_damage = weapon["base_atk"]
        stamina_cost = 2
        proc_type = weapon.get("proc", None)
        proc_chance = weapon.get("proc_chance", 0)
    elif args.type == "ranged":
        atk_mod = modifier(args.dex)
        def_mod = modifier(enemy.get("dex", 10))
        weapon = get_weapon(args.weapon)
        base_damage = weapon["base_atk"]
        stamina_cost = 1
        proc_type = weapon.get("proc", None)
        proc_chance = weapon.get("proc_chance", 0)
    elif args.type == "spell":
        atk_mod = modifier(args.spr)
        def_mod = modifier(enemy.get("spr", 6))
        spell = get_spell(args.spell)
        base_damage = spell["base_damage"]
        stamina_cost = spell.get("stamina_cost", 2)
        proc_type = spell.get("proc", None)
        proc_chance = spell.get("proc_chance", 0)
    else:
        error_exit(f"Unknown attack type: {args.type}")

    # Roll
    d20 = roll_d(20)
    attack_roll = d20 + atk_mod
    defense = 10 + def_mod  # base 10 + modifier
    diff = attack_roll - defense

    # Damage variance
    d6 = roll_d(6)

    # Position penalty: melee from BACK = half damage
    position_penalty = False
    if args.type == "melee" and args.player_position == "BACK":
        position_penalty = True

    # Hit resolution
    if diff < -4:
        # Full miss
        result = {
            "roll": d20,
            "attack_total": attack_roll,
            "defense": defense,
            "outcome": "miss",
            "damage": 0,
            "stamina_cost": 0,
            "position_penalty": position_penalty,
        }
    elif diff < 0:
        # Graze: quarter damage, half stamina
        raw_damage = base_damage + atk_mod + d6
        damage = max(1, raw_damage // 4)
        if position_penalty:
            damage = max(1, damage // 2)
        # Check weakness
        if args.type == "spell" and enemy.get("weakness") == "spr":
            damage += 4
        result = {
            "roll": d20,
            "attack_total": attack_roll,
            "defense": defense,
            "outcome": "graze",
            "damage": damage,
            "stamina_cost": max(1, stamina_cost // 2),
            "position_penalty": position_penalty,
        }
    else:
        is_crit = diff >= 5
        raw_damage = base_damage + atk_mod + d6
        if position_penalty:
            raw_damage = max(1, raw_damage // 2)
        # Check weakness
        if args.type == "spell" and enemy.get("weakness") == "spr":
            raw_damage += 4
        damage = raw_damage * 2 if is_crit else raw_damage

        # Proc check
        proc_triggered = False
        proc_name = None
        effective_proc_chance = proc_chance * 2 if is_crit else proc_chance
        if proc_type and random.random() < effective_proc_chance:
            proc_triggered = True
            proc_name = proc_type

        result = {
            "roll": d20,
            "attack_total": attack_roll,
            "defense": defense,
            "outcome": "crit" if is_crit else "hit",
            "damage": damage,
            "stamina_cost": stamina_cost,
            "position_penalty": position_penalty,
        }
        if proc_triggered:
            result["proc_triggered"] = proc_name

    # Enemy HP
    enemy_hp = args.enemy_hp if args.enemy_hp is not None else enemy["hp"]
    enemy_hp_remaining = max(0, enemy_hp - result["damage"])
    result["enemy_hp_remaining"] = enemy_hp_remaining
    result["enemy_dead"] = enemy_hp_remaining == 0

    # Mana cost for spells
    if args.type == "spell":
        spell = get_spell(args.spell)
        result["mana_cost"] = spell["mana_cost"]

    output(result)


def cmd_enemy_attack(args):
    """Enemy attacks the player."""
    enemy = get_enemy(args.enemy)
    moves = enemy.get("moves", [])

    # Pick a move (random or specified)
    if args.move:
        move = next((m for m in moves if m["name"] == args.move), None)
        if not move:
            error_exit(f"Unknown move: {args.move}")
    else:
        move = random.choice(moves)

    # Determine attack type from move
    atk_type = move.get("type", "melee")

    if atk_type == "melee":
        atk_mod = modifier(enemy.get("str", 10))
        def_mod = modifier(args.player_str) if args.player_str else 0
    elif atk_type == "ranged":
        atk_mod = modifier(enemy.get("dex", 10))
        def_mod = modifier(args.player_dex) if args.player_dex else 0
    elif atk_type == "spell":
        atk_mod = modifier(enemy.get("spr", 6))
        def_mod = modifier(args.player_spr) if args.player_spr else 0
    else:
        atk_mod = modifier(enemy.get("str", 10))
        def_mod = 0

    d20 = roll_d(20)
    attack_roll = d20 + atk_mod
    defense = 10 + def_mod
    diff = attack_roll - defense

    d6 = roll_d(6)
    base_damage = move.get("base_damage", 4)

    # Position penalty: melee vs BACK player = half damage
    position_penalty = False
    if atk_type == "melee" and args.player_position == "BACK":
        position_penalty = True

    # Exhaustion: halve defense
    if args.exhausted:
        defense = max(1, defense // 2)
        diff = attack_roll - defense

    if diff < -4:
        damage = 0
        outcome = "miss"
    elif diff < 0:
        raw = base_damage + atk_mod + d6
        damage = max(1, raw // 4)
        if position_penalty:
            damage = max(1, damage // 2)
        outcome = "graze"
    else:
        is_crit = diff >= 5
        raw = base_damage + atk_mod + d6
        if position_penalty:
            raw = max(1, raw // 2)
        damage = raw * 2 if is_crit else raw
        outcome = "crit" if is_crit else "hit"

    # Proc from move
    proc_triggered = False
    proc_name = None
    if outcome in ("hit", "crit") and move.get("proc"):
        chance = move.get("proc_chance", 0.3)
        if outcome == "crit":
            chance *= 2
        if random.random() < chance:
            proc_triggered = True
            proc_name = move["proc"]

    player_hp_remaining = max(0, args.player_hp - damage)

    result = {
        "move_used": move["name"],
        "roll": d20,
        "attack_total": attack_roll,
        "defense": defense,
        "outcome": outcome,
        "damage": damage,
        "position_penalty": position_penalty,
        "player_hp_remaining": player_hp_remaining,
        "player_dead": player_hp_remaining == 0,
    }
    if proc_triggered:
        result["proc_triggered"] = proc_name

    output(result)


def cmd_dodge(args):
    """Contested DEX roll to avoid an incoming attack."""
    player_roll = roll_d(20) + modifier(args.player_dex)
    enemy = get_enemy(args.enemy)
    enemy_roll = roll_d(20) + modifier(enemy.get("dex", 10))

    success = player_roll >= enemy_roll
    output({
        "player_roll": player_roll,
        "enemy_roll": enemy_roll,
        "success": success,
        "stamina_cost": 1,
    })


def cmd_flee(args):
    """Contested DEX to escape combat."""
    player_roll = roll_d(20) + modifier(args.player_dex)
    enemy = get_enemy(args.enemy)
    enemy_roll = roll_d(20) + modifier(enemy.get("dex", 10))

    success = player_roll > enemy_roll
    output({
        "player_roll": player_roll,
        "enemy_roll": enemy_roll,
        "success": success,
        "stamina_cost": 2,
    })


def cmd_check(args):
    """Generic d20 skill check vs a stat threshold."""
    d20 = roll_d(20)
    total = d20 + modifier(args.stat)
    success = total >= args.dc
    output({
        "roll": d20,
        "total": total,
        "dc": args.dc,
        "success": success,
    })


def cmd_loot(args):
    """Random drop from enemy loot table."""
    enemy = get_enemy(args.enemy)
    loot_table = enemy.get("loot", {})

    # Gold
    gold_formula = loot_table.get("gold", "0")
    # Parse "1d6 × 10" style
    if "d" in gold_formula:
        parts = gold_formula.replace("×", "*").replace("x", "*").split("*")
        dice_part = parts[0].strip()
        multiplier = int(parts[1].strip()) if len(parts) > 1 else 1
        count, sides = dice_part.split("d")
        count = int(count) if count else 1
        gold = sum(roll_d(int(sides)) for _ in range(count)) * multiplier
    else:
        gold = int(gold_formula)

    # Item drops
    drops = []
    for item in loot_table.get("items", []):
        if random.random() < item["chance"]:
            drops.append(item["id"])

    output({
        "gold": gold,
        "items": drops,
    })


def cmd_rest(args):
    """Partial HP/stamina/mana recovery from resources."""
    hp_recovery = min(args.max_hp - args.hp, max(1, args.max_hp // 4))
    stamina_recovery = min(args.max_stamina - args.stamina, max(1, args.max_stamina // 2))

    new_hp = args.hp + hp_recovery
    new_stamina = args.stamina + stamina_recovery

    result = {
        "hp": new_hp,
        "hp_recovered": hp_recovery,
        "stamina": new_stamina,
        "stamina_recovered": stamina_recovery,
        "ember_flasks_remaining": args.ember_flasks - 1,
    }

    if args.max_mana and args.max_mana > 0:
        mana_recovery = min(args.max_mana - args.mana, max(1, args.max_mana // 3))
        result["mana"] = args.mana + mana_recovery
        result["mana_recovered"] = mana_recovery

    output(result)


def cmd_status_tick(args):
    """Tick active status durations, apply per-turn damage."""
    statuses = []
    hp = args.hp

    if not args.statuses or args.statuses == "none":
        output({"statuses": [], "hp": hp, "damage_taken": 0})
        return

    damage_taken = 0
    for entry in args.statuses.split(","):
        parts = entry.strip().split(":")
        name = parts[0]
        remaining = int(parts[1]) - 1

        # Per-turn effects
        if name == "bleeding":
            hp -= 2
            damage_taken += 2
        elif name == "rotting":
            hp -= 1
            damage_taken += 1

        if remaining > 0:
            statuses.append({"name": name, "turns_remaining": remaining})

    hp = max(0, hp)
    output({
        "statuses": statuses,
        "hp": hp,
        "damage_taken": damage_taken,
        "player_dead": hp == 0,
    })


def cmd_death_check(args):
    """Death's Door: 1d6 when HP <= 25% max. Roll 1 = instant death."""
    threshold = args.max_hp * 0.25
    # Check for Doomed status (raises threshold to 50%)
    if args.doomed:
        threshold = args.max_hp * 0.50

    if args.hp > threshold:
        output({"triggered": False, "dead": False, "hp": args.hp})
        return

    roll = roll_d(6)
    dead = roll == 1
    output({
        "triggered": True,
        "roll": roll,
        "dead": dead,
        "hp": args.hp,
        "threshold_hp": int(threshold),
    })


def cmd_turn_order(args):
    """Compare DEX values, return who acts first. Ties broken by coin flip."""
    if args.player_dex > args.enemy_dex:
        first = "player"
    elif args.enemy_dex > args.player_dex:
        first = "enemy"
    else:
        first = "player" if roll_d(2) == 1 else "enemy"

    output({
        "first": first,
        "player_dex": args.player_dex,
        "enemy_dex": args.enemy_dex,
    })


def cmd_unlock(args):
    """Check if player has the required key to unlock a room."""
    rooms = load_config("../world")  # world.json is at project root
    # Actually, let's load world.json directly
    world_path = os.path.join(SCRIPT_DIR, "world.json")
    with open(world_path) as f:
        world = json.load(f)

    room = world["rooms"].get(args.room)
    if not room:
        error_exit(f"Unknown room: {args.room}")

    if not room["locked"]:
        output({"already_unlocked": True, "success": True})
        return

    required = room.get("lock_requires")
    has_key = args.item == required

    output({
        "already_unlocked": False,
        "required_item": required,
        "has_item": has_key,
        "success": has_key,
    })


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Ashen Realm Rules Engine")
    sub = parser.add_subparsers(dest="command")

    # --- attack ---
    p_atk = sub.add_parser("attack")
    p_atk.add_argument("--type", required=True, choices=["melee", "ranged", "spell"])
    p_atk.add_argument("--str", dest="str_stat", type=int, default=10)
    p_atk.add_argument("--dex", type=int, default=10)
    p_atk.add_argument("--spr", type=int, default=6)
    p_atk.add_argument("--weapon", default=None)
    p_atk.add_argument("--spell", default=None)
    p_atk.add_argument("--player-position", default="FRONT")
    p_atk.add_argument("--enemy", required=True)
    p_atk.add_argument("--enemy-position", default="FRONT")
    p_atk.add_argument("--enemy-hp", type=int, default=None)

    # --- enemy-attack ---
    p_eatk = sub.add_parser("enemy-attack")
    p_eatk.add_argument("--enemy", required=True)
    p_eatk.add_argument("--enemy-position", default="FRONT")
    p_eatk.add_argument("--move", default=None)
    p_eatk.add_argument("--player-position", default="FRONT")
    p_eatk.add_argument("--player-hp", type=int, required=True)
    p_eatk.add_argument("--player-str", type=int, default=10)
    p_eatk.add_argument("--player-dex", type=int, default=10)
    p_eatk.add_argument("--player-spr", type=int, default=6)
    p_eatk.add_argument("--exhausted", action="store_true")

    # --- dodge ---
    p_dodge = sub.add_parser("dodge")
    p_dodge.add_argument("--player-dex", type=int, required=True)
    p_dodge.add_argument("--enemy", required=True)

    # --- flee ---
    p_flee = sub.add_parser("flee")
    p_flee.add_argument("--player-dex", type=int, required=True)
    p_flee.add_argument("--enemy", required=True)

    # --- check ---
    p_check = sub.add_parser("check")
    p_check.add_argument("--stat", type=int, required=True)
    p_check.add_argument("--dc", type=int, required=True)

    # --- loot ---
    p_loot = sub.add_parser("loot")
    p_loot.add_argument("--enemy", required=True)

    # --- rest ---
    p_rest = sub.add_parser("rest")
    p_rest.add_argument("--hp", type=int, required=True)
    p_rest.add_argument("--max-hp", type=int, required=True)
    p_rest.add_argument("--stamina", type=int, required=True)
    p_rest.add_argument("--max-stamina", type=int, required=True)
    p_rest.add_argument("--mana", type=int, default=0)
    p_rest.add_argument("--max-mana", type=int, default=0)
    p_rest.add_argument("--ember-flasks", type=int, required=True)

    # --- status-tick ---
    p_tick = sub.add_parser("status-tick")
    p_tick.add_argument("--statuses", required=True)
    p_tick.add_argument("--hp", type=int, required=True)

    # --- death-check ---
    p_death = sub.add_parser("death-check")
    p_death.add_argument("--hp", type=int, required=True)
    p_death.add_argument("--max-hp", type=int, required=True)
    p_death.add_argument("--doomed", action="store_true")

    # --- turn-order ---
    p_turn = sub.add_parser("turn-order")
    p_turn.add_argument("--player-dex", type=int, required=True)
    p_turn.add_argument("--enemy-dex", type=int, required=True)

    # --- unlock ---
    p_unlock = sub.add_parser("unlock")
    p_unlock.add_argument("--room", required=True)
    p_unlock.add_argument("--item", required=True)

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    dispatch = {
        "attack": cmd_attack,
        "enemy-attack": cmd_enemy_attack,
        "dodge": cmd_dodge,
        "flee": cmd_flee,
        "check": cmd_check,
        "loot": cmd_loot,
        "rest": cmd_rest,
        "status-tick": cmd_status_tick,
        "death-check": cmd_death_check,
        "turn-order": cmd_turn_order,
        "unlock": cmd_unlock,
    }

    dispatch[args.command](args)


if __name__ == "__main__":
    main()
