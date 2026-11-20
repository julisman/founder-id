---
description: Stop the founder-id dashboard server (the projects stay registered and every founder/ file is untouched)
allowed-tools: Bash(python3:*)
---

!`python3 "${CLAUDE_PLUGIN_ROOT}/gui/serve.py" --stop`

Tell the user, in one line, what the output above says: the dashboard was stopped
(and on which address), or it was not running. Mention that
`/founder-id:founder-gui` starts it again and the projects are remembered.
