# AIDD Methodology - Documentation Index

## Overview

Welcome to the AI-Driven Development (AIDD) methodology documentation. This index helps you navigate all the documentation and understand the methodology structure.

## Quick Start

1. **Start Here**: Read [AIDD.metodology.md](AIDD.metodology.md) for an overview of the methodology
2. **Understand the Workflow**: Check [WORKFLOW_STATES.md](WORKFLOW_STATES.md) to understand how features progress through states
3. **Quality Standards**: Review [QUALITY_GATES.md](QUALITY_GATES.md) to understand quality requirements
4. **Patterns and Practices**: Consult [PATTERNS.md](PATTERNS.md) and [BEST_PRACTICES.md](BEST_PRACTICES.md) for guidance

## Core Documentation

### Methodology Overview

- **[AIDD.metodology.md](AIDD.metodology.md)**: Main methodology document describing roles, workflow, and responsibilities
- **[WORKFLOW_STATES.md](WORKFLOW_STATES.md)**: Feature state machine, transitions, and state management
- **[QUALITY_GATES.md](QUALITY_GATES.md)**: Quality criteria and validation checkpoints for each stage
- **[syntax.template.md](syntax.template.md)**: Template syntax reference for all templates

### Reference Documentation

- **[PATTERNS.md](PATTERNS.md)**: Technology-agnostic architecture and design patterns
- **[BEST_PRACTICES.md](BEST_PRACTICES.md)**: Development best practices and principles

## Role-Specific Documentation

### Architect Role

The Architect defines requirements, features, and domain models.

#### Instructions

- **[a-1.prd.instructions.md](architect/a-1.prd.instructions.md)**: Instructions for generating the PRD
- **[a-2.features.instructions.md](architect/a-2.features.instructions.md)**: Instructions for defining features
- **[a-3.domain-model.instructions.md](architect/a-3.domain-model.instructions.md)**: Instructions for creating the domain model

#### Templates

- **[a-1.prd.template.md](architect/a-1.prd.template.md)**: PRD template structure
- **[a-2.features.template.md](architect/a-2.features.template.md)**: Feature definition template
- **[a-3.domain-model.template.md](architect/a-3.domain-model.template.md)**: Domain model template

#### Quality Gates

- Gate 1: PRD Completion - See [QUALITY_GATES.md](QUALITY_GATES.md#gate-1-prd-completion)
- Gate 2: Feature Definition - See [QUALITY_GATES.md](QUALITY_GATES.md#gate-2-feature-definition-completion)
- Gate 3: Domain Model - See [QUALITY_GATES.md](QUALITY_GATES.md#gate-3-domain-model-completion)

### Builder Role

The Builder plans and implements features.

#### Instructions

- **[b-1.plan.instructions.md](builder/b-1.plan.instructions.md)**: Instructions for creating implementation plans
- **[b-2.implement.instructions.md](builder/b-2.implement.instructions.md)**: Instructions for implementing features

#### Templates

- **[b-1.plan.template.md](builder/b-1.plan.template.md)**: Implementation plan template

#### Quality Gates

- Gate 4: Implementation Plan - See [QUALITY_GATES.md](QUALITY_GATES.md#gate-4-implementation-plan-completion)
- Gate 5: Code Implementation - See [QUALITY_GATES.md](QUALITY_GATES.md#gate-5-code-implementation-completion)

### Craftsman Role

The Craftsman tests and documents features.

#### Instructions

- **[c-1.test.instructions.md](craftsman/c-1.test.instructions.md)**: Instructions for writing tests
- **[c-2.document.instructions.md](craftsman/c-2.document.instructions.md)**: Instructions for documentation

#### Quality Gates

- Gate 6: Test Coverage - See [QUALITY_GATES.md](QUALITY_GATES.md#gate-6-test-coverage-completion)
- Gate 7: Documentation - See [QUALITY_GATES.md](QUALITY_GATES.md#gate-7-documentation-completion)

## Workflow Overview

```
draft → defined → planned → implemented → tested → documented → deployed
```

For detailed state transitions and rules, see [WORKFLOW_STATES.md](WORKFLOW_STATES.md).

## Document Generation

All generated documents follow a bilingual approach:

- English version: `docs/{DOCUMENT}.md` (e.g., `docs/PRD.md`)
- Spanish version: `docs/{DOCUMENT}-es.md` (e.g., `docs/PRD-es.md`)

Documents generated:
- PRD (Product Requirements Document)
- DOMAIN (Domain Model Document)
- STRUCTURE (Architecture Structure Document)
- Feature Plans: `docs/features/{feature-slug}/plan.md`

## Key Concepts

### Quality Gates

Quality gates are checkpoints that ensure deliverables meet minimum standards before progressing. Each role has specific quality gates that must be passed. See [QUALITY_GATES.md](QUALITY_GATES.md) for details.

### Workflow States

Features progress through defined states tracked via GitHub issues. State transitions follow specific rules and quality gates. See [WORKFLOW_STATES.md](WORKFLOW_STATES.md) for the complete state machine.

### Patterns

The methodology uses technology-agnostic patterns that can be applied across different programming languages and frameworks. See [PATTERNS.md](PATTERNS.md) for common patterns.

### Best Practices

Development best practices guide implementation decisions. See [BEST_PRACTICES.md](BEST_PRACTICES.md) for principles and guidelines.

## Getting Help

### For Specific Questions

- **Workflow and States**: [WORKFLOW_STATES.md](WORKFLOW_STATES.md)
- **Quality Requirements**: [QUALITY_GATES.md](QUALITY_GATES.md)
- **Architecture Patterns**: [PATTERNS.md](PATTERNS.md)
- **Development Practices**: [BEST_PRACTICES.md](BEST_PRACTICES.md)
- **Template Syntax**: [syntax.template.md](syntax.template.md)

### Role-Specific Help

- **Architect**: See `architect/` directory for role-specific documentation
- **Builder**: See `builder/` directory for role-specific documentation
- **Craftsman**: See `craftsman/` directory for role-specific documentation

## Document Relationships

```
AIDD.metodology.md (Main entry point)
    ├── WORKFLOW_STATES.md (State management)
    ├── QUALITY_GATES.md (Quality criteria)
    ├── PATTERNS.md (Architecture patterns)
    ├── BEST_PRACTICES.md (Development practices)
    └── syntax.template.md (Template syntax)
            │
            ├── architect/ (Role documentation)
            │   ├── Instructions
            │   └── Templates
            ├── builder/ (Role documentation)
            │   ├── Instructions
            │   └── Templates
            └── craftsman/ (Role documentation)
                └── Instructions
```

## Quick Reference Checklist

When starting a new feature:

- [ ] Architect: Create PRD and define features
- [ ] Architect: Create domain model
- [ ] Builder: Create implementation plan
- [ ] Builder: Implement code
- [ ] Craftsman: Write tests
- [ ] Craftsman: Document code and architecture

Each step has quality gates that must be passed before proceeding.

## Notes

- All documentation is technology-agnostic
- Templates use syntax defined in `syntax.template.md`
- Quality gates are enforced, not optional
- State transitions follow rules in `WORKFLOW_STATES.md`
- Generated documents are bilingual (English and Spanish)

---

**Last Updated**: See git history for latest changes

