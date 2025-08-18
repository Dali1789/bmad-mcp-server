#!/usr/bin/env python3
"""
BMAD MCP Server - Real World Project Example

This example demonstrates a complete project workflow using BMAD methodology
for developing a web application with user authentication, API, and frontend.
"""

import time
from datetime import datetime, timedelta

def print_header(title):
    """Print a formatted section header"""
    print(f"\n{'='*50}")
    print(f" {title}")
    print(f"{'='*50}\n")

def print_step(step_num, description):
    """Print a formatted step"""
    print(f"{step_num:2d}. {description}")

# Real-world project: E-Commerce Platform
print_header("BMAD Real-World Project: E-Commerce Platform")

print("Project: Building a modern e-commerce platform")
print("Team: 5 BMAD agents working collaboratively")
print("Timeline: 8 weeks development cycle")
print("Features: User auth, product catalog, shopping cart, payments\n")

# Phase 1: Project Planning & Architecture
print_header("Phase 1: Project Planning & Architecture")

print_step(1, "Activate Business Analyst for requirements gathering")
# bmad_activate_agent(agent="analyst")

print_step(2, "Create business analysis tasks")
analysis_tasks = [
    {
        "task_id": "market-research", 
        "name": "E-commerce market research and competitor analysis",
        "allocated_hours": 8.0,
        "agent": "analyst"
    },
    {
        "task_id": "user-personas",
        "name": "Define user personas and customer journey",
        "allocated_hours": 6.0, 
        "agent": "analyst"
    },
    {
        "task_id": "requirements-spec",
        "name": "Create detailed requirements specification",
        "allocated_hours": 12.0,
        "agent": "analyst"
    }
]

for task in analysis_tasks:
    # bmad_create_task(**task)
    print(f"   → Created: {task['name']} ({task['allocated_hours']}h)")

print_step(3, "Switch to System Architect for technical planning")
# bmad_activate_agent(agent="architect")

print_step(4, "Create architecture and design tasks")
architecture_tasks = [
    {
        "task_id": "system-architecture",
        "name": "Design overall system architecture and tech stack",
        "allocated_hours": 10.0,
        "agent": "architect"
    },
    {
        "task_id": "database-design",
        "name": "Design database schema and relationships", 
        "allocated_hours": 8.0,
        "agent": "architect"
    },
    {
        "task_id": "api-specification",
        "name": "Create RESTful API specification",
        "allocated_hours": 6.0,
        "agent": "architect"
    },
    {
        "task_id": "security-architecture",
        "name": "Design security architecture and authentication flow",
        "allocated_hours": 8.0,
        "agent": "architect"
    }
]

for task in architecture_tasks:
    # bmad_create_task(**task)
    print(f"   → Created: {task['name']} ({task['allocated_hours']}h)")

print_step(5, "Generate architecture documentation")
architecture_docs = [
    {
        "template": "system-architecture",
        "data": {
            "project_name": "E-Commerce Platform",
            "tech_stack": "React + Node.js + PostgreSQL",
            "deployment": "Docker + AWS"
        }
    },
    {
        "template": "api-specification", 
        "data": {
            "version": "v1",
            "base_url": "/api/v1",
            "authentication": "JWT Bearer Token"
        }
    }
]

for doc in architecture_docs:
    # bmad_create_document(**doc)
    print(f"   → Generated: {doc['template']} documentation")

# Phase 2: Backend Development
print_header("Phase 2: Backend Development")

print_step(6, "Activate Developer agent for implementation")
# bmad_activate_agent(agent="dev")

print_step(7, "Create backend development tasks")
backend_tasks = [
    {
        "task_id": "project-setup",
        "name": "Initialize Node.js project and development environment",
        "allocated_hours": 4.0,
        "agent": "dev"
    },
    {
        "task_id": "database-implementation",
        "name": "Implement database models and migrations",
        "allocated_hours": 12.0,
        "agent": "dev"
    },
    {
        "task_id": "auth-system",
        "name": "Implement JWT authentication system",
        "allocated_hours": 16.0,
        "agent": "dev"
    },
    {
        "task_id": "user-management",
        "name": "Create user registration and profile management",
        "allocated_hours": 10.0,
        "agent": "dev"
    },
    {
        "task_id": "product-api",
        "name": "Implement product catalog API endpoints",
        "allocated_hours": 14.0,
        "agent": "dev"
    },
    {
        "task_id": "cart-api",
        "name": "Implement shopping cart and order management",
        "allocated_hours": 16.0,
        "agent": "dev"
    },
    {
        "task_id": "payment-integration",
        "name": "Integrate Stripe payment processing",
        "allocated_hours": 12.0,
        "agent": "dev"
    }
]

