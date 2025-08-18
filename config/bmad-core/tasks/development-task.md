# Development Task Template

## Task Information
- **Type**: Development
- **Priority**: {{ priority | default("medium") }}
- **Estimated Hours**: {{ estimated_hours | default("TBD") }}
- **Agent**: bmad-dev
- **Status**: {{ status | default("todo") }}

## Description
{{ description | default("Detaillierte Beschreibung der Entwicklungsaufgabe") }}

## Technical Requirements
{{ technical_requirements | default("- Technische Anforderungen definieren") }}

## Acceptance Criteria
{{ acceptance_criteria | default("- [ ] Funktionalität implementiert\n- [ ] Tests geschrieben\n- [ ] Code Review durchgeführt\n- [ ] Dokumentation aktualisiert") }}

## Definition of Done
- [ ] Code implementiert und funktionsfähig
- [ ] Unit Tests geschrieben (Coverage > 80%)
- [ ] Integration Tests erfolgreich
- [ ] Code Review approved
- [ ] Linting ohne Fehler
- [ ] Performance-Tests bestanden
- [ ] Dokumentation aktualisiert
- [ ] Deployment erfolgreich

## Dependencies
{{ dependencies | default("Keine Abhängigkeiten") }}

## Files to Change
{{ files_to_change | default("- Dateien auflisten") }}

## Testing Strategy
{{ testing_strategy | default("- Unit Tests\n- Integration Tests\n- Manual Testing") }}

## Rollback Plan
{{ rollback_plan | default("Rollback-Strategie definieren") }}

## Notes
{{ notes | default("Zusätzliche Notizen") }}

---
*Template für BMAD Development Tasks*