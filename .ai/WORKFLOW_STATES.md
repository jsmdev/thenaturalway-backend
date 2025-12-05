# Workflow States - AIDD Methodology

## Overview

Features in the AIDD methodology progress through a defined set of states managed via GitHub issues. Each state represents a specific phase in the development lifecycle and has associated responsibilities and quality gates.

## State Machine Diagram

```
[draft] → [defined] → [planned] → [implemented] → [tested] → [documented] → [deployed]
   ↑                                                                    ↓
   └──────────────────────────────────────────────────────────────────┘
                               (if rework needed)
```

## Feature States

### 1. draft (borrador-arquitecto)

**Role**: Architect
**Label**: `borrador-arquitecto`
**Description**: Initial state when a feature is first identified in the PRD.

**Entry Conditions**:
- Feature is identified and added to PRD
- GitHub issue is created for the feature

**Responsibilities**:
- Create GitHub issue with basic feature description
- Add `borrador-arquitecto` label
- Link issue in PRD

**Quality Criteria**: None (entry state)

**Valid Transitions**: → `defined`

---

### 2. defined (definido-arquitecto)

**Role**: Architect
**Label**: `definido-arquitecto`
**Description**: Feature is fully defined with detailed requirements and acceptance criteria.

**Entry Conditions**:
- Feature definition is complete
- Acceptance criteria are specified
- Dependencies are identified

**Responsibilities**:
- Complete feature definition following template
- Update GitHub issue with full definition
- Remove `borrador-arquitecto` label
- Add `definido-arquitecto` label
- Update PRD with feature status

**Quality Criteria**:
- Feature description is complete
- User stories/use cases are defined
- Acceptance criteria are testable
- Functional and non-functional requirements are documented
- Dependencies are identified

**Valid Transitions**: → `planned`

**Blocking Conditions**:
- Feature definition is incomplete
- Acceptance criteria are missing or unclear
- Dependencies are not identified

---

### 3. planned (builder-planned)

**Role**: Builder
**Label**: `builder-planned`
**Description**: Implementation plan is created with detailed tasks and dependencies.

**Entry Conditions**:
- Feature is in `defined` state
- Implementation plan document is created

**Responsibilities**:
- Create detailed implementation plan
- Break feature into discrete tasks
- Identify task dependencies and order
- Document risks and mitigations
- Save plan to `docs/features/{feature-slug}/plan.md`
- Add plan as comment to GitHub issue
- Remove `definido-arquitecto` label
- Add `builder-planned` label
- Update PRD with plan link

**Quality Criteria**:
- Plan breaks feature into implementable tasks
- Tasks have clear acceptance criteria
- Task dependencies are identified
- Risks and mitigations are documented
- Plan follows project conventions

**Valid Transitions**: → `implemented`

**Blocking Conditions**:
- Plan is incomplete
- Tasks are not actionable
- Dependencies are unclear

---

### 4. implemented (builder-implemented)

**Role**: Builder
**Label**: `builder-implemented`
**Description**: All code for the feature is implemented and meets quality standards.

**Entry Conditions**:
- Feature is in `planned` state
- All implementation tasks are complete
- Code passes static analysis

**Responsibilities**:
- Implement all tasks from the plan
- Follow architectural patterns and best practices
- Ensure code passes static analysis
- Update GitHub issue with implementation progress
- Remove `builder-planned` label
- Add `builder-implemented` label

**Quality Criteria**:
- All plan tasks are implemented
- Code follows architectural patterns
- Code adheres to coding standards
- Static analysis passes
- Code compiles/executes without errors

**Valid Transitions**: → `tested`, → `planned` (if rework needed)

**Blocking Conditions**:
- Implementation tasks are incomplete
- Static analysis fails
- Code does not compile/execute

---

### 5. tested (craftsman-tested)

**Role**: Craftsman
**Label**: `craftsman-tested`
**Description**: Comprehensive tests are written and all tests pass.

**Entry Conditions**:
- Feature is in `implemented` state
- Test suite is created
- All tests pass

**Responsibilities**:
- Write unit and integration tests
- Ensure test coverage meets minimum threshold
- Verify all tests pass
- Update GitHub issue with test coverage information
- Remove `builder-implemented` label
- Add `craftsman-tested` label

