#!/usr/bin/env python3
"""
BMAD MCP Server - Getting Started Example

This example demonstrates the basic usage of BMAD MCP tools
for task management and agent-based workflows.

Prerequisites:
- BMAD MCP Server installed and configured
- OpenRouter API key set in environment
- MCP-compatible IDE (Claude Code, VS Code, etc.)
"""

# Example 1: Basic Agent Management
print("=== BMAD Getting Started Example ===\n")

# List all available agents
print("1. Listing available agents:")
# bmad_list_agents()
print("   → Shows 5 specialized agents with their capabilities\n")

# Activate a specific agent
print("2. Activating developer agent:")
# bmad_activate_agent(agent="dev")
print("   → Developer agent activated for coding tasks\n")

# Get agent-specific help
print("3. Getting agent help:")
# bmad_get_agent_help(agent="dev")
print("   → Shows developer-specific guidance and best practices\n")


# Example 2: Task Management Workflow
print("=== Task Management Workflow ===\n")

# Create a new development task
print("4. Creating a new task:")
task_config = {
    "task_id": "user-authentication",
    "name": "Implement user authentication system",
    "allocated_hours": 12.0,
    "agent": "dev",
    "start_date": "2025-01-20"
}
# bmad_create_task(**task_config)
print(f"   → Task created: {task_config['name']}")
print(f"   → Allocated: {task_config['allocated_hours']} hours")
print(f"   → Agent: {task_config['agent']}\n")

# Check today's tasks
print("5. Checking today's schedule:")
# bmad_get_today_tasks()
print("   → Shows all tasks scheduled for today with priorities\n")

# Update task progress
print("6. Working on the task and updating progress:")
progress_update = {
    "task_id": "user-authentication",
    "hours_completed": 2.5
}
# bmad_update_task_progress(**progress_update)
print(f"   → Added {progress_update['hours_completed']} hours of progress")
print("   → Task status automatically updated\n")

# Get comprehensive task summary
print("7. Getting project overview:")
# bmad_get_task_summary()
print("   → Shows overall progress, completion rates, and metrics\n")


# Example 3: Real-time Monitoring
print("=== Real-time Monitoring ===\n")

# Start real-time monitoring
print("8. Starting real-time monitoring:")
# bmad_start_realtime_mode()
print("   → Live monitoring activated")
print("   → Background progress tracking enabled\n")

# Start a work session
print("9. Starting work session:")
# bmad_start_work_session(task_id="user-authentication")
print("   → Work session started for user-authentication")
print("   → Time tracking activated\n")

# Simulate some work time...
print("10. Working on the task...")
print("    → [Simulating 2 hours of development work]")
print("    → Implementing login endpoints")
print("    → Writing authentication middleware\n")

# End work session
print("11. Ending work session:")
# bmad_end_work_session(task_id="user-authentication", hours_worked=2.0)
print("    → Work session completed")
print("    → Progress automatically logged\n")

# Check real-time status
print("12. Checking real-time status:")
# bmad_get_realtime_status()
print("    → Shows active sessions, metrics, and performance data\n")


# Example 4: Multi-Agent Workflow
print("=== Multi-Agent Workflow ===\n")

# Switch to architect for design decisions
print("13. Switching to architect agent:")
# bmad_activate_agent(agent="architect")
print("    → Architect agent activated for system design\n")

# Query architect about authentication approach
print("14. Consulting architect about design:")
architecture_query = {
    "query": "What's the best architecture for a scalable authentication system?",
    "agent": "architect",
    "context": {
        "project_type": "web_application",
        "expected_users": "10000+",
        "security_requirements": "high"
    }
}
# bmad_query_with_model(**architecture_query)
print("    → Architect provides detailed architectural recommendations\n")

# Create architecture task
print("15. Creating architecture documentation task:")
arch_task = {
    "task_id": "auth-architecture",
    "name": "Design authentication system architecture",
    "allocated_hours": 4.0,
    "agent": "architect"
}
# bmad_create_task(**arch_task)
print("    → Architecture task created and assigned\n")

# Switch to QA agent for testing strategy
print("16. Switching to QA agent:")
# bmad_activate_agent(agent="qa")
print("    → QA agent activated for testing strategy\n")

# Create testing task
print("17. Creating testing task:")
qa_task = {
    "task_id": "auth-testing",
    "name": "Develop authentication testing strategy",
    "allocated_hours": 6.0,
    "agent": "qa"
}
# bmad_create_task(**qa_task)
print("    → Testing task created and assigned\n")

# View all agent tasks
print("18. Viewing tasks by agent:")
agents = ["dev", "architect", "qa"]
for agent in agents:
    print(f"    → {agent.upper()} tasks:")
    # bmad_get_agent_tasks(agent=agent)
print("\n")


# Example 5: Project Management Features
print("=== Project Management ===\n")

# Detect current project
print("19. Detecting project configuration:")
# bmad_detect_project(path="./")
print("    → Scans for .bmad-core configuration")
print("    → Shows project settings and resources\n")

# Get comprehensive project status
print("20. Getting project status:")
# bmad_get_project_status()
print("    → Shows project overview with:")
print("    → • Task distribution by agent")
print("    → • Phase completion progress")
print("    → • Resource allocation")
print("    → • Timeline information\n")

# Create project documentation
print("21. Creating project documentation:")
doc_config = {
    "template": "project-overview",
    "data": {
        "project_name": "Authentication System",
        "lead_developer": "John Doe",
        "estimated_completion": "2025-02-15"
    }
}
# bmad_create_document(**doc_config)
print("    → Project documentation generated from template\n")

# Run quality checklist
print("22. Running quality checklist:")
checklist_config = {
    "checklist": "code-quality",
    "target": "authentication-module"
}
# bmad_run_checklist(**checklist_config)
print("    → Quality checklist executed")
print("    → Shows compliance status and recommendations\n")


# Example 6: Advanced Features
print("=== Advanced Features ===\n")

# Sync with Notion
print("23. Syncing with Notion:")
# bmad_sync_notion_tasks()
print("    → Tasks synchronized with Notion databases")
print("    → Enables team collaboration and reporting\n")

# Simulate work day for planning
print("24. Simulating work day:")
# bmad_simulate_work_day(speed_factor=10.0)
print("    → Simulates realistic task progression")
print("    → Useful for planning and timeline estimation\n")

# Get task suggestions
print("25. Getting task suggestions:")
# bmad_suggest_next_tasks(agent="dev")
print("    → AI-powered task recommendations")
print("    → Based on project progress and dependencies\n")

# Start background monitoring
print("26. Starting background monitoring:")
# bmad_start_task_monitoring()
print("    → Background monitoring activated")
print("    → Automatic reminders and progress checks")
print("    → Daily reports and follow-up generation\n")

print("=== Example Complete ===")
print("\nThis example demonstrated:")
print("• Basic agent management and activation")
print("• Task creation and progress tracking")
print("• Real-time monitoring and work sessions")
print("• Multi-agent workflows and collaboration")
print("• Project management and documentation")
print("• Advanced features and automation")
print("\nFor more examples, see the examples/ directory")
print("For complete API reference, see docs/api-reference.md")