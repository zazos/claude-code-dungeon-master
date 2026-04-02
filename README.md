# Ashen Realm

A grimdark terminal RPG built entirely inside Claude Code. Death is permanent. The world does not care if you live.

Built to explore Claude Code's agentic primitives: commands, subagents, skills, and a Python rules engine that handles all game arithmetic so Claude never computes a number directly.

---

## How it works

```
/dungeon new  →  DM agent narrates  →  Rules agent calls rules_engine.py  →  JSON back to DM
```

Three agents. One Python engine. Structured files for state.

| Layer | What it does |
|---|---|
| `.claude/commands/` | Entry points — `/dungeon`, `/dungeon-combat`, `/dungeon-map` |
| `.claude/agents/` | DM (narration), Rules (JSON only), NPC (forked context) |
| `.claude/skills/ashen-realm/` | Progressive-load rulebook — only what's needed per turn |
| `rules_engine.py` | All dice, damage, procs, death checks — pure Python, testable in isolation |
| `game/` | Persistent state files — append-only logs survive every death |

---

## Stack

- **Claude Code** (Sonnet 4.6 recommended)
- Python 3 — no dependencies beyond stdlib
- Markdown state files, JSON world graph

---

## Run it

```bash
cd AI-Dungeon-Master
claude
/dungeon new
```

---

## What I was learning

- Structuring multi-agent pipelines with commands, agents, and skills in Claude Code
- Separating concerns across agents (narrator vs. rules interpreter vs. NPC voice)
- Keeping a language model out of the math layer entirely via an external engine
- Progressive skill loading to manage context window cost
