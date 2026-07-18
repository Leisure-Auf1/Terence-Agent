# Phase C.3 — Human Interface Layer

**Status:** C.3 — Design Complete · 🟢
**Date:** 2026-07-18

## CLI Command Interface

| Command | Function | Kernel Path |
|:-----|:-----|:-----|
| `hermes run <intent>` | Resolve + execute skill | resolver → executor |
| `hermes skill list [--project]` | List skills by namespace | Registry v1.1 |
| `hermes skill explain <id>` | Show skill metadata + health | Registry + health engine |
| `hermes health [skill_id]` | Show health state + score | health engine |
| `hermes audit [skill_id]` | Show execution history | telemetry event store |
| `hermes governance` | List pending proposals | governance proposal store |

## Design Principles

```
✅ All commands route through Kernel (never bypass)
✅ All execution passes through Resolver
✅ All operations enter Audit trail
✅ No direct Registry mutation from CLI
✅ Project-scoped output (per-project visibility)
```

## Decision

```
🟢 Interface Layer — Design Approved
```
