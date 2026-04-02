#!/usr/bin/env python3
"""PostToolUse hook — snapshots game/state.md after every write.

Implements the /rewind concept from CLAUDE.md.
Every time state.md is written, a timestamped copy lands in
game/backups/ — giving a full history to roll back to if
something breaks mid-session.

Runs async so it never blocks the game loop.
"""

import json
import os
import shutil
import sys
from datetime import datetime

data = json.load(sys.stdin)

if data.get("tool_name") != "Write":
    sys.exit(0)

file_path = data.get("tool_input", {}).get("file_path", "")

if not file_path.endswith("game/state.md"):
    sys.exit(0)

if not os.path.exists(file_path):
    sys.exit(0)

backup_dir = os.path.join(os.path.dirname(file_path), "backups")
os.makedirs(backup_dir, exist_ok=True)

timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
dest = os.path.join(backup_dir, f"state-{timestamp}.md")
shutil.copy2(file_path, dest)

sys.exit(0)
