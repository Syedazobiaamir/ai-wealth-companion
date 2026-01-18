# Research: Phase I Financial Core

**Feature**: 002-phase1-financial-core
**Date**: 2026-01-18

## Technology Decisions

### Decision 1: Python Version

**Decision**: Python 3.x (3.10+ recommended)
**Rationale**: Specified in constitution; modern type hints support for better code quality
**Alternatives considered**:
- Python 3.8: Older, fewer type hint features
- Python 3.12: Newer but not necessary for CLI app

### Decision 2: CLI Libraries

**Decision**: colorama (colored text) + tabulate (table display)
**Rationale**: Specified in user requirements; lightweight, well-maintained libraries
**Alternatives considered**:
- Rich: More features but heavier dependency
- Click: Full CLI framework, overkill for Phase I
- Typer: Modern but adds unnecessary complexity for Phase I scope

### Decision 3: Storage Pattern

**Decision**: Repository pattern with in-memory dictionaries/lists
**Rationale**: Constitution mandates repository pattern for future database swap; dictionaries provide O(1) lookup by ID
**Alternatives considered**:
- Direct data structures: Violates constitution's swappable storage requirement
- SQLite in-memory: Adds unnecessary database dependency for Phase I

### Decision 4: Project Structure

**Decision**: Single project with layered architecture (models → services → repositories → cli)
**Rationale**: Phase I is CLI-only; simple structure appropriate for scope
**Alternatives considered**:
- Multiple packages: Overkill for Phase I
- Flat structure: Would violate layer separation principle

### Decision 5: Testing Framework

**Decision**: pytest
**Rationale**: Industry standard for Python; supports TDD workflow required by constitution
**Alternatives considered**:
- unittest: Built-in but less ergonomic
- nose2: Less popular, fewer features

## Best Practices Research

### Python CLI Application Patterns

1. **Entry Point**: Use `__main__.py` for CLI entry
2. **Argument Parsing**: Use `argparse` for command-line arguments (built-in, no extra dependency)
3. **Menu Loop**: While-loop with input() for interactive menu
4. **Error Handling**: Catch exceptions at CLI layer, display user-friendly messages

### Repository Pattern in Python

1. **Interface**: Define abstract base class (ABC) for repository interface
2. **Implementation**: Concrete class implements interface with in-memory storage
3. **Dependency Injection**: Pass repository to service layer, enables testing with mocks

### In-Memory Data Structure Selection

| Entity | Structure | Rationale |
|--------|-----------|-----------|
| Transactions | Dict[int, Transaction] | O(1) lookup by ID, iteration for filtering |
| Categories | Dict[str, Category] | O(1) lookup by name (unique key) |
| Budgets | Dict[str, Budget] | O(1) lookup by category name |

## Validation Approach

Per constitution Phase I Validation Rules:
- Amount validation: Check > 0 before storage
- Date validation: Parse with datetime, reject invalid formats
- Type validation: Check against enum/set of valid types
- Category validation: Check existence before transaction creation

## Dependencies Summary

```
colorama>=0.4.6    # Colored terminal output
tabulate>=0.9.0    # Table formatting
pytest>=7.0.0      # Testing (dev dependency)
```

## Unresolved Items

None - all technical decisions resolved from constitution and user input.
