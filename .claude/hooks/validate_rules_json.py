#!/usr/bin/env python3
"""PostToolUse hook — validates rules_engine.py output is valid JSON.

The rules engine is the only place math happens. If it returns
invalid JSON, the DM agent will try to parse garbage and either
crash or invent numbers — both break the game silently.

This hook catches that failure at the boundary and injects a
warning into Claude's context before it can act on bad output.
Does not block — surfaces the failure for Claude to handle.
"""

import json
import sys

data = json.load(sys.stdin)

if data.get("tool_name") != "Bash":
    sys.exit(0)

command = data.get("tool_input", {}).get("command", "")
if "rules_engine.py" not in command:
    sys.exit(0)

output = data.get("tool_response", {}).get("output", "").strip()

try:
    json.loads(output)
    sys.exit(0)
except (json.JSONDecodeError, ValueError):
    print(json.dumps({
        "additionalContext": (
            "WARNING: rules_engine.py returned invalid JSON.\n"
            f"Command: {command}\n"
            f"Output: {output}\n"
            "Do not use this result. Re-run the command or surface the error to the player."
        )
    }))
    sys.exit(0)
