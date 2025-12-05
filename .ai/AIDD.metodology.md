# AI-Driven Development Methodology (AIDD)

## Overview

AIDD is a methodology for generating high-quality software through a structured, three-role process: Architect, Builder, and Craftsman. Each role has specific responsibilities and deliverables, ensuring comprehensive coverage from requirements to implementation and documentation.

## Roles and Workflow

### Architect

The Architect role is responsible for defining requirements, features, and domain models.

#### Input Files:

- `.ai/architect/a-1.prd.instructions.md`: Instructions for generating the PRD (Product Requirements Document).
- `.ai/architect/a-1.prd.template.md`: Template with the expected structure of the PRD.
- `.ai/architect/a-2.features.instructions.md`: Instructions for generating detailed feature descriptions.
- `.ai/architect/a-2.features.template.md`: Template with the detailed structure of a feature.
- `.ai/architect/a-3.domain-model.instructions.md`: Instructions for generating the Domain Model document.
- `.ai/architect/a-3.domain-model.template.md`: Template with the expected structure of the Domain Model document.
- `.ai/syntax.template.md`: Template syntax reference.
- `.ai/WORKFLOW_STATES.md`: Feature state machine and transitions (see workflow documentation).
- `.ai/QUALITY_GATES.md`: Quality criteria and validation checkpoints (see quality documentation).

#### Output Deliverables:

- `docs/PRD.md` and `docs/PRD-es.md`: Product Requirements Document describing system functionality and characteristics (English and Spanish versions).
- `docs/DOMAIN.md` and `docs/DOMAIN-es.md`: Domain document defining key concepts and relationships. Entity-Relationship diagrams with business rules (English and Spanish versions).
- `github.com/issues`: GitHub issues describing specific tasks and features to implement, with their states.

#### Key Responsibilities:

- Define product vision and requirements
- Break down features into detailed specifications
- Model the domain with entities, relationships, and business rules
- Create GitHub issues for each feature
- Ensure quality gates are met before transitioning features to Builder

### Builder

The Builder role is responsible for planning and implementing features.

**Note**: After implementing features that interact with browsers (APIs, authentication, etc.), consider using the optional **Inspector** phase before moving to Craftsman.

The Builder role is responsible for planning and implementing features.

#### Input Files:

- `.ai/builder/b-1.plan.instructions.md`: Instructions for planning feature implementation.
- `.ai/builder/b-1.plan.template.md`: Template with the structure of a feature implementation plan.
- `.ai/builder/b-2.implement.instructions.md`: Instructions for implementing a feature plan.
- `.ai/syntax.template.md`: Template syntax reference.
- `.ai/PATTERNS.md`: Architecture and design patterns (see patterns documentation).
- `.ai/BEST_PRACTICES.md`: Development best practices (see best practices documentation).
- `.ai/WORKFLOW_STATES.md`: Feature state machine and transitions.
- `.ai/QUALITY_GATES.md`: Quality criteria and validation checkpoints.

#### Output Deliverables:

- `docs/features/{feature-slug}/plan.md`: Implementation plan document for a feature.
- Source code in the project structure: Source code organized by layers and features.

#### Key Responsibilities:

- Create detailed implementation plans for features
- Implement code following architectural patterns
- Ensure code meets quality standards
- Update feature states in GitHub issues

### Inspector (Optional)

The Inspector role is responsible for validating backend APIs from a real browser perspective.

#### Input Files:

- `.ai/inspector/i-1.browser-integration.instructions.md`: Instructions for browser-based integration testing.
- Implemented API endpoints from Builder phase
- Test pages or API testing tools

#### Output Deliverables:

- `docs/features/{feature-slug}/integration-issues.md`: Documentation of integration issues found.
- Updated implementation with fixes
- Performance baseline metrics
- Integration validation report

#### Key Responsibilities:

