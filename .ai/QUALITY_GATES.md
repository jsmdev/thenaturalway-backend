# Quality Gates - AIDD Methodology

## Overview

Quality Gates are checkpoints in the AIDD methodology that ensure each deliverable meets minimum quality standards before progressing to the next stage. Each role has specific quality criteria that must be validated.

## Quality Gate Structure

Each quality gate consists of:
- **Objective**: What we're validating
- **Criteria**: Specific requirements that must be met
- **Validation Method**: How to verify the criteria
- **Exit Criteria**: Conditions that must be satisfied to proceed

## Architect Quality Gates

### Gate 1: PRD Completion

**Objective**: Ensure the Product Requirements Document is complete, clear, and actionable.

**Criteria**:
- ✅ All required sections are present and complete
- ✅ Product vision is clearly defined
- ✅ Target audience is identified
- ✅ All features are listed with priorities
- ✅ System context diagram is included (using C4 model)
- ✅ Technical specifications are defined (agnostic of specific technologies)
- ✅ Document exists in both English and Spanish versions

**Validation Method**:
- Review PRD structure against template
- Verify all placeholders are filled
- Check that technical specifications are technology-agnostic
- Verify both language versions exist and are synchronized

**Exit Criteria**:
- PRD is approved and saved to `docs/PRD.md` and `docs/PRD-es.md`
- All features have corresponding GitHub issues created
- PRD is linked in repository README

---

### Gate 2: Feature Definition Completion

**Objective**: Ensure each feature is fully defined with sufficient detail for implementation planning.

**Criteria**:
- ✅ Feature description is clear and complete
- ✅ User stories or use cases are defined
- ✅ Acceptance criteria are specified
- ✅ Functional requirements are documented
- ✅ Non-functional requirements are identified (performance, security, etc.)
- ✅ Dependencies on other features are identified
- ✅ Edge cases and error scenarios are considered
- ✅ If feature has user interface, UI/UX section is complete with components, user flow, states, and validations
- ✅ If feature is API/backend only, UI/UX section indicates "Not applicable"
- ✅ Feature definition is updated in GitHub issue (main description, not just comments)

**Validation Method**:
- Review feature definition against template
- Verify acceptance criteria are testable
- Check that dependencies are clearly stated
- Validate that the GitHub issue contains the complete definition

**Exit Criteria**:
- Feature definition is complete in GitHub issue
- Feature status is set to "defined"
- PRD is updated with feature status
- Feature can be transitioned to Builder for planning

---

### Gate 3: Domain Model Completion

**Objective**: Ensure the domain model accurately represents business concepts, entities, and relationships.

**Criteria**:
- ✅ All major entities are identified with attributes
- ✅ Entity relationships are clearly defined (one-to-one, one-to-many, many-to-many)
- ✅ Business rules are documented for each entity and relationship
- ✅ Entity-Relationship diagram is created (using Mermaid syntax)
- ✅ Glossary of domain terms is included
- ✅ Cardinality and constraints are specified
- ✅ Domain model exists in both English and Spanish versions

**Validation Method**:
- Review domain model structure against template
- Verify ER diagram is syntactically correct and renders properly
- Check that business rules are clear and implementable
- Validate entity relationships are logically sound

**Exit Criteria**:
- Domain model is saved to `docs/DOMAIN.md` and `docs/DOMAIN-es.md`
- ER diagram is included and renders correctly
- Domain model is linked in PRD
- All entities correspond to features in PRD

## Builder Quality Gates

### Gate 4: Implementation Plan Completion

**Objective**: Ensure the implementation plan is detailed, actionable, and complete.

**Criteria**:
- ✅ Plan breaks down feature into discrete, implementable tasks
- ✅ Tasks are ordered by dependencies
- ✅ Each task has clear acceptance criteria
- ✅ Task complexity is estimated
- ✅ Dependencies between tasks are identified
- ✅ Risks and mitigations are documented
- ✅ Required architectural patterns are identified
- ✅ Plan follows project conventions and patterns
- ✅ If feature has user interface, plan includes Presentation layer tasks (templates, views, UI components, forms, etc.)
- ✅ If feature is API/backend only, Presentation layer may be omitted

**Validation Method**:
- Review plan structure against template
- Verify tasks are specific and actionable
- Check that dependencies form a valid directed acyclic graph
- Validate that acceptance criteria are testable

