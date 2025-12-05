# Architecture and Design Patterns - AIDD Methodology

## Overview

This document describes technology-agnostic architecture and design patterns that can be applied across different programming languages and frameworks. These patterns provide reusable solutions to common software design problems.

## Architectural Patterns

### Layered Architecture

**Intent**: Organize code into layers with clear separation of concerns.

**Structure**:
```
┌─────────────────┐
│  Presentation   │  (User Interface / API Endpoints)
├─────────────────┤
│   Application   │  (Business Logic / Use Cases)
├─────────────────┤
│    Domain       │  (Business Entities / Rules)
├─────────────────┤
│ Infrastructure  │  (Data Access / External Services)
└─────────────────┘
```

**Principles**:
- Each layer only depends on layers below it
- Domain layer has no external dependencies
- Presentation layer orchestrates application layer

**When to Use**:
- Building enterprise applications
- Need clear separation between business logic and technical concerns
- Multiple interfaces to the same business logic

---

### Repository Pattern

**Intent**: Abstract data access logic and provide a collection-like interface for domain objects.

**Structure**:
```
Repository Interface
    ↓
Repository Implementation
    ↓
Data Store
```

**Benefits**:
- Decouples business logic from data access
- Makes testing easier (can mock repositories)
- Provides consistent interface for data operations

**Key Operations**:
- Create, Read, Update, Delete (CRUD)
- Query operations (find, filter, search)
- Batch operations when needed

**When to Use**:
- Need to abstract data access
- Want to switch data storage technologies
- Need to test business logic without database

---

### Service Layer Pattern

**Intent**: Encapsulate business logic in service objects that coordinate between repositories and domain entities.

**Structure**:
```
Controller/API
    ↓
Service Layer (Business Logic)
    ↓
Repository Layer (Data Access)
```

**Responsibilities**:
- Orchestrate business operations
- Validate business rules
- Coordinate multiple repositories
- Handle transactions

**When to Use**:
- Complex business logic that spans multiple entities
- Need to coordinate multiple data sources
- Want to separate business logic from controllers

---

### Dependency Injection

**Intent**: Provide dependencies to classes from external sources rather than creating them internally.

**Benefits**:
- Loose coupling between components
- Easier testing (can inject mocks)
- Flexible configuration
- Better separation of concerns

**When to Use**:
- Building modular applications
- Need to swap implementations
- Want testable code

---

### API Gateway Pattern

**Intent**: Provide a single entry point for all client requests, routing them to appropriate backend services.

**Structure**:
```
Clients → API Gateway → [Service A, Service B, Service C]
```

**Benefits**:
- Single point of entry for clients
- Can handle cross-cutting concerns (auth, logging, rate limiting)
- Can aggregate responses from multiple services

**When to Use**:
- Microservices architecture
- Multiple backend services
- Need centralized authentication/authorization
- Need request aggregation

---

### Command Query Responsibility Segregation (CQRS)

**Intent**: Separate read and write operations into different models and potentially different data stores.

**Structure**:
```
Write Model → Command Handler → Write Store
Read Model  → Query Handler   → Read Store
```

**When to Use**:
- Different read and write patterns
- Need to optimize reads independently of writes
- Complex domain with different views of data

---

## Design Patterns

### Factory Pattern

**Intent**: Create objects without specifying the exact class of object that will be created.

**Use Cases**:
- Creating objects based on configuration
- Deciding object type at runtime
- Simplifying object creation logic

---

### Strategy Pattern

**Intent**: Define a family of algorithms, encapsulate each one, and make them interchangeable.

**Use Cases**:
- Multiple ways to perform a task
- Need to switch algorithms at runtime
- Want to avoid conditional logic for algorithm selection

---

### Observer Pattern

**Intent**: Define a one-to-many dependency between objects so that when one object changes state, all dependents are notified.

**Use Cases**:
- Event-driven architectures
- Need to notify multiple objects of state changes
- Decoupling event producers from consumers

---

### Decorator Pattern

**Intent**: Attach additional responsibilities to objects dynamically.

**Use Cases**:
- Adding features to objects without modifying them
- Need to combine behaviors flexibly
- Cross-cutting concerns (logging, caching, validation)

---

### Adapter Pattern

**Intent**: Convert the interface of a class into another interface clients expect.

**Use Cases**:
- Integrating with external libraries
- Wrapping legacy code
- Making incompatible interfaces work together

---

## Testing Patterns

### Arrange-Act-Assert (AAA)

**Structure**:
```plaintext
Arrange: Set up test data and dependencies
Act: Execute the code under test
Assert: Verify the expected outcome
```

**Benefits**:
- Clear test structure
- Easy to understand
- Separates setup, execution, and verification

---

### Test Double Patterns