**Quality Criteria**:
- Unit tests cover business logic
- Edge cases are tested
- Tests follow Arrange-Act-Assert pattern
- All tests pass consistently
- Test coverage meets minimum threshold (>80% recommended)

**Valid Transitions**: → `documented`, → `implemented` (if rework needed)

**Blocking Conditions**:
- Tests are incomplete
- Test coverage is below threshold
- Tests fail

---

### 6. documented (craftsman-documented)

**Role**: Craftsman
**Label**: `craftsman-documented`
**Description**: All public APIs, interfaces, and architecture are documented.

**Entry Conditions**:
- Feature is in `tested` state
- Documentation is complete
- Architecture documentation is updated

**Responsibilities**:
- Document all public APIs and interfaces
- Update architecture documentation (STRUCTURE.md)
- Ensure documentation exists in both languages
- Update GitHub issue with documentation links
- Remove `craftsman-tested` label
- Add `craftsman-documented` label

**Quality Criteria**:
- Public APIs are documented
- Interfaces and types are documented
- Configuration options are documented
- Examples are provided
- STRUCTURE.md is updated
- Documentation is in both English and Spanish

**Valid Transitions**: → `deployed`

**Blocking Conditions**:
- Documentation is incomplete
- Public APIs are not documented
- STRUCTURE.md is not updated

---

### 7. deployed

**Role**: DevOps / Release Manager
**Label**: `deployed`
**Description**: Feature is deployed to production environment.

**Entry Conditions**:
- Feature is in `documented` state
- All quality gates are passed
- Deployment is successful

**Responsibilities**:
- Deploy feature to production
- Verify deployment is successful
- Monitor for issues
- Remove `craftsman-documented` label
- Add `deployed` label
- Update PRD with deployment status

**Quality Criteria**:
- Feature is successfully deployed
- No critical errors in production
- Monitoring indicates healthy state

**Valid Transitions**: End state (feature complete)

---

## State Transitions

### Forward Transitions (Normal Flow)

1. `draft` → `defined`: Architect completes feature definition
2. `defined` → `planned`: Builder creates implementation plan
3. `planned` → `implemented`: Builder completes implementation
4. `implemented` → `tested`: Craftsman completes testing
5. `tested` → `documented`: Craftsman completes documentation
6. `documented` → `deployed`: Feature is deployed

### Backward Transitions (Rework)

- `implemented` → `planned`: If implementation needs rework or plan needs adjustment
- `tested` → `implemented`: If tests reveal implementation issues
- `documented` → `tested`: If documentation reveals missing test coverage

**Note**: Backward transitions should be avoided when possible. They indicate quality issues that should be caught earlier.

## State Management

### GitHub Labels

Each state corresponds to a GitHub label:
- `borrador-arquitecto`: draft
- `definido-arquitecto`: defined
- `builder-planned`: planned
- `builder-implemented`: implemented
- `craftsman-tested`: tested
- `craftsman-documented`: documented
- `deployed`: deployed

### State Updates

When transitioning a feature:
1. Remove the current state label
2. Add the new state label
3. Update the PRD with the new status
4. Add a comment to the GitHub issue documenting the transition
5. Commit changes with appropriate conventional commit message

### State Validation

Before transitioning:
1. Verify all quality criteria for current state are met
2. Verify entry conditions for target state are satisfied
3. Ensure no blocking conditions exist
4. Update all relevant documentation

## Workflow Best Practices

1. **Don't Skip States**: Each state has a purpose. Skipping states leads to quality issues.
2. **Validate Transitions**: Always verify quality gates before transitioning.
3. **Document Changes**: Update PRD, GitHub issues, and other documentation when transitioning.
4. **Avoid Backward Transitions**: Catch issues early to minimize rework.
5. **Monitor Progress**: Track features through states to identify bottlenecks.

## State Checklist Template

When transitioning a feature to a new state:

```
### Transitioning [Feature Name] from [Old State] to [New State]

**Quality Criteria Met**:
- [ ] All criteria for old state are satisfied
- [ ] Entry conditions for new state are met
- [ ] No blocking conditions exist

**Updates Required**:
- [ ] GitHub labels updated
- [ ] PRD updated with new status
- [ ] GitHub issue updated/commented
- [ ] Related documentation updated
- [ ] Changes committed with conventional commit message
```

## Notes

- States are managed via GitHub issue labels
- PRD should always reflect current feature status
- Quality gates must be passed before state transitions
- Document any exceptions or special cases
