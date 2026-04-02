#!/usr/bin/env python3
"""PreToolUse hook — blocks overwriting append-only game files.

graveyard.md and world-log.md are append-only by design.
If Claude tries to Write (overwrite) either file instead of
Edit (append), this hook blocks the call entirely.
"""

import json
import os
import sys

APPEND_ONLY = {"graveyard.md", "world-log.md"}

try:
    data = json.load(sys.stdin)
except json.JSONDecodeError:
    sys.exit(0)  # Can't parse input — don't block

if data.get("tool_name") != "Write":
    sys.exit(0)

file_path = data.get("tool_input", {}).get("file_path", "")

if not any(file_path.endswith(f) for f in APPEND_ONLY):
    sys.exit(0)

new_content = data.get("tool_input", {}).get("content", "")

if os.path.exists(file_path):
    with open(file_path) as f:
        existing = f.read()
    if not new_content.startswith(existing):
        filename = os.path.basename(file_path)
        print(json.dumps({
            "hookSpecificOutput": {
                "permissionDecision": "deny",
                "permissionDecisionReason": (
                    f"BLOCKED: {filename} is append-only. "
                    "Use Edit to append new content — never Write to overwrite."
                )
            }
        }))
        sys.exit(2)

sys.exit(0)
