# BMAD MCP Server - API Reference

Complete reference for all available MCP tools and their parameters.

## 🤖 Agent Management Tools

### `bmad_list_agents`
**Description**: List all available BMAD agents with their capabilities.

**Parameters**: None

**Returns**: Formatted list of agents with:
- Agent ID and name
- Specialization and use cases
- Model configuration
- Current status

**Example Response**:
```
🤖 Available BMAD Agents

1. 📊 Business Analyst (analyst)
   - ID: analyst
   - Model: perplexity/llama-3.1-sonar-large-128k-online
   - Use For: Business analysis, market research, requirement gathering

2. 🏗️ System Architect (architect)
   - ID: architect  
   - Model: anthropic/claude-3-opus
   - Use For: System design, architecture planning, tech selection
```

### `bmad_activate_agent`
**Description**: Activate a specific BMAD agent for subsequent operations.

**Parameters**:
- `agent` (string, required): Agent ID (`analyst`, `architect`, `dev`, `pm`, `qa`)

**Returns**: Confirmation of agent activation with context information.

**Example**:
```python
bmad_activate_agent(agent="dev")
```

### `bmad_get_agent_help`
**Description**: Get help and guidance for current or specified agent.

**Parameters**:
- `agent` (string, optional): Specific agent ID, defaults to current agent

**Returns**: Agent-specific help, capabilities, and best practices.

## 📋 Task Management Tools

### `bmad_get_task_summary`
**Description**: Get comprehensive overview of all tasks and project status.

**Parameters**: None

**Returns**: Detailed summary including:
- Task counts by status
- Progress percentages
- Today's workload
- Capacity utilization

**Example Response**:
```
📊 BMAD Task Summary

Overall Progress:
• Total Tasks: 12 (75% complete)
• Completed: 9 | In Progress: 2 | Pending: 1
• Hours: 45.5/60.0 (76%)

Today's Summary:
• Tasks: 3 tasks scheduled
• Hours: 6.5h (65% capacity)
```

### `bmad_create_task`
**Description**: Create a new task with intelligent scheduling.

**Parameters**:
- `task_id` (string, required): Unique task identifier
- `name` (string, required): Task name/description
- `allocated_hours` (float, required): Total hours needed
- `agent` (string, optional): Assigned agent
- `start_date` (string, optional): Start date (YYYY-MM-DD)

**Returns**: Task creation confirmation with scheduling details.

**Example**:
```python
bmad_create_task(
    task_id="auth-system",
    name="Implement user authentication",
    allocated_hours=12.0,
    agent="dev",
    start_date="2025-01-20"
)
```

### `bmad_update_task_progress`
**Description**: Update task progress with real-time sync.

**Parameters**:
- `task_id` (string, required): Task identifier
- `hours_completed` (float, required): Hours to add to progress

**Returns**: Updated progress information and completion status.

**Example**:
```python
bmad_update_task_progress(
    task_id="auth-system",
    hours_completed=2.5
)
```

### `bmad_get_today_tasks`
**Description**: Get all tasks scheduled for today.

**Parameters**: None

**Returns**: Today's task list with:
- Task names and status
- Allocated hours for today
- Agent assignments
- Priority order

### `bmad_get_agent_tasks`
**Description**: Get all tasks assigned to a specific agent.

**Parameters**:
- `agent` (string, required): Agent ID

**Returns**: Agent-specific task list with progress and status.

**Example**:
```python
bmad_get_agent_tasks(agent="dev")
```

### `bmad_set_task_status`
**Description**: Set task status manually.

**Parameters**:
- `task_id` (string, required): Task identifier
- `status` (string, required): New status (`pending`, `in_progress`, `completed`, `blocked`)

**Returns**: Status update confirmation.

### `bmad_delete_task`
**Description**: Delete a task from the system.

**Parameters**:
- `task_id` (string, required): Task identifier

**Returns**: Deletion confirmation.

## ⚡ Enhanced Features

### `bmad_start_realtime_mode`
**Description**: Enable real-time task monitoring with live updates.

**Parameters**: None

**Returns**: Live monitoring startup confirmation and status.

**Features**:
- Background progress tracking
- Work session monitoring
- Automatic reminders
- Performance metrics

### `bmad_stop_realtime_mode`
**Description**: Disable real-time monitoring.

**Parameters**: None

**Returns**: Session summary with metrics.

### `bmad_start_work_session`
**Description**: Start tracking a work session for a specific task.

**Parameters**:
- `task_id` (string, required): Task identifier

**Returns**: Work session started confirmation with context.

**Example**:
```python
bmad_start_work_session(task_id="auth-system")
```

### `bmad_end_work_session`
**Description**: End work session and log hours.

**Parameters**:
- `task_id` (string, required): Task identifier
- `hours_worked` (float, optional): Manual hours override

**Returns**: Session summary and progress update.

### `bmad_get_active_sessions`
**Description**: View all currently active work sessions.

**Parameters**: None

**Returns**: List of active sessions with duration and progress.

### `bmad_get_realtime_status`
**Description**: Get comprehensive real-time monitoring status.

**Parameters**: None

**Returns**: Detailed status including:
- Active sessions
- Monitoring state
- Daily metrics
- Performance indicators

## 🧪 Simulation & Testing

### `bmad_simulate_work_day`
**Description**: Simulate a complete work day with realistic task progression.