- Connect to browser developer tools for real-time inspection
- Validate CORS, authentication, and response formats
- Monitor console for errors and warnings
- Measure API performance from client perspective
- Document integration issues with evidence
- Suggest backend fixes for issues found

#### When to Use:

- After implementing authentication/authorization endpoints
- When APIs are consumed by frontend applications
- Before deploying to production
- When debugging browser-specific integration issues

**Note**: This phase is optional and should be used strategically. Skip it for backend-only features or internal services not accessed by browsers.

### Craftsman

The Craftsman role is responsible for testing and documenting features.

#### Input Files:

- `.ai/craftsman/c-1.test.instructions.md`: Instructions for implementing feature tests.
- `.ai/craftsman/c-2.document.instructions.md`: Instructions for documenting feature source code.
- `.ai/syntax.template.md`: Template syntax reference.
- `.ai/PATTERNS.md`: Testing and documentation patterns.
- `.ai/BEST_PRACTICES.md`: Testing and documentation best practices.
- `.ai/WORKFLOW_STATES.md`: Feature state machine and transitions.
- `.ai/QUALITY_GATES.md`: Quality criteria and validation checkpoints.

#### Output Deliverables:

- Test files: Unit and integration tests for the system, organized by features.
- `docs/STRUCTURE.md` and `docs/STRUCTURE-es.md`: Structure document describing system architecture, including design patterns and folder organization (English and Spanish versions).
- Inline code documentation: API documentation, type definitions, and configuration documentation.

#### Key Responsibilities:

- Write comprehensive tests for implemented features
- Document public APIs, interfaces, and configurations
- Update architecture documentation
- Ensure quality gates are met before marking features as complete

## Workflow and States

Features progress through defined states managed via GitHub issues. See `.ai/WORKFLOW_STATES.md` for the complete state machine and transition rules.

### Workflow Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         AIDD Workflow                            │
└─────────────────────────────────────────────────────────────────┘

ARCHITECT PHASE
    │
    ├─► PRD Creation ───────────────┐
    │   (Quality Gate 1)             │
    │                                 │
    ├─► Feature Definition ──────────┼──► GitHub Issues Created
    │   (Quality Gate 2)             │    (State: draft)
    │                                 │
    └─► Domain Model ────────────────┘
        (Quality Gate 3)
                │
                ▼
        [State: defined]
                │
                ▼
BUILDER PHASE
    │
    ├─► Implementation Plan ─────────┐
    │   (Quality Gate 4)             │
    │                                 │
    └─► Code Implementation ─────────┼──► Source Code
        (Quality Gate 5)             │
                │
                ▼
        [State: implemented]
                │
                ▼
INSPECTOR PHASE (Optional)
    │
    ├─► Browser DevTools Inspection ┐
    │   (Quality Gate 5.5)           │
    │                                 │
    └─► Integration Validation ──────┼──► Integration Issues Report
        (Quality Gate 5.5)           │
                │
                ▼
        [State: validated]
                │
                ▼
CRAFTSMAN PHASE
    │
    ├─► Testing ─────────────────────┐
    │   (Quality Gate 6)             │
    │                                 │
    └─► Documentation ────────────────┼──► Tests + Docs
        (Quality Gate 7)             │
                │
                ▼
        [State: documented]
                │
                ▼
        [State: deployed] ──────────► Production

Quality gates must pass before transitioning to next state.
```

## Quality Assurance

Each role has specific quality gates that must be met before features can transition to the next stage. See `.ai/QUALITY_GATES.md` for detailed quality criteria and validation checkpoints.

## Related Documentation

- [Template Syntax](syntax.template.md): Reference for template syntax used in all templates.
- [Workflow States](WORKFLOW_STATES.md): Feature state machine and transition rules.
- [Quality Gates](QUALITY_GATES.md): Quality criteria and validation checkpoints.
- [Architecture Patterns](PATTERNS.md): Technology-agnostic architecture and design patterns.
- [Best Practices](BEST_PRACTICES.md): Development best practices and principles.
