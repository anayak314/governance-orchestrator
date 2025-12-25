# Context management rationale

This document explains how the framework minimizes effective LLM context usage by externalizing state, enforcing contracts, and making sessions resumable without re-teaching instructions.

## Problem the framework solves
LLM-only conversations drift and bloat: rules fade, clarifications repeat, and implicit constraints vanish after truncation. Token pressure forces re-derivation and increases correction loops.

## Architectural shift
- Memory moves from chat to versioned artifacts (`specs/`, `todo.md`, `handover.md`, `runs/`).
- Narrative context is replaced by symbolic references (spec IDs, Concept manifests, Synchronizations).
- Control-plane chat is distinct from the state-plane repo; `AGENTS.md` defines the boundary.

## Mechanisms that reduce context pressure
- Spec-first rule in `AGENTS.md` keeps requirements in `specs/` and out of long chats.
- Concepts + manifests (`concepts/`) anchor domain state; Synchronizations (`synchronizations/`) declare cross-domain coupling explicitly.
- Governance CI (`.github/workflows/`) and PDCA in `docs/agents.md` enforce schemas, lint, and invariants on every run.
- Handover + run records (`handover.md`, `runs/`) rehydrate progress without recalling prior messages.
- README governance (`README_GOVERNANCE.md`, `README_SPEC.yaml`) prevents instruction drift in entry docs.

## Why the model stops “remembering”
- Required constraints live in files; prompts reference those files instead of replaying chat logs.
- Rehydration pulls artifacts (specs, manifests, handover) so truncation does not erase rules.
- Lost chat tokens no longer imply lost constraints because CI and validators block out-of-contract outputs.

## Practical consequences
- Longer productive sessions before intervention is needed.
- Fewer correction loops because constraints are reread, not retaught.
- Faster restarts: load `handover.md`, `todo.md`, and relevant specs to continue.
- Lower cognitive load for humans: follow the document map instead of re-typing context.

## Boundaries
- Does not increase raw token limits.
- Requires disciplined upkeep of specs, manifests, and handover entries.
- CI enforcement must stay enabled; disabling it removes the guarantees described here.
