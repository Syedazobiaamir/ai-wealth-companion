---
id: 002
title: Phase I Laws Amendment
stage: constitution
date: 2026-01-18
surface: agent
model: claude-opus-4-5-20251101
feature: none
branch: master
user: unknown
command: /sp.constitution
labels: ["constitution", "phase1", "cli", "governance", "amendment"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - .specify/memory/constitution.md
tests:
  - null
---

## Prompt

constitution/phase1.const.md

# Phase I Constitution - CLI App

## Purpose
Implement the **core account & transaction management** in Python CLI (in-memory), forming foundation for web, AI, and cloud phases.

## Data Storage
- Accounts: dictionary
- Transactions: list of dictionaries
- Recurring payments: boolean flag

## UI Guidelines
- Emoji & colors: Income, Expense, Recurring
- Menu numbers & clear navigation
- Tabular output for transactions (use `tabulate`)

## Validation
- Unique account names
- Transaction amount > 0
- Valid date: YYYY-MM-DD
- Transaction type: Income/Expense/Transfer
- Recurring: Yes/No

# Phase I Constitution - CLI Financial Core

## Purpose
Create a stable, testable, in-memory financial core that will later be reused by the web app and AI agents.

## Core Laws
- All behavior must come from specifications.
- No AI features in Phase I.
- No databases. In-memory only.
- CLI is the only interface.
- Clean separation between CLI, logic, and storage.

## Engineering Laws
- Domain logic must be framework-independent.
- Storage must be swappable.
- Commands must be deterministic.
- Every command must be testable.

## Safety Laws
- No real banking connections.
- No real financial advice.
- Sample data only.

## Acceptance Laws
- Every feature must work via CLI.
- All commands must show confirmations.
- Data resets on restart.

## Response snapshot

Amended constitution from v1.0.0 to v1.1.0 (MINOR version bump).

**Added Phase I Laws section** containing:
- Core Laws (NON-NEGOTIABLE): spec-driven behavior, no AI, in-memory only, CLI only, layer separation
- Engineering Laws: framework-independent logic, swappable storage, deterministic commands, testable commands
- Safety Laws: no real banking, no real advice, sample data only
- Acceptance Laws: CLI-only features, confirmations required, data resets on restart
- Phase I Data Storage: accounts (dict), transactions (list), recurring (bool flag)
- Phase I Validation Rules: unique names, amount > 0, YYYY-MM-DD dates, valid types
- Phase I UI Guidelines: emoji colors, menu numbers, tabulate library

Also added Phase I to Deployment Phases section for completeness.

All existing Core Principles (I-VI) preserved unchanged.

## Outcome

- Impact: Constitution amended with Phase I specific laws; establishes CLI-only, in-memory constraints for initial phase
- Tests: N/A (governance document)
- Files: 1 file modified (.specify/memory/constitution.md)
- Next prompts: /sp.specify to create Phase I feature specs, /sp.plan to design CLI architecture
- Reflection: Phase I laws properly scope the initial development to avoid scope creep (no AI, no database, CLI only)

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): PASS - version bumped correctly, all Phase I constraints captured
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): N/A
