---
name: mem-leak-auditor
description: Compile explicit C sources with strict warnings and execute the resulting local binary under bounded Valgrind leak and memory-error analysis. Use for C heap leaks, invalid access, uninitialized reads, ownership failures, allocator imbalance, or cleanup verification.
---

# Memory Leak Auditor

1. Confirm every target is explicit, trusted C source inside the workspace.
2. Resolve the skill directory as the directory containing this file.
3. Run:

   ```text
   python3 audit_memory.py --root WORKSPACE SOURCE
   ```

4. Add include directories, defines, libraries, program arguments, or an input
   file only through their dedicated options.
5. Report compiler diagnostics, Valgrind error counts, leak-kind totals, and
   loss-record stack locations.

The wrapper uses a temporary build directory, direct argument vectors, timeouts,
and process-group termination. It is not a sandbox: compiled code can access the
user's files and network. Do not run unfamiliar or externally supplied source
without explicit authorization. Never report a precise leak location when debug
evidence is unavailable.
