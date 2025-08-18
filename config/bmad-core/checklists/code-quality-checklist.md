# Code Quality Checklist

## Pre-Development
- [ ] Requirements klar definiert und verstanden
- [ ] Technical Design dokumentiert
- [ ] Development Environment setup
- [ ] Git Branch erstellt (feature/task-name)
- [ ] Dependencies und Libraries identifiziert

## During Development
- [ ] Code follows established conventions
- [ ] Variable und Function Names sind beschreibend
- [ ] No hardcoded values (use configuration)
- [ ] Error handling implementiert
- [ ] Security best practices befolgt
- [ ] Performance considerations berücksichtigt

## Code Structure
- [ ] Functions sind single-purpose und klein
- [ ] Code ist DRY (Don't Repeat Yourself)
- [ ] SOLID principles befolgt
- [ ] Proper separation of concerns
- [ ] Consistent indentation und formatting

## Testing
- [ ] Unit Tests geschrieben für neue Funktionalität
- [ ] Test Coverage mindestens 80%
- [ ] Edge Cases getestet
- [ ] Integration Tests wo erforderlich
- [ ] Manual Testing durchgeführt

## Documentation
- [ ] Inline Code Comments wo nötig
- [ ] README.md aktualisiert
- [ ] API Documentation aktualisiert
- [ ] Changelog Entry erstellt
- [ ] Architecture Decision Records (ADRs) wo nötig

## Security
- [ ] Input Validation implementiert
- [ ] SQL Injection Prevention
- [ ] XSS Protection
- [ ] Authentication/Authorization korrekt
- [ ] Sensitive Data nicht in Logs
- [ ] Dependencies Security Scan durchgeführt

## Performance
- [ ] Database Queries optimiert
- [ ] Caching implementiert wo sinnvoll
- [ ] Large datasets paginiert
- [ ] Memory leaks vermieden
- [ ] Performance Tests durchgeführt

## Code Review Preparation
- [ ] Self-review durchgeführt
- [ ] Linting ohne Errors
- [ ] All Tests passing
- [ ] Build successful
- [ ] Commit Messages sind beschreibend

## Pre-Merge
- [ ] Code Review approved
- [ ] All discussions resolved
- [ ] Branch up-to-date with main
- [ ] Merge conflicts resolved
- [ ] CI/CD Pipeline successful

## Post-Merge
- [ ] Deployment erfolgreich
- [ ] Smoke Tests bestanden
- [ ] Monitoring und Logging aktiv
- [ ] Stakeholders informiert
- [ ] Documentation deployed

## Quality Metrics
- [ ] Code Coverage: ____% (Ziel: >80%)
- [ ] Complexity Score: ____ (Ziel: <10)
- [ ] Technical Debt: ____ (Ziel: minimiert)
- [ ] Performance Benchmark: ____ (Ziel: <2s Response Time)

## Agent Responsibilities

### BMAD Dev
- [ ] Code Implementation Quality
- [ ] Unit Testing Complete
- [ ] Linting und Formatting
- [ ] Basic Documentation

### BMAD Architect
- [ ] Architecture Review
- [ ] Design Pattern Compliance
- [ ] Scalability Assessment
- [ ] Security Architecture

### BMAD QA
- [ ] Test Plan Review
- [ ] Integration Testing
- [ ] Performance Testing
- [ ] Bug Verification

### BMAD PM
- [ ] Requirements Traceability
- [ ] Timeline Adherence
- [ ] Stakeholder Communication
- [ ] Risk Assessment

---
*BMAD Code Quality Standards v2.0*