for task in backend_tasks:
    # bmad_create_task(**task)
    print(f"   → Created: {task['name']} ({task['allocated_hours']}h)")

print_step(8, "Start real-time monitoring for development phase")
# bmad_start_realtime_mode()
print("   → Live monitoring activated for development phase")

print_step(9, "Simulate development work sessions")
development_sessions = [
    ("project-setup", 4.0, "Environment configuration and initial setup"),
    ("database-implementation", 6.0, "Database schema and model implementation"),
    ("auth-system", 8.0, "JWT authentication and middleware"),
    ("user-management", 5.0, "User registration and profile APIs")
]

for task_id, hours, description in development_sessions:
    print(f"   → Working on {task_id}: {description}")
    # bmad_start_work_session(task_id=task_id)
    print(f"     • Session started for {hours} hours")
    # Simulate work time
    # bmad_update_task_progress(task_id=task_id, hours_completed=hours)
    # bmad_end_work_session(task_id=task_id, hours_worked=hours)
    print(f"     • Session completed: {hours}h logged")

# Phase 3: Quality Assurance
print_header("Phase 3: Quality Assurance")

print_step(10, "Activate QA agent for testing strategy")
# bmad_activate_agent(agent="qa")

print_step(11, "Create QA and testing tasks")
qa_tasks = [
    {
        "task_id": "test-strategy",
        "name": "Develop comprehensive testing strategy",
        "allocated_hours": 6.0,
        "agent": "qa"
    },
    {
        "task_id": "unit-tests",
        "name": "Write unit tests for core functionality",
        "allocated_hours": 20.0,
        "agent": "qa"
    },
    {
        "task_id": "integration-tests",
        "name": "Create API integration test suite",
        "allocated_hours": 16.0,
        "agent": "qa"
    },
    {
        "task_id": "security-testing",
        "name": "Perform security testing and vulnerability assessment",
        "allocated_hours": 12.0,
        "agent": "qa"
    },
    {
        "task_id": "performance-testing",
        "name": "Load testing and performance optimization",
        "allocated_hours": 10.0,
        "agent": "qa"
    }
]

for task in qa_tasks:
    # bmad_create_task(**task)
    print(f"   → Created: {task['name']} ({task['allocated_hours']}h)")

print_step(12, "Run quality assurance checklists")
qa_checklists = [
    {"checklist": "code-quality", "target": "backend-api"},
    {"checklist": "security-review", "target": "authentication-system"},
    {"checklist": "performance-review", "target": "api-endpoints"}
]

for checklist in qa_checklists:
    # bmad_run_checklist(**checklist)
    print(f"   → Executed: {checklist['checklist']} for {checklist['target']}")

# Phase 4: Frontend Development
print_header("Phase 4: Frontend Development")

print_step(13, "Create frontend development tasks")
frontend_tasks = [
    {
        "task_id": "react-setup",
        "name": "Initialize React application with TypeScript",
        "allocated_hours": 4.0,
        "agent": "dev"
    },
    {
        "task_id": "ui-components",
        "name": "Create reusable UI component library",
        "allocated_hours": 16.0,
        "agent": "dev"
    },
    {
        "task_id": "auth-frontend",
        "name": "Implement login/register user interface",
        "allocated_hours": 10.0,
        "agent": "dev"
    },
    {
        "task_id": "product-catalog-ui",
        "name": "Create product browsing and search interface",
        "allocated_hours": 14.0,
        "agent": "dev"
    },
    {
        "task_id": "shopping-cart-ui",
        "name": "Implement shopping cart and checkout flow",
        "allocated_hours": 12.0,
        "agent": "dev"
    },
    {
        "task_id": "user-dashboard",
        "name": "Create user profile and order history dashboard",
        "allocated_hours": 10.0,
        "agent": "dev"
    }
]

for task in frontend_tasks:
    # bmad_create_task(**task)
    print(f"   → Created: {task['name']} ({task['allocated_hours']}h)")

# Phase 5: Project Management & Coordination
print_header("Phase 5: Project Management & Coordination")

