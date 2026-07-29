---
name: code-griller
description: Perform a read-only, severity-ranked static critique of Python, C, C++, Rust, Go, JavaScript, TypeScript, and shell code. Use for PR review, active-file grilling, architecture vetting, edge-case analysis, complexity risk, resource ownership, unsafe APIs, missing error handling, or test-gap detection.
---

# Code Griller

1. Resolve explicit targets inside the active workspace.
2. Run:

   ```text
   python3 grill.py --root WORKSPACE TARGET
   ```

3. Verify blocker and high findings against source context.
4. Report severity, category, `path:line`, evidence, impact, and remediation.
5. Separate proven defects from potential static risks.

Never import, compile, or execute reviewed source. Ignore generated dependencies,
secret-bearing files, binaries, symlinks, and oversized inputs. Do not modify
code unless the user separately requests fixes.
