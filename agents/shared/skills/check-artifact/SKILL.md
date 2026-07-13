---
name: check-artifact
description: Render a requested result or current work product as one self-contained local HTML file and open it in the best available terminal or browser preview. Use when the user says check, preview, render, 看一下, or wants a visual inspection artifact rather than a prose answer.
---

# Check artifact

1. Determine the content from the user's request and current task context. If no target is given, use the most relevant result produced in the current task.
2. Create exactly one UTF-8 HTML file at `.check/<short-kebab-slug>.html` under the current project.
3. Make it self-contained: inline CSS and JavaScript, no CDN or network resources, responsive and print-friendly. Do not modify source artifacts merely to preview them.
4. Inspect the generated HTML for broken markup and obvious overflow. For important visual work, render a screenshot and inspect it before reporting success.
5. Open it with:

   ```bash
   SKILL_DIR="${CHECK_ARTIFACT_SKILL_DIR:-$HOME/.agents/skills/check-artifact}"
   bash "$SKILL_DIR/scripts/open-render.sh" "$PWD/.check/<short-kebab-slug>.html"
   ```

6. Report the absolute path and the surface printed by the dispatcher. Revise the same file on follow-up requests.

Never claim the preview opened unless the dispatcher succeeds. Keep `.check/` as disposable project-local output.