print_step(14, "Activate Project Manager for coordination")
# bmad_activate_agent(agent="pm")

print_step(15, "Create project management tasks")
pm_tasks = [
    {
        "task_id": "sprint-planning",
        "name": "Plan development sprints and milestones",
        "allocated_hours": 8.0,
        "agent": "pm"
    },
    {
        "task_id": "risk-assessment",
        "name": "Identify and mitigate project risks",
        "allocated_hours": 6.0,
        "agent": "pm"
    },
    {
        "task_id": "team-coordination",
        "name": "Coordinate between different development phases",
        "allocated_hours": 12.0,
        "agent": "pm"
    },
    {
        "task_id": "deployment-planning",
        "name": "Plan production deployment strategy",
        "allocated_hours": 8.0,
        "agent": "pm"
    },
    {
        "task_id": "documentation-management",
        "name": "Ensure comprehensive project documentation",
        "allocated_hours": 10.0,
        "agent": "pm"
    }
]

for task in pm_tasks:
    # bmad_create_task(**task)
    print(f"   → Created: {task['name']} ({task['allocated_hours']}h)")

print_step(16, "Get comprehensive project status")
# bmad_get_project_status()
print("   → Project overview with agent workload distribution")
print("   → Phase completion progress and timeline")
print("   → Resource allocation and capacity planning")

print_step(17, "Sync project with Notion for team collaboration")
# bmad_sync_notion_tasks()
print("   → All tasks synchronized with Notion workspace")
print("   → Team members can track progress and collaborate")

# Phase 6: Monitoring & Optimization
print_header("Phase 6: Monitoring & Optimization")

print_step(18, "Start comprehensive project monitoring")
# bmad_start_task_monitoring()
print("   → Background monitoring activated")
print("   → Daily progress reports enabled")
print("   → Automatic follow-up task generation")

print_step(19, "Simulate project progression")
# bmad_simulate_work_day(speed_factor=5.0)
print("   → Simulating realistic project progression")
print("   → Testing timeline and resource allocation")

print_step(20, "Get intelligent task suggestions")
for agent in ["analyst", "architect", "dev", "qa", "pm"]:
    # bmad_suggest_next_tasks(agent=agent)
    print(f"   → {agent.upper()}: AI-powered task recommendations")

print_step(21, "Generate project reports and metrics")
# bmad_get_task_summary()
print("   → Comprehensive project summary generated")
print("   → Progress metrics and completion rates")
print("   → Resource utilization and efficiency metrics")

# Final Project Overview
print_header("Project Summary")

project_stats = {
    "total_tasks": 35,
    "total_hours": 280,
    "agents_involved": 5,
    "phases_completed": 6,
    "estimated_duration": "8 weeks",
    "technologies": ["React", "Node.js", "PostgreSQL", "JWT", "Stripe"],
    "deliverables": [
        "Market research and requirements",
        "System architecture documentation", 
        "Complete backend API",
        "React frontend application",
        "Comprehensive test suite",
        "Deployment documentation"
    ]
}

print("Final Project Statistics:")
for key, value in project_stats.items():
    if isinstance(value, list):
        print(f"• {key.replace('_', ' ').title()}:")
        for item in value:
            print(f"  - {item}")
    else:
        print(f"• {key.replace('_', ' ').title()}: {value}")

print("\nKey Benefits of BMAD Methodology:")
print("✅ Clear agent specialization and role separation")
print("✅ Intelligent task scheduling and dependency management")
print("✅ Real-time progress tracking and monitoring")
print("✅ Automated quality assurance and testing workflows")
print("✅ Comprehensive documentation and knowledge management")
print("✅ Cross-IDE accessibility and team collaboration")
print("✅ AI-powered task suggestions and optimization")

print("\nProject successfully demonstrates BMAD's capability for:")
print("• Complex multi-phase project management")
print("• Coordinated multi-agent workflows") 
print("• Real-time monitoring and adaptation")
print("• Quality-driven development processes")
print("• Comprehensive documentation and reporting")

print(f"\n{'='*50}")
print(" Real-World Project Example Complete")
print(f"{'='*50}")
print("\nThis example can be adapted for any software project by:")
print("1. Adjusting task definitions and time allocations")
print("2. Customizing agent assignments based on team skills")
print("3. Modifying phases to match project methodology")
print("4. Integrating with specific tools and platforms")
print("5. Scaling task complexity based on project size")