**Exit Criteria**:
- Plan is saved to `docs/features/{feature-slug}/plan.md`
- Plan is commented in GitHub issue
- Feature status is set to "planned"
- PRD is updated with plan link

---

### Gate 5: Code Implementation Completion

**Objective**: Ensure implemented code meets quality standards and follows best practices.

**Criteria**:
- ✅ All tasks from the plan are implemented
- ✅ Code follows architectural patterns specified in plan
- ✅ Code adheres to project coding standards
- ✅ Static analysis passes (linters, type checkers, etc.)
- ✅ Code compiles/executes without errors
- ✅ Code is organized following project structure conventions
- ✅ Dependencies are properly managed
- ✅ No hardcoded values or magic numbers (use constants/config)
- ✅ If plan includes Presentation layer, all UI components are implemented (templates, views, forms, reusable components, etc.)
- ✅ User interface follows UI/UX requirements defined in feature definition

**Validation Method**:
- Execute static analysis tools
- Review code structure and organization
- Verify all plan tasks are completed
- Check code follows patterns from PATTERNS.md
- Validate adherence to BEST_PRACTICES.md

**Exit Criteria**:
- All implementation tasks are complete
- Code passes static analysis
- Feature status is set to "implemented"
- Feature can be transitioned to Craftsman for testing

## Craftsman Quality Gates

### Gate 6: Test Coverage Completion

**Objective**: Ensure comprehensive test coverage for implemented functionality.

**Criteria**:
- ✅ Unit tests cover all business logic
- ✅ Edge cases and error scenarios are tested
- ✅ Tests follow Arrange-Act-Assert pattern
- ✅ Tests are independent and can run in any order
- ✅ All dependencies are mocked/stubbed
- ✅ Test coverage meets minimum threshold (recommended: >80% for business logic)
- ✅ Tests are organized following project conventions
- ✅ All tests pass consistently

**Validation Method**:
- Execute test suite and verify all tests pass
- Run coverage analysis tools
- Review test quality and completeness
- Check that tests follow testing patterns

**Exit Criteria**:
- Test suite passes completely
- Coverage meets minimum threshold
- Feature status is set to "tested"
- Feature can be transitioned to documentation phase

---

### Gate 7: Documentation Completion

**Objective**: Ensure all public APIs, interfaces, and configurations are properly documented.

**Criteria**:
- ✅ Public APIs are documented (inline documentation)
- ✅ Interfaces and types are documented
- ✅ Configuration options are documented
- ✅ Examples of usage are provided
- ✅ Architecture documentation is updated (STRUCTURE.md)
- ✅ Documentation follows project conventions
- ✅ Documentation exists in both English and Spanish versions (for STRUCTURE.md)
- ✅ No sensitive information is exposed in public documentation

**Validation Method**:
- Review inline documentation completeness
- Verify examples are correct and executable
- Check that STRUCTURE.md reflects current architecture
- Validate that documentation tools can generate output (if applicable)

**Exit Criteria**:
- All public APIs are documented
- STRUCTURE.md is updated and saved to `docs/STRUCTURE.md` and `docs/STRUCTURE-es.md`
- Feature status is set to "documented"
- Feature is complete and ready for deployment

## Quality Metrics

### Recommended Metrics

- **Code Quality**: Static analysis score, complexity metrics
- **Test Coverage**: Line coverage, branch coverage, function coverage
- **Documentation Coverage**: Percentage of public APIs documented
- **Completeness**: Percentage of planned tasks completed

### Continuous Improvement

- Review quality gates periodically
- Adjust criteria based on project needs
- Collect metrics to identify improvement areas
- Share lessons learned across the team

## Quality Gate Checklist Template

Use this checklist when reviewing deliverables:

```
### [Gate Name] Checklist

- [ ] All criteria are met
- [ ] Validation methods have been executed
- [ ] Exit criteria are satisfied
- [ ] Any issues are documented and resolved
- [ ] Deliverable is saved in correct location
- [ ] Status is updated in tracking system (GitHub issues)
- [ ] Related documentation is updated
```

## Notes

- Quality gates should be enforced, not optional
- If a gate fails, address issues before proceeding
- Quality gates can be customized per project, but core criteria should remain
- Document any exceptions or modifications to standard gates