**Parameters**:
- `speed_factor` (float, optional): Simulation speed multiplier (default: 1.0)

**Returns**: Work day simulation results with progression details.

**Example**:
```python
bmad_simulate_work_day(speed_factor=10.0)  # 10x speed
```

### `bmad_simulate_task_progression`
**Description**: Simulate realistic task progression.

**Parameters**:
- `task_id` (string, required): Task to simulate
- `target_hours` (float, required): Hours to simulate

**Returns**: Task progression simulation results.

### `bmad_simulate_agent_workday`
**Description**: Simulate a full workday for specific agent.

**Parameters**:
- `agent` (string, required): Agent ID
- `hours` (float, optional): Workday length (default: 8.0)

**Returns**: Agent workday simulation with productivity metrics.

### `bmad_simulate_crisis_scenario`
**Description**: Simulate crisis scenarios and recovery patterns.

**Parameters**:
- `crisis_type` (string, optional): Crisis type (`blocked_task`, `resource_conflict`, `deadline_pressure`)

**Returns**: Crisis simulation results and recovery recommendations.

## 🔧 Project Management

### `bmad_detect_project`
**Description**: Scan directory for BMAD project configuration.

**Parameters**:
- `path` (string, optional): Directory path (default: current directory)

**Returns**: Project detection results and configuration details.

### `bmad_register_project`
**Description**: Register project in global registry for cross-IDE access.

**Parameters**:
- `project_path` (string, required): Project directory path
- `project_name` (string, optional): Custom project name

**Returns**: Project registration confirmation.

### `bmad_get_project_status`
**Description**: Get comprehensive project status overview.

**Parameters**: None

**Returns**: Detailed project status including:
- Task distribution by agent
- Phase completion progress
- Resource allocation
- Timeline information

### `bmad_execute_task`
**Description**: Execute BMAD methodology tasks.

**Parameters**:
- `task` (string, required): Task template name
- `parameters` (object, optional): Task-specific parameters

**Returns**: Task execution results.

### `bmad_create_document`
**Description**: Generate documents using BMAD templates.

**Parameters**:
- `template` (string, required): Template name
- `data` (object, optional): Template data

**Returns**: Document generation results.

### `bmad_run_checklist`
**Description**: Execute quality assurance checklists.

**Parameters**:
- `checklist` (string, required): Checklist name
- `target` (string, optional): Target for validation

**Returns**: Checklist execution results.

## 🔄 Synchronization

### `bmad_sync_notion_tasks`
**Description**: Synchronize tasks with Notion databases.

**Parameters**: None

**Returns**: Synchronization results with success/failure counts.

**Requirements**: `NOTION_TOKEN` environment variable

### `bmad_start_task_monitoring`
**Description**: Start background task monitoring system.

**Parameters**: None

**Returns**: Monitoring activation confirmation.

**Features**:
- 30-minute progress checks
- Daily reports at 18:00
- Automatic follow-up generation

### `bmad_stop_task_monitoring`
**Description**: Stop background monitoring.

**Parameters**: None

**Returns**: Monitoring deactivation confirmation.

## 🕒 Time Management

### `bmad_manual_reminder_check`
**Description**: Manually trigger reminder system.

**Parameters**: None

**Returns**: Reminder check results and actions taken.

### `bmad_manual_progress_check`
**Description**: Manually trigger progress validation.

**Parameters**: None

**Returns**: Progress check results and recommendations.

### `bmad_manual_daily_report`
**Description**: Generate daily progress report.

**Parameters**: None

**Returns**: Comprehensive daily summary.

### `bmad_get_todays_schedule`
**Description**: Get today's complete reminder and task schedule.

**Parameters**: None

**Returns**: Detailed daily schedule with times and priorities.

## 💡 Task Suggestions

### `bmad_suggest_next_tasks`
**Description**: Get intelligent task suggestions.

**Parameters**:
- `agent` (string, optional): Agent-specific suggestions

**Returns**: List of suggested next tasks based on:
- Current progress
- Dependencies
- Agent capacity
- Project priorities

## 🔧 Advanced Configuration

### `bmad_query_with_model`
**Description**: Execute queries using agent-specific model routing.

**Parameters**:
- `query` (string, required): Query to execute
- `agent` (string, optional): Target agent
- `context` (object, optional): Additional context

**Returns**: Model response with agent context.

**Example**:
```python
bmad_query_with_model(
    query="How should I structure the authentication system?",
    agent="architect",
    context={"project_type": "web_app", "user_count": "10000+"}
)
```

## Error Handling

All tools return structured error messages when:
- Required parameters are missing
- Invalid agent IDs are provided
- Tasks are not found
- API keys are not configured

**Example Error Response**:
```
❌ Task not found: invalid-task-id

Available tasks:
• auth-system (in_progress)
• user-dashboard (pending)
• api-endpoints (completed)
```

## Rate Limits & Performance

- **Task Operations**: No limits for local operations
- **Model Queries**: Subject to OpenRouter API limits
- **Notion Sync**: Rate limited to prevent API exhaustion
- **Real-time Updates**: Optimized for minimal resource usage

## Best Practices

1. **Always activate appropriate agent** before complex operations
2. **Use descriptive task IDs** for better project organization
3. **Regular progress updates** for accurate tracking
4. **Leverage simulation tools** for planning and testing
5. **Monitor real-time status** during active development
6. **Sync with Notion regularly** for backup and collaboration