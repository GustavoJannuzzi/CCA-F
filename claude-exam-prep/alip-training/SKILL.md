---
author: m.murphy@accenture.com
name: alip-training
description: "Claude Certified Architect — Exam Prep. Interactive training course with tabbed HTML slides, scenario-based practice problems, and an AI tutor."
argument-hint: "'claude-exam-prep' to start training"
allowed-tools: ["Read", "Bash", "Grep", "Glob", "ask_user_input"]
---

# Claude Exam Prep — Interactive Training

## Immediate Execution on Load

As soon as this skill is loaded — whether via slash command, zip upload, or any other mechanism — immediately open the course. Do NOT summarize the skill or ask what the user wants. Execute the steps below as your first action.

## Take the Course

1. Detect the runtime environment:
   ```bash
   if [ -d "/mnt/skills" ]; then echo "claudeai"; else echo "claudecode"; fi
   ```

   **If claude.ai** — copy to outputs then call `present_files`:
   ```bash
   cp courses/claude-exam-prep/index.html /mnt/user-data/outputs/index.html
   ```
   Then call `present_files(["/mnt/user-data/outputs/index.html"])`
   Present once. The user navigates modules via tabs.
   Do NOT use `show_widget` — only `present_files` renders in the right panel.

   **If Claude Code CLI** — open in external browser:
   ```bash
   PLATFORM=$(if grep -qi microsoft /proc/version 2>/dev/null; then echo "wsl"; elif [[ "$OSTYPE" == "darwin"* ]]; then echo "macos"; else echo "linux"; fi)
   FILEPATH="$HOME/.claude/skills/alip-training/courses/claude-exam-prep/index.html"
   case $PLATFORM in
     wsl) powershell.exe -Command "Start-Process '$(wslpath -w $FILEPATH)'" ;;
     macos) open "$FILEPATH" ;;
     linux) xdg-open "$FILEPATH" ;;
   esac
   ```

2. Check `~/.alip-training.md` for prior progress on this course. Offer to resume.

3. Follow the interactive tutor flow:
   - Read module MD files from `courses/claude-exam-prep/`
   - Present concepts with executive context first
   - Remind the user to review the module slides in the HTML viewer
   - Present ONE problem at a time, wait for answer, give feedback
   - Track scores per module and overall
   - Use `ask_user_input` for all interactions (see below)

## Interactive Menus (ask_user_input)

Use `ask_user_input` with `single_select` for ALL interactions:

**Practice problems**: Show question + options as text, then:
- `question`: `"Your answer?"`
- `type`: `"single_select"`
- `options`: `["A", "B", "C", "D"]`

**After concepts**: options `["I have a question", "Ready for problems"]`
**After each problem**: options `["I have a question", "Next problem"]`
**Between modules**: options `["Next module", "Review this module", "Stop here"]`
**After all modules**: options `["Review weak areas", "Done"]`

## Progress Tracking

Store in `~/.alip-training.md` under `## claude-exam-prep`. Create the file if it doesn't exist.

## Tutor Rules
- NEVER show the answer before the user responds
- ALWAYS pause after concepts and ASK if questions before problems
- ALWAYS pause after each problem and ASK if questions before next
- Present ONE question at a time
- Track score per module and overall
- Encourage but direct; practical framing ("in production, this means...")
- After wrong answers, give a memorable one-liner