**Dummy**: Placeholder objects passed but never used
**Fake**: Working implementation with simplified behavior
**Stub**: Returns predetermined responses
**Mock**: Verifies interactions and expectations
**Spy**: Records interactions for later verification

**When to Use**:
- **Stub**: When you need to control return values
- **Mock**: When you need to verify interactions
- **Fake**: When you need a working but simplified implementation

---

### Test Isolation

**Principles**:
- Each test is independent
- Tests can run in any order
- No shared state between tests
- Tests clean up after themselves

**Implementation**:
- Use setup/teardown methods
- Create fresh test data for each test
- Mock external dependencies
- Reset state between tests

---

### Boundary Value Testing

**Strategy**: Test at the boundaries of input ranges.

**Test Cases**:
- Minimum value
- Maximum value
- Just below minimum
- Just above maximum
- Valid middle values
- Invalid out-of-range values

---

## Data Access Patterns

### Unit of Work Pattern

**Intent**: Maintain a list of objects affected by a business transaction and coordinate writing out changes.

**Benefits**:
- Manages database transactions
- Tracks changes to entities
- Ensures consistency

**When to Use**:
- Multiple repository operations in one transaction
- Need to ensure atomic operations
- Complex business transactions

---

### Specification Pattern

**Intent**: Encapsulate business rules that determine if an object satisfies certain criteria.

**Benefits**:
- Reusable business rules
- Composable criteria
- Testable rules independently

**When to Use**:
- Complex query logic
- Reusable business rules
- Need to combine multiple criteria

---

## API Design Patterns

### RESTful API Design

**Principles**:
- Resources are nouns (e.g., `/users`, `/orders`)
- HTTP methods indicate actions (GET, POST, PUT, DELETE)
- Stateless requests
- Use HTTP status codes appropriately
- Version APIs when needed

**Response Structure**:
```json
{
  "data": {...},
  "meta": {...},
  "links": {...},
  "errors": [...]
}
```

---

### Pagination Patterns

**Offset-Based**:
```
GET /items?page=1&limit=20
```

**Cursor-Based**:
```
GET /items?cursor=abc123&limit=20
```

**When to Use**:
- **Offset**: Simple, works for small datasets
- **Cursor**: Better for large datasets, consistent results

---

### Error Handling Patterns

**Structure**:
```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable message",
    "details": {...},
    "request_id": "unique-id"
  }
}
```

**Principles**:
- Consistent error format
- Appropriate HTTP status codes
- Include request ID for tracking
- Don't expose sensitive information

---

## Documentation Patterns

### Inline Documentation

**What to Document**:
- Public APIs and interfaces
- Complex algorithms and business logic
- Non-obvious design decisions
- Usage examples for public APIs

**What NOT to Document**:
- Obvious code (self-explanatory)
- Implementation details (unless public API)
- Temporary workarounds (fix the code instead)

---

### API Documentation Structure

**Required Sections**:
1. Overview and purpose
2. Authentication/Authorization
3. Endpoints with request/response examples
4. Error responses
5. Rate limiting and constraints
6. Changelog and versioning

---

## Common Patterns by Concern

### Validation Patterns

- **Input Validation**: Validate at boundaries (API, UI)
- **Business Rule Validation**: Validate in domain/service layer
- **Constraint Validation**: Validate at data layer
- **Early Validation**: Fail fast, validate early

---

### Error Handling Patterns

- **Fail Fast**: Detect errors early
- **Return Errors, Don't Throw**: For expected errors
- **Throw Exceptions**: For unexpected errors
- **Error Context**: Include relevant context in errors
- **Error Logging**: Log errors with context for debugging

---

### Performance Patterns

- **Caching**: Cache frequently accessed data
- **Lazy Loading**: Load data when needed
- **Eager Loading**: Load related data upfront
- **Pagination**: Limit result sets
- **Batch Operations**: Group multiple operations

---

## Pattern Selection Guidelines

1. **Understand the Problem**: Know what problem you're solving
2. **Keep It Simple**: Choose the simplest pattern that works
3. **Consider Trade-offs**: Patterns have benefits and costs
4. **Be Consistent**: Use the same patterns throughout the project
5. **Document Decisions**: Explain why you chose a pattern

## Anti-Patterns to Avoid

- **God Object**: Classes with too many responsibilities
- **Anemic Domain Model**: Domain objects with no behavior
- **Circular Dependencies**: Modules depending on each other
- **Premature Optimization**: Optimizing before understanding needs
- **Copy-Paste Programming**: Duplicating code instead of abstracting

## Notes

- Patterns are tools, not goals
- Adapt patterns to your specific needs
- Combine patterns when appropriate
- Document pattern usage in your project
- Review and refactor to improve pattern implementation
