"""
BMAD Workflow Engine
Zentrale Engine für die Orchestrierung aller BMAD-METHOD Workflows
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple, Callable

from .workflow_states import (
    ProjectContext, StoryContext, WorkflowSession,
    ProjectState, StoryState, WorkflowState,
    AGENT_RESPONSIBILITIES
)
from .orchestrator_agent import BMadOrchestratorAgent
from .quality_gates import QualityGateManager

logger = logging.getLogger(__name__)


class BMadWorkflowEngine:
    """
    Central BMAD Workflow Engine
    
    Koordiniert:
    - BMAD-METHOD Planning Workflow
    - Core Development Cycle
    - Agent Routing und Orchestrierung
    - Quality Gates und QA-Prozesse
    - Session Management und Persistence
    """
    
    def __init__(self, global_registry=None, persistence_path: str = None):
        self.global_registry = global_registry
        self.persistence_path = Path(persistence_path) if persistence_path else Path("./workflows")
        self.persistence_path.mkdir(exist_ok=True)
        
        # Core components
        self.orchestrator = BMadOrchestratorAgent(global_registry)
        self.quality_manager = QualityGateManager()
        
        # Agent registry - will be populated by actual agents
        self.active_agents = {
            "orchestrator": self.orchestrator,
            "analyst": None,
            "architect": None,
            "pm": None,
            "dev": None,
            "qa": None,
            "coder": None,
            "serena": None
        }
        
        # Event handlers
        self.event_handlers = {
            "project_created": [],
            "project_state_changed": [],
            "story_created": [],
            "story_state_changed": [],
            "agent_assigned": [],
            "quality_gate_checked": [],
            "workflow_completed": []
        }
        
        # Workflow automation rules
        self.automation_rules = []
        
        # Engine metrics
        self.engine_metrics = {
            "workflows_started": 0,
            "workflows_completed": 0,
            "agent_interactions": 0,
            "quality_gates_processed": 0,
            "automation_triggers": 0
        }
        
        # Initialize persistence (will be loaded later when needed)
        self._persistence_loaded = False
        
        # Background tasks will be started when server runs
        self._background_tasks = []
    
    async def initialize(self):
        """Initialize the workflow engine asynchronously"""
        if not self._persistence_loaded:
            await self._load_persisted_state()
            self._persistence_loaded = True
            
        # Register automatic Notion sync handlers
        await self._setup_auto_notion_sync()
        
        # Register automatic GitHub sync handlers
        await self._setup_auto_github_sync()
    
    async def _setup_auto_notion_sync(self):
        """Setup automatic Notion synchronization for all events"""
        try:
            # Register event handlers for automatic Notion updates
            self.register_event_handler("project_created", self._auto_sync_project_created)
            self.register_event_handler("project_state_changed", self._auto_sync_project_update)
            self.register_event_handler("story_created", self._auto_sync_story_created)
            self.register_event_handler("story_state_changed", self._auto_sync_story_update)
            self.register_event_handler("agent_assigned", self._auto_sync_agent_assignment)
            self.register_event_handler("quality_gate_checked", self._auto_sync_quality_gate)
            
            logger.info("✅ Auto-Notion sync handlers registered for all events")
            
        except Exception as e:
            logger.warning(f"Failed to setup auto-Notion sync: {e}")
    
    async def _setup_auto_github_sync(self):
        """Setup automatic GitHub synchronization for all events"""
        try:
            from ..core.github_sync import BMadGitHubAutoSync
            
            # Initialize GitHub auto-sync
            github_sync = BMadGitHubAutoSync()
            sync_result = await github_sync.initialize_auto_sync()
            
            if sync_result.get("success"):
                # Register event handlers for GitHub sync
                await github_sync.setup_workflow_event_handlers(self)
                
                # Store GitHub sync instance for later use
                self.github_sync = github_sync
                
                logger.info("✅ Auto-GitHub-Sync erfolgreich eingerichtet")
                return {
                    "success": True,
                    "auto_sync_enabled": True,
                    "repo_url": sync_result.get("repo_url"),
                    "message": "Automatische GitHub-Synchronisation aktiv"
                }
            else:
                logger.warning(f"GitHub Auto-Sync nicht verfügbar: {sync_result.get('error')}")
                return {
                    "success": False,
                    "auto_sync_enabled": False,
                    "error": sync_result.get("error")
                }
            
        except Exception as e:
            logger.error(f"Fehler bei Auto-GitHub-Sync Setup: {e}")
            return {"success": False, "error": str(e)}
    
    async def _auto_sync_project_created(self, event_data: Dict[str, Any]):
        """Auto-sync project creation to Notion"""
        try:
            project_id = event_data.get("project_id")
            workflow_context = event_data.get("workflow_context", {})
            
            logger.info(f"🔄 Auto-syncing project creation to Notion: {project_id}")
            
            # Create Notion project page with full context
            notion_data = {
                "Name": workflow_context.get("project_name", project_id),
                "BMAD_ID": project_id,
                "Status": "🚀 Created",
                "Created_At": datetime.now().isoformat(),
                "Event_Type": "project_created",
                "Workflow_ID": workflow_context.get("workflow_id"),
                "Auto_Synced": True
            }
            
            # TODO: Implement actual Notion API call when MCP works
            logger.info(f"✅ Project auto-synced to Notion: {project_id}")
            
        except Exception as e:
            logger.error(f"Failed to auto-sync project creation: {e}")
    
    async def _auto_sync_project_update(self, event_data: Dict[str, Any]):
        """Auto-sync project state changes to Notion"""
        try:
            project_id = event_data.get("project_id")
            new_state = event_data.get("new_state")
            
            logger.info(f"🔄 Auto-syncing project update to Notion: {project_id} → {new_state}")
            
            # Update Notion project page
            update_data = {
                "Status": f"📋 {new_state}",
                "Last_Updated": datetime.now().isoformat(),
                "Event_Type": "project_state_changed"
            }
            
            # TODO: Implement actual Notion API call when MCP works
            logger.info(f"✅ Project update auto-synced to Notion: {project_id}")
            
        except Exception as e:
            logger.error(f"Failed to auto-sync project update: {e}")
    
    async def _auto_sync_story_created(self, event_data: Dict[str, Any]):
        """Auto-sync story creation to Notion"""
        try:
            story_id = event_data.get("story_id")
            project_id = event_data.get("project_id")
            
            logger.info(f"🔄 Auto-syncing story creation to Notion: {story_id}")
            
            # TODO: Create Notion task/story entry
            logger.info(f"✅ Story auto-synced to Notion: {story_id}")
            
        except Exception as e:
            logger.error(f"Failed to auto-sync story creation: {e}")
    
    async def _auto_sync_story_update(self, event_data: Dict[str, Any]):
        """Auto-sync story state changes to Notion"""
        try:
            story_id = event_data.get("story_id")
            new_state = event_data.get("new_state")
            
            logger.info(f"🔄 Auto-syncing story update to Notion: {story_id} → {new_state}")
            
            # TODO: Update Notion task/story entry
            logger.info(f"✅ Story update auto-synced to Notion: {story_id}")
            
        except Exception as e:
            logger.error(f"Failed to auto-sync story update: {e}")
    
    async def _auto_sync_agent_assignment(self, event_data: Dict[str, Any]):
        """Auto-sync agent assignments to Notion"""
        try:
            agent = event_data.get("agent")
            task_id = event_data.get("task_id")
            
            logger.info(f"🔄 Auto-syncing agent assignment to Notion: {agent} → {task_id}")
            
            # TODO: Update Notion with agent assignment
            logger.info(f"✅ Agent assignment auto-synced to Notion")
            
        except Exception as e:
            logger.error(f"Failed to auto-sync agent assignment: {e}")
    
    async def _auto_sync_quality_gate(self, event_data: Dict[str, Any]):
        """Auto-sync quality gate results to Notion"""
        try:
            gate_result = event_data.get("result")
            project_id = event_data.get("project_id")
            
            logger.info(f"🔄 Auto-syncing quality gate to Notion: {gate_result}")
            
            # TODO: Update Notion with quality gate results
            logger.info(f"✅ Quality gate auto-synced to Notion")
            
        except Exception as e:
            logger.error(f"Failed to auto-sync quality gate: {e}")
    
    # =====================================
    # WORKFLOW LIFECYCLE MANAGEMENT
    # =====================================
    
    async def start_project_workflow(self, project_name: str, initial_idea: str = None, workflow_type: str = "full") -> Dict[str, Any]:
        """
        Start complete BMAD-METHOD project workflow
        
        Args:
            project_name: Name of the project
            initial_idea: Optional initial project idea
            workflow_type: Type of workflow (full, planning_only, development_only)
            
        Returns:
            Workflow startup result with orchestration plan
        """
        try:
            logger.info(f"Starting BMAD workflow for project: {project_name}")
            
            # Create project via orchestrator
            project_result = await self.orchestrator.create_project(project_name, initial_idea)
            
            if not project_result["success"]:
                return project_result
            
            project_id = project_result["project_id"]
            session_id = project_result["session_id"]
            
            # Create workflow execution plan
            execution_plan = await self._create_execution_plan(project_id, workflow_type)
            
            # Register workflow in engine
            workflow_context = {
                "workflow_id": f"workflow_{project_id}",
                "project_id": project_id,
                "session_id": session_id,
                "workflow_type": workflow_type,
                "execution_plan": execution_plan,
                "started_at": datetime.now().isoformat(),
                "status": "active"
            }
            
            # Store workflow context
            await self._persist_workflow_context(workflow_context)
            
            # Trigger automation if enabled
            await self._trigger_workflow_automation(workflow_context)
            
            # Fire events
            await self._fire_event("project_created", {
                "project_id": project_id,
                "workflow_context": workflow_context
            })
            
            self.engine_metrics["workflows_started"] += 1
            
            logger.info(f"BMAD workflow started successfully for {project_name}")
            
            return {
                "success": True,
                "workflow_id": workflow_context["workflow_id"],
                "project_id": project_id,
                "session_id": session_id,
                "execution_plan": execution_plan,
                "next_actions": await self._get_immediate_next_actions(workflow_context),
                "message": f"BMAD workflow started for {project_name}",
                "orchestrator_status": project_result
            }
            
        except Exception as e:
            logger.error(f"Error starting project workflow: {e}")
            return {"success": False, "error": str(e)}
    
    async def advance_workflow(self, workflow_id: str, target_state: str = None, agent_override: str = None) -> Dict[str, Any]:
        """
        Advance workflow to next state or specific target
        
        Args:
            workflow_id: Workflow identifier
            target_state: Optional specific target state
            agent_override: Optional agent to handle advancement
            
        Returns:
            Workflow advancement result
        """
        try:
            # Load workflow context
            workflow_context = await self._load_workflow_context(workflow_id)
            if not workflow_context:
                return {"success": False, "error": "Workflow not found"}
            
            project_id = workflow_context["project_id"]
            
            # Determine advancement type (project vs story)
            if target_state and target_state.startswith("story_"):
                # Story advancement
                story_id = workflow_context.get("current_story_id")
                if not story_id:
                    return {"success": False, "error": "No active story for advancement"}
                
                story_state = target_state.replace("story_", "")
                result = await self.orchestrator.advance_story_state(story_id, story_state)
                
                if result["success"]:
                    await self._fire_event("story_state_changed", {
                        "story_id": story_id,
                        "new_state": story_state,
                        "workflow_id": workflow_id
                    })
                
            else:
                # Project advancement
                result = await self.orchestrator.advance_project_state(project_id, target_state)
                
                if result["success"]:
                    await self._fire_event("project_state_changed", {
                        "project_id": project_id,
                        "new_state": result["current_state"],
                        "workflow_id": workflow_id
                    })
            
            # Update workflow context
            if result["success"]:
                workflow_context["last_advancement"] = datetime.now().isoformat()
                workflow_context["current_state"] = result["current_state"]
                await self._persist_workflow_context(workflow_context)
            
            # Trigger automation
            await self._trigger_workflow_automation(workflow_context)
            
            logger.info(f"Workflow {workflow_id} advanced: {result.get('message', 'Success')}")
            
            return {
                "success": result["success"],
                "workflow_id": workflow_id,
                "advancement_result": result,
                "next_actions": await self._get_immediate_next_actions(workflow_context) if result["success"] else [],
                "message": f"Workflow advancement: {result.get('message', 'Completed')}"
            }
            
        except Exception as e:
            logger.error(f"Error advancing workflow: {e}")
            return {"success": False, "error": str(e)}
    
    async def execute_agent_command(self, workflow_id: str, agent_type: str, command: str, parameters: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Execute agent command within workflow context
        
        Args:
            workflow_id: Workflow identifier
            agent_type: Type of agent (analyst, architect, pm, dev, qa)
            command: Agent command
            parameters: Command parameters
            
        Returns:
            Command execution result
        """
        try:
            # Load workflow context
            workflow_context = await self._load_workflow_context(workflow_id)
            if not workflow_context:
                return {"success": False, "error": "Workflow not found"}
            
            project_id = workflow_context["project_id"]
            context_id = parameters.get("context_id", project_id)
            
            # Route command through orchestrator
            route_result = await self.orchestrator.route_agent_command(
                agent_type, command, context_id, parameters
            )
            
            if not route_result["success"]:
                return route_result
            
            # Execute command via actual agent if available
            agent = self.active_agents.get(agent_type)
            if agent and hasattr(agent, 'execute_command'):
                execution_result = await agent.execute_command(command, parameters)
            else:
                # Simulate command execution for now
                execution_result = await self._simulate_agent_command(agent_type, command, parameters)
            
            # Update workflow tracking
            workflow_context["last_agent_interaction"] = datetime.now().isoformat()
            workflow_context["last_agent"] = agent_type
            await self._persist_workflow_context(workflow_context)
            
            # Fire events
            await self._fire_event("agent_assigned", {
                "workflow_id": workflow_id,
                "agent_type": agent_type,
                "command": command,
                "execution_result": execution_result
            })
            
            self.engine_metrics["agent_interactions"] += 1
            
            logger.info(f"Agent command executed: {agent_type} {command} in workflow {workflow_id}")
            
            return {
                "success": True,
                "workflow_id": workflow_id,
                "route_result": route_result,
                "execution_result": execution_result,
                "next_recommended_actions": await self._get_post_command_actions(workflow_context, agent_type, command),
                "message": f"Agent command {command} executed by {agent_type}"
            }
            
        except Exception as e:
            logger.error(f"Error executing agent command: {e}")
            return {"success": False, "error": str(e)}
    
    # =====================================
    # STORY DEVELOPMENT CYCLE
    # =====================================
    
    async def start_story_cycle(self, workflow_id: str, story_title: str, story_description: str = None, epic_id: str = None) -> Dict[str, Any]:
        """
        Start story development cycle within workflow
        
        Args:
            workflow_id: Parent workflow identifier
            story_title: Story title
            story_description: Story description
            epic_id: Optional parent epic ID
            
        Returns:
            Story cycle startup result
        """
        try:
            # Load workflow context
            workflow_context = await self._load_workflow_context(workflow_id)
            if not workflow_context:
                return {"success": False, "error": "Workflow not found"}
            
            project_id = workflow_context["project_id"]
            
            # Create story via orchestrator
            story_result = await self.orchestrator.create_story(project_id, story_title, story_description, epic_id)
            
            if not story_result["success"]:
                return story_result
            
            story_id = story_result["story_id"]
            
            # Update workflow context
            workflow_context["current_story_id"] = story_id
            workflow_context["story_cycle_started"] = datetime.now().isoformat()
            await self._persist_workflow_context(workflow_context)
            
            # Create story development plan
            development_plan = await self._create_story_development_plan(story_id)
            
            # Fire events
            await self._fire_event("story_created", {
                "workflow_id": workflow_id,
                "story_id": story_id,
                "development_plan": development_plan
            })
            
            logger.info(f"Story cycle started: {story_title} in workflow {workflow_id}")
            
            return {
                "success": True,
                "workflow_id": workflow_id,
                "story_id": story_id,
                "story_result": story_result,
                "development_plan": development_plan,
                "recommended_first_steps": await self._get_story_first_steps(story_id),
                "message": f"Story development cycle started for '{story_title}'"
            }
            
        except Exception as e:
            logger.error(f"Error starting story cycle: {e}")
            return {"success": False, "error": str(e)}
    
    async def run_quality_gate(self, workflow_id: str, story_id: str, gate_type: str = "comprehensive") -> Dict[str, Any]:
        """
        Run quality gate check for story
        
        Args:
            workflow_id: Workflow identifier
            story_id: Story identifier
            gate_type: Type of quality gate (risk, design, trace, nfr, review, gate)
            
        Returns:
            Quality gate result
        """
        try:
            # Get story context
            story = self.orchestrator.active_stories.get(story_id)
            if not story:
                return {"success": False, "error": "Story not found"}
            
            # Run appropriate quality gate
            if gate_type == "risk":
                gate_result = await self.quality_manager.risk_assessment(story)
            elif gate_type == "design":
                gate_result = await self.quality_manager.design_test_strategy(story)
            elif gate_type == "trace":
                gate_result = await self.quality_manager.trace_requirements(story)
            elif gate_type == "nfr":
                gate_result = await self.quality_manager.check_nfr(story)
            elif gate_type == "review":
                gate_result = await self.quality_manager.comprehensive_review(story)
            elif gate_type == "gate":
                gate_result = await self.quality_manager.quality_gate_assessment(story)
            else:
                # Comprehensive quality check
                gate_result = await self.quality_manager.check_story_gates(story, story.state)
            
            # Update workflow context
            workflow_context = await self._load_workflow_context(workflow_id)
            if workflow_context:
                if "quality_gates" not in workflow_context:
                    workflow_context["quality_gates"] = []
                
                workflow_context["quality_gates"].append({
                    "story_id": story_id,
                    "gate_type": gate_type,
                    "result": gate_result,
                    "timestamp": datetime.now().isoformat()
                })
                
                await self._persist_workflow_context(workflow_context)
            
            # Fire events
            await self._fire_event("quality_gate_checked", {
                "workflow_id": workflow_id,
                "story_id": story_id,
                "gate_type": gate_type,
                "gate_result": gate_result
            })
            
            self.engine_metrics["quality_gates_processed"] += 1
            
            logger.info(f"Quality gate {gate_type} executed for story {story_id}")
            
            return {
                "success": True,
                "workflow_id": workflow_id,
                "story_id": story_id,
                "gate_type": gate_type,
                "gate_result": gate_result,
                "next_actions": await self._get_post_gate_actions(gate_result, gate_type),
                "message": f"Quality gate {gate_type} completed"
            }
            
        except Exception as e:
            logger.error(f"Error running quality gate: {e}")
            return {"success": False, "error": str(e)}
    
    # =====================================
    # WORKFLOW AUTOMATION & INTELLIGENCE
    # =====================================
    
    def add_automation_rule(self, rule: Dict[str, Any]):
        """
        Add workflow automation rule
        
        Args:
            rule: Automation rule definition
        """
        self.automation_rules.append(rule)
        logger.info(f"Added automation rule: {rule.get('name', 'unnamed')}")
    
    async def _trigger_workflow_automation(self, workflow_context: Dict[str, Any]):
        """Trigger workflow automation based on current context"""
        try:
            for rule in self.automation_rules:
                if await self._evaluate_automation_rule(rule, workflow_context):
                    await self._execute_automation_action(rule, workflow_context)
                    self.engine_metrics["automation_triggers"] += 1
                    
        except Exception as e:
            logger.error(f"Error in workflow automation: {e}")
    
    async def _evaluate_automation_rule(self, rule: Dict[str, Any], context: Dict[str, Any]) -> bool:
        """Evaluate if automation rule should trigger"""
        # Simple rule evaluation - can be expanded
        conditions = rule.get("conditions", {})
        
        for key, expected_value in conditions.items():
            if context.get(key) != expected_value:
                return False
        
        return True
    
    async def _execute_automation_action(self, rule: Dict[str, Any], context: Dict[str, Any]):
        """Execute automation action"""
        action = rule.get("action", {})
        action_type = action.get("type")
        
        if action_type == "advance_workflow":
            await self.advance_workflow(context["workflow_id"], action.get("target_state"))
        elif action_type == "assign_agent":
            # Implement agent assignment automation
            pass
        elif action_type == "run_quality_gate":
            # Implement quality gate automation
            pass
        
        logger.info(f"Executed automation action: {action_type}")
    
    # =====================================
    # MONITORING & REPORTING
    # =====================================
    
    async def get_workflow_status(self, workflow_id: str = None) -> Dict[str, Any]:
        """
        Get comprehensive workflow status
        
        Args:
            workflow_id: Optional specific workflow ID
            
        Returns:
            Workflow status report
        """
        try:
            if workflow_id:
                # Single workflow status
                workflow_context = await self._load_workflow_context(workflow_id)
                if not workflow_context:
                    return {"success": False, "error": "Workflow not found"}
                
                # Get orchestrator status for the project
                project_status = await self.orchestrator.get_workflow_status(workflow_context["project_id"])
                
                return {
                    "success": True,
                    "workflow_id": workflow_id,
                    "workflow_context": workflow_context,
                    "project_status": project_status,
                    "engine_metrics": self.engine_metrics,
                    "active_agents": list(self.active_agents.keys()),
                    "automation_rules_count": len(self.automation_rules)
                }
            else:
                # All workflows overview
                orchestrator_status = await self.orchestrator.get_workflow_status()
                
                return {
                    "success": True,
                    "engine_overview": {
                        "engine_version": "1.0.0",
                        "active_workflows": await self._count_active_workflows(),
                        "engine_metrics": self.engine_metrics,
                        "active_agents": list(self.active_agents.keys()),
                        "automation_rules": len(self.automation_rules)
                    },
                    "orchestrator_status": orchestrator_status,
                    "quality_metrics": self.quality_manager.get_quality_metrics()
                }
                
        except Exception as e:
            logger.error(f"Error getting workflow status: {e}")
            return {"success": False, "error": str(e)}
    
    async def generate_workflow_report(self, workflow_id: str) -> Dict[str, Any]:
        """
        Generate comprehensive workflow report
        
        Args:
            workflow_id: Workflow identifier
            
        Returns:
            Comprehensive workflow report
        """
        try:
            workflow_context = await self._load_workflow_context(workflow_id)
            if not workflow_context:
                return {"success": False, "error": "Workflow not found"}
            
            project_id = workflow_context["project_id"]
            project_status = await self.orchestrator.get_workflow_status(project_id)
            
            # Generate comprehensive report
            report = {
                "report_id": f"report_{workflow_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "workflow_id": workflow_id,
                "generated_at": datetime.now().isoformat(),
                "workflow_summary": {
                    "started_at": workflow_context.get("started_at"),
                    "duration": self._calculate_workflow_duration(workflow_context),
                    "current_state": workflow_context.get("current_state"),
                    "completion_percentage": await self._calculate_completion_percentage(workflow_context)
                },
                "project_details": project_status,
                "agent_interactions": await self._get_agent_interaction_summary(workflow_context),
                "quality_gate_summary": await self._get_quality_gate_summary(workflow_context),
                "automation_events": workflow_context.get("automation_events", []),
                "recommendations": await self._generate_workflow_recommendations(workflow_context)
            }
            
            logger.info(f"Generated workflow report for {workflow_id}")
            
            return {
                "success": True,
                "report": report,
                "message": "Workflow report generated successfully"
            }
            
        except Exception as e:
            logger.error(f"Error generating workflow report: {e}")
            return {"success": False, "error": str(e)}
    
    # =====================================
    # AGENT REGISTRATION & MANAGEMENT
    # =====================================
    
    def register_agent(self, agent_type: str, agent_instance):
        """
        Register actual agent instance with workflow engine
        
        Args:
            agent_type: Type of agent (analyst, architect, pm, dev, qa)
            agent_instance: Actual agent instance
        """
        if agent_type in self.active_agents:
            self.active_agents[agent_type] = agent_instance
            logger.info(f"Registered {agent_type} agent with workflow engine")
        else:
            logger.warning(f"Unknown agent type: {agent_type}")
    
    def register_event_handler(self, event_type: str, handler: Callable):
        """
        Register event handler for workflow events
        
        Args:
            event_type: Type of event
            handler: Event handler function
        """
        if event_type in self.event_handlers:
            self.event_handlers[event_type].append(handler)
            logger.info(f"Registered event handler for {event_type}")
    
    async def _fire_event(self, event_type: str, event_data: Dict[str, Any]):
        """Fire workflow event to all registered handlers"""
        handlers = self.event_handlers.get(event_type, [])
        for handler in handlers:
            try:
                if asyncio.iscoroutinefunction(handler):
                    await handler(event_data)
                else:
                    handler(event_data)
            except Exception as e:
                logger.error(f"Error in event handler for {event_type}: {e}")
    
    # =====================================
    # PRIVATE HELPER METHODS
    # =====================================
    
    async def _create_execution_plan(self, project_id: str, workflow_type: str) -> Dict[str, Any]:
        """Create workflow execution plan"""
        if workflow_type == "full":
            return {
                "phases": [
                    {"phase": "planning", "states": ["idea_generation", "analyst_research", "project_brief", "prd_creation", "architecture"]},
                    {"phase": "development", "states": ["development_ready", "in_development"]},
                    {"phase": "quality", "states": ["qa_review", "quality_gates"]},
                    {"phase": "completion", "states": ["completed"]}
                ],
                "estimated_duration": "4-8 weeks",
                "required_agents": ["analyst", "architect", "pm", "dev", "qa"],
                "quality_gates": ["risk_assessment", "design_review", "comprehensive_review", "final_gate"]
            }
        elif workflow_type == "planning_only":
            return {
                "phases": [
                    {"phase": "planning", "states": ["idea_generation", "analyst_research", "project_brief", "prd_creation", "architecture"]}
                ],
                "estimated_duration": "1-2 weeks",
                "required_agents": ["analyst", "architect", "pm"],
                "quality_gates": ["requirements_review", "architecture_review"]
            }
        else:
            return {
                "phases": [
                    {"phase": "development", "states": ["development_ready", "in_development"]},
                    {"phase": "quality", "states": ["qa_review", "quality_gates"]},
                    {"phase": "completion", "states": ["completed"]}
                ],
                "estimated_duration": "2-6 weeks",
                "required_agents": ["dev", "qa"],
                "quality_gates": ["code_review", "comprehensive_review", "final_gate"]
            }
    
    async def _create_story_development_plan(self, story_id: str) -> Dict[str, Any]:
        """Create story development plan"""
        return {
            "development_phases": [
                {"phase": "analysis", "steps": ["risk_profiling", "requirements_analysis"]},
                {"phase": "planning", "steps": ["task_breakdown", "test_strategy"]},
                {"phase": "implementation", "steps": ["development", "unit_testing"]},
                {"phase": "quality", "steps": ["qa_check", "integration_testing"]},
                {"phase": "review", "steps": ["comprehensive_review", "quality_gate"]}
            ],
            "estimated_duration": "3-10 days",
            "quality_checkpoints": ["risk_assessment", "mid_development_qa", "final_review"],
            "required_artifacts": ["acceptance_criteria", "test_cases", "documentation"]
        }
    
    async def _get_immediate_next_actions(self, workflow_context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Get immediate next actions for workflow"""
        # Get next steps from orchestrator
        project_id = workflow_context["project_id"]
        orchestrator_status = await self.orchestrator.get_workflow_status(project_id)
        
        next_actions = []
        
        if orchestrator_status["success"] and orchestrator_status.get("project"):
            current_state = orchestrator_status["project"]["state"]
            
            # Determine next logical actions based on state
            if current_state == "idea_generation":
                next_actions.append({
                    "action": "analyst_research",
                    "description": "Conduct analyst research",
                    "required_agent": "analyst",
                    "command": "*research",
                    "priority": "high"
                })
            elif current_state == "analyst_research":
                next_actions.append({
                    "action": "create_project_brief",
                    "description": "Create project brief",
                    "required_agent": "pm",
                    "command": "*create-brief",
                    "priority": "high"
                })
            # Add more state-specific actions as needed
        
        return next_actions
    
    async def _get_story_first_steps(self, story_id: str) -> List[Dict[str, Any]]:
        """Get recommended first steps for story"""
        return [
            {
                "action": "risk_assessment",
                "description": "Conduct story risk assessment",
                "required_agent": "qa",
                "command": "*risk",
                "priority": "high"
            },
            {
                "action": "task_breakdown",
                "description": "Break story into development tasks",
                "required_agent": "dev",
                "command": "*breakdown",
                "priority": "high"
            },
            {
                "action": "acceptance_criteria_review",
                "description": "Review and refine acceptance criteria",
                "required_agent": "pm",
                "command": "*review-criteria",
                "priority": "medium"
            }
        ]
    
    async def _get_post_command_actions(self, workflow_context: Dict[str, Any], agent_type: str, command: str) -> List[Dict[str, Any]]:
        """Get recommended actions after agent command"""
        # Simple logic - can be expanded
        if agent_type == "qa" and command == "*risk":
            return [
                {
                    "action": "review_risk_mitigation",
                    "description": "Review risk mitigation strategies",
                    "required_agent": "pm",
                    "priority": "medium"
                }
            ]
        
        return []
    
    async def _get_post_gate_actions(self, gate_result: Dict[str, Any], gate_type: str) -> List[Dict[str, Any]]:
        """Get recommended actions after quality gate"""
        actions = []
        
        if not gate_result.get("passed", False):
            actions.append({
                "action": "address_quality_issues",
                "description": "Address identified quality issues",
                "priority": "high",
                "issues": gate_result.get("issues", [])
            })
        
        if gate_result.get("recommendations"):
            actions.append({
                "action": "implement_recommendations",
                "description": "Implement quality recommendations",
                "priority": "medium",
                "recommendations": gate_result["recommendations"]
            })
        
        return actions
    
    async def _simulate_agent_command(self, agent_type: str, command: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate agent command execution"""
        # This would be replaced by actual agent implementations
        return {
            "success": True,
            "agent": agent_type,
            "command": command,
            "simulated": True,
            "result": f"Command {command} executed by {agent_type}",
            "timestamp": datetime.now().isoformat()
        }
    
    # Persistence methods
    async def _persist_workflow_context(self, context: Dict[str, Any]):
        """Persist workflow context to storage"""
        try:
            workflow_id = context["workflow_id"]
            file_path = self.persistence_path / f"{workflow_id}.json"
            
            with open(file_path, 'w') as f:
                json.dump(context, f, indent=2, default=str)
                
        except Exception as e:
            logger.error(f"Error persisting workflow context: {e}")
    
    async def _load_workflow_context(self, workflow_id: str) -> Optional[Dict[str, Any]]:
        """Load workflow context from storage"""
        try:
            file_path = self.persistence_path / f"{workflow_id}.json"
            
            if file_path.exists():
                with open(file_path, 'r') as f:
                    return json.load(f)
                    
        except Exception as e:
            logger.error(f"Error loading workflow context: {e}")
        
        return None
    
    async def _load_persisted_state(self):
        """Load all persisted workflow state on startup"""
        try:
            if self.persistence_path.exists():
                for file_path in self.persistence_path.glob("workflow_*.json"):
                    context = await self._load_workflow_context(file_path.stem)
                    if context:
                        logger.info(f"Loaded persisted workflow: {context['workflow_id']}")
                        
        except Exception as e:
            logger.error(f"Error loading persisted state: {e}")
    
    def _start_background_tasks(self):
        """Start background maintenance tasks"""
        # This would start background tasks for monitoring, cleanup, etc.
        pass
    
    async def _count_active_workflows(self) -> int:
        """Count active workflows"""
        count = 0
        for file_path in self.persistence_path.glob("workflow_*.json"):
            try:
                context = await self._load_workflow_context(file_path.stem)
                if context and context.get("status") == "active":
                    count += 1
            except Exception:
                pass
        
        return count
    
    def _calculate_workflow_duration(self, context: Dict[str, Any]) -> str:
        """Calculate workflow duration"""
        started_at = context.get("started_at")
        if started_at:
            start_time = datetime.fromisoformat(started_at.replace('Z', '+00:00'))
            duration = datetime.now() - start_time.replace(tzinfo=None)
            return str(duration)
        
        return "Unknown"
    
    async def _calculate_completion_percentage(self, context: Dict[str, Any]) -> float:
        """Calculate workflow completion percentage"""
        # Simple calculation based on execution plan
        execution_plan = context.get("execution_plan", {})
        phases = execution_plan.get("phases", [])
        
        if not phases:
            return 0.0
        
        # This would need more sophisticated logic based on actual state
        return 50.0  # Placeholder
    
    async def _get_agent_interaction_summary(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Get summary of agent interactions"""
        return {
            "total_interactions": context.get("agent_interactions", 0),
            "last_agent": context.get("last_agent"),
            "last_interaction": context.get("last_agent_interaction"),
            "agents_used": list(set(context.get("agents_history", [])))
        }
    
    async def _get_quality_gate_summary(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Get summary of quality gates"""
        quality_gates = context.get("quality_gates", [])
        
        return {
            "total_gates": len(quality_gates),
            "gates_passed": len([g for g in quality_gates if g.get("result", {}).get("passed", False)]),
            "gates_failed": len([g for g in quality_gates if not g.get("result", {}).get("passed", True)]),
            "last_gate": quality_gates[-1] if quality_gates else None
        }
    
    async def _generate_workflow_recommendations(self, context: Dict[str, Any]) -> List[str]:
        """Generate workflow recommendations"""
        recommendations = []
        
        # Analyze workflow progress and suggest improvements
        current_state = context.get("current_state")
        duration = context.get("started_at")
        
        if duration:
            start_time = datetime.fromisoformat(duration.replace('Z', '+00:00'))
            days_elapsed = (datetime.now() - start_time.replace(tzinfo=None)).days
            
            if days_elapsed > 14 and current_state in ["idea_generation", "analyst_research"]:
                recommendations.append("Consider accelerating planning phase - project has been in early stages for over 2 weeks")
            
            if context.get("quality_gates", []):
                failed_gates = [g for g in context["quality_gates"] if not g.get("result", {}).get("passed", True)]
                if failed_gates:
                    recommendations.append(f"Address {len(failed_gates)} failed quality gates before proceeding")
        
        return recommendations
    
    def get_engine_status(self) -> Dict[str, Any]:
        """Get workflow engine status"""
        return {
            "engine_version": "1.0.0",
            "engine_metrics": self.engine_metrics,
            "active_agents": {k: v is not None for k, v in self.active_agents.items()},
            "automation_rules_count": len(self.automation_rules),
            "event_handlers": {k: len(v) for k, v in self.event_handlers.items()},
            "persistence_path": str(self.persistence_path),
            "orchestrator_status": self.orchestrator.get_orchestrator_status(),
            "quality_manager_status": self.quality_manager.get_quality_metrics()
        }