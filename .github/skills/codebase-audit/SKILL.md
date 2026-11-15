---
name: codebase-audit
description: Audit a repository's implemented architecture, workflows, tests, and gaps using evidence from the current worktree without changing files.
---

# Codebase Audit

Use this skill when asked to assess an existing repository, implementation, or
documentation baseline.

## Workflow

1. Inspect `git status`, the current branch and commit, and available local
   history. Clearly separate committed state from uncommitted changes.
2. Inventory tracked source, configuration, tests, dependencies, data
   manifests, generated contracts, and existing documentation. Exclude
   generated dependency/build trees and local databases from claims about
   tracked source.
3. Trace the main data flow through implementation files and tests. Verify
   whether an apparent feature is wired and exercised; do not infer completion
   from filenames or README claims alone.
4. Run relevant existing tests/builds when appropriate. Report the exact
   commands and results, including warnings or limitations.
5. Link technical findings to their repository evidence. Label verified facts,
   inferences, and unanswered questions separately.
6. Report implemented behavior, incomplete behavior, source-of-truth files,
   development workflow, architectural decisions supported by code, and
   missing team decisions.
7. If asked only to audit or propose, do not modify files. If implementation is
   separately approved, preserve existing worktree changes and limit edits to
   the approved scope.

## Report checks

- Distinguish current worktree behavior from the current commit.
- Do not treat a local ignored database or test fixture as production data.
- Do not repeat stale documentation counts as current validation.
- Do not invent requirements, architecture decisions, or scientific claims.
- State when a requested blueprint, specification, or history is not present.
