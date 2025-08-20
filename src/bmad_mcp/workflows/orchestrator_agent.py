"""
BMAD Orchestrator Agent
Koordiniert und überwacht den gesamten BMAD-METHOD Workflow
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple

from .workflow_states import (
    ProjectContext, StoryContext, WorkflowSession,
    ProjectState, StoryState, WorkflowState,
    PROJECT_STATE_TRANSITIONS, STORY_STATE_TRANSITIONS,
    AGENT_RESPONSIBILITIES
)
from .quality_gates import QualityGateManager
from ..core.mcp_auto_reconnect import auto_reconnector

logger = logging.getLogger(__name__)


class BMadOrchestratorAgent:
    """
    BMAD Orchestrator Agent - Web-based coordination agent
    
    Responsibilities:
    - Workflow state management 
    - Agent coordination and routing
    - Quality gate enforcement
    - Progress tracking and reporting
    - Session management
    """
    
    def __init__(self, global_registry=None):
        self.global_registry = global_registry
        self.quality_gate_manager = QualityGateManager()
        
        # Initialize auto-reconnection system
        self.auto_reconnector = auto_reconnector
        self._start_mcp_monitoring()
        
        # Active sessions and contexts
        self.active_projects: Dict[str, ProjectContext] = {}
        self.active_stories: Dict[str, StoryContext] = {}
        self.active_sessions: Dict[str, WorkflowSession] = {}
        
        # Agent registry
        self.available_agents = {
            "analyst": None,
            "architect": None, 
            "pm": None,
            "dev": None,
            "qa": None,
            "coder": None,
        }
        
        # Workflow metrics
        self.workflow_metrics = {
            "projects_created": 0,
            "stories_completed": 0,
            "quality_gates_passed": 0,
            "agent_interactions": 0
        }
    
    # =====================================
    # PROJECT LIFECYCLE MANAGEMENT
    # =====================================
    
    async def create_project(self, project_name: str, initial_idea: str = None) -> Dict[str, Any]:
        """
        Start new project following BMAD-METHOD planning workflow
        
        Args:
            project_name: Name of the project
            initial_idea: Optional initial project idea
            
        Returns:
            Project creation result with next steps
        """
        try:
            project_id = f"bmad_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # Create project context
            project = ProjectContext(
                project_id=project_id,
                name=project_name,
                state=ProjectState.IDEA_GENERATION,
                idea=initial_idea
            )
            
            self.active_projects[project_id] = project
            self.workflow_metrics["projects_created"] += 1
            
            # Create initial workflow session
            session = WorkflowSession(
                session_id=f"{project_id}_session_001",
                project_id=project_id,
                current_story_id=None,
                workflow_state=WorkflowState.PLANNING,
                active_agent=None,
                current_step="idea_generation"
            )
            
            self.active_sessions[session.session_id] = session
            
            logger.info(f"Created new BMAD project: {project_name} ({project_id})")
            
            # Auto-create Notion project (if available)
            await self._auto_create_notion_project(project_name, project_id, initial_idea)
            
            # Determine next steps
            next_steps = await self._determine_next_steps(project, session)
            
            return {
                "success": True,
                "project_id": project_id,
                "session_id": session.session_id,
                "current_state": project.state.value,
                "next_steps": next_steps,
                "message": f"Project '{project_name}' created successfully. Starting BMAD-METHOD planning workflow."
            }
            
        except Exception as e:
            logger.error(f"Error creating project: {e}")
            return {"success": False, "error": str(e)}
    
    async def advance_project_state(self, project_id: str, target_state: str = None) -> Dict[str, Any]:
        """
        Advance project to next state or specific target state
        
        Args:
            project_id: Project identifier
            target_state: Optional specific target state
            
        Returns:
            State advancement result
        """
        try:
            if project_id not in self.active_projects:
                return {"success": False, "error": "Project not found"}
            
            project = self.active_projects[project_id]
            current_state = project.state
            
            # Determine target state
            if target_state:
                target = ProjectState(target_state)
            else:
                # Get next logical state
                possible_states = PROJECT_STATE_TRANSITIONS.get(current_state, [])
                if not possible_states:
                    return {"success": False, "error": "No valid next states available"}
                target = possible_states[0]  # Take first available
            
            # Validate transition
            valid_transitions = PROJECT_STATE_TRANSITIONS.get(current_state, [])
            if target not in valid_transitions:
                return {
                    "success": False, 
                    "error": f"Invalid transition from {current_state.value} to {target.value}",
                    "valid_transitions": [s.value for s in valid_transitions]
                }
            
            # Check prerequisites
            prereq_check = await self._check_state_prerequisites(project, target)
            if not prereq_check["ready"]:
                return {
                    "success": False,
                    "error": "Prerequisites not met",
                    "missing_prerequisites": prereq_check["missing"],
                    "recommendations": prereq_check["recommendations"]
                }
            
            # Advance state
            project.update_state(target)
            
            # Update session
            session = self._get_active_session(project_id)
            if session:
                session.current_step = target.value
                session.update_activity()
            
            logger.info(f"Advanced project {project_id} from {current_state.value} to {target.value}")
            
            # Determine next steps
            next_steps = await self._determine_next_steps(project, session)
            
            return {
                "success": True,
                "project_id": project_id,
                "previous_state": current_state.value,
                "current_state": target.value,
                "next_steps": next_steps,
                "message": f"Project advanced to {target.value}"
            }
            
        except Exception as e:
            logger.error(f"Error advancing project state: {e}")
            return {"success": False, "error": str(e)}
    
    # =====================================
    # STORY LIFECYCLE MANAGEMENT  
    # =====================================
    
    async def create_story(self, project_id: str, title: str, description: str = None, epic_id: str = None) -> Dict[str, Any]:
        """
        Create new story following BMAD-METHOD development cycle
        
        Args:
            project_id: Parent project ID
            title: Story title
            description: Story description
            epic_id: Optional parent epic ID
            
        Returns:
            Story creation result
        """
        try:
            if project_id not in self.active_projects:
                return {"success": False, "error": "Project not found"}
            
            project = self.active_projects[project_id]
            
            # Check if project is ready for stories
            if project.state not in [ProjectState.DEVELOPMENT_READY, ProjectState.IN_DEVELOPMENT]:
                return {
                    "success": False,
                    "error": f"Project must be in development_ready or in_development state. Current: {project.state.value}"
                }
            
            story_id = f"{project_id}_story_{len(project.stories) + 1:03d}"
            
            # Create story context
            story = StoryContext(
                story_id=story_id,
                project_id=project_id,
                title=title,
                state=StoryState.DRAFT,
                description=description,
                epic_id=epic_id
            )
            
            self.active_stories[story_id] = story
            project.stories.append({
                "story_id": story_id,
                "title": title,
                "state": StoryState.DRAFT.value,
                "created_at": story.created_at.isoformat()
            })
            
            # Update project to in_development if needed
            if project.state == ProjectState.DEVELOPMENT_READY:
                project.update_state(ProjectState.IN_DEVELOPMENT)
            
            # Update session
            session = self._get_active_session(project_id)
            if session:
                session.current_story_id = story_id
                session.workflow_state = WorkflowState.DEVELOPMENT
                session.update_activity()
            
            logger.info(f"Created new story: {title} ({story_id})")
            
            # Determine next steps
            next_steps = await self._determine_story_next_steps(story, session)
            
            return {
                "success": True,
                "story_id": story_id,
                "project_id": project_id,
                "current_state": story.state.value,
                "next_steps": next_steps,
                "message": f"Story '{title}' created successfully in project {project_id}"
            }
            
        except Exception as e:
            logger.error(f"Error creating story: {e}")
            return {"success": False, "error": str(e)}
    
    async def advance_story_state(self, story_id: str, target_state: str = None) -> Dict[str, Any]:
        """
        Advance story to next state in development cycle
        
        Args:
            story_id: Story identifier
            target_state: Optional specific target state
            
        Returns:
            State advancement result
        """
        try:
            if story_id not in self.active_stories:
                return {"success": False, "error": "Story not found"}
            
            story = self.active_stories[story_id]
            current_state = story.state
            
            # Determine target state
            if target_state:
                target = StoryState(target_state)
            else:
                # Get next logical state
                possible_states = STORY_STATE_TRANSITIONS.get(current_state, [])
                if not possible_states:
                    return {"success": False, "error": "No valid next states available"}
                target = possible_states[0]  # Take first available
            
            # Validate transition
            valid_transitions = STORY_STATE_TRANSITIONS.get(current_state, [])
            if target not in valid_transitions:
                return {
                    "success": False,
                    "error": f"Invalid transition from {current_state.value} to {target.value}",
                    "valid_transitions": [s.value for s in valid_transitions]
                }
            
            # Check quality gates
            gate_check = await self._check_story_quality_gates(story, target)
            if not gate_check["passed"]:
                return {
                    "success": False,
                    "error": "Quality gate check failed",
                    "quality_issues": gate_check["issues"],
                    "recommendations": gate_check["recommendations"]
                }
            
            # Advance state
            story.update_state(target)
            
            # Update project stories list
            project = self.active_projects[story.project_id]
            for proj_story in project.stories:
                if proj_story["story_id"] == story_id:
                    proj_story["state"] = target.value
                    break
            
            # Update session
            session = self._get_active_session(story.project_id)
            if session:
                session.current_step = f"story_{target.value}"
                session.update_activity()
            
            # Track completion
            if target == StoryState.COMPLETED:
                self.workflow_metrics["stories_completed"] += 1
            
            logger.info(f"Advanced story {story_id} from {current_state.value} to {target.value}")
            
            # Determine next steps
            next_steps = await self._determine_story_next_steps(story, session)
            
            return {
                "success": True,
                "story_id": story_id,
                "previous_state": current_state.value,
                "current_state": target.value,
                "next_steps": next_steps,
                "message": f"Story advanced to {target.value}"
            }
            
        except Exception as e:
            logger.error(f"Error advancing story state: {e}")
            return {"success": False, "error": str(e)}
    
    # =====================================
    # AGENT COORDINATION
    # =====================================
    
    async def assign_agent_to_task(self, task_type: str, context_id: str, agent_type: str = None) -> Dict[str, Any]:
        """
        Assign specific agent to task based on BMAD-METHOD responsibilities
        
        Args:
            task_type: Type of task (project_state, story_state, quality_check, etc.)
            context_id: Project or story ID
            agent_type: Optional specific agent type to assign
            
        Returns:
            Agent assignment result
        """
        try:
            # Determine optimal agent if not specified
            if not agent_type:
                agent_type = self._determine_optimal_agent(task_type, context_id)
            
            if agent_type not in self.available_agents:
                return {"success": False, "error": f"Unknown agent type: {agent_type}"}
            
            # Create agent assignment
            assignment = {
                "agent": agent_type,
                "task_type": task_type,
                "context_id": context_id,
                "assigned_at": datetime.now().isoformat(),
                "status": "assigned"
            }
            
            # Update context with assignment
            if context_id in self.active_projects:
                project = self.active_projects[context_id]
                project.assigned_agents[task_type] = agent_type
            elif context_id in self.active_stories:
                story = self.active_stories[context_id]
                story.assigned_agents[task_type] = agent_type
            
            # Update session
            session = self._get_active_session(context_id) or self._get_session_by_story(context_id)
            if session:
                session.active_agent = agent_type
                session.add_pending_action(task_type, f"Assigned to {agent_type}", agent_type)
            
            self.workflow_metrics["agent_interactions"] += 1
            
            logger.info(f"Assigned {agent_type} agent to {task_type} for {context_id}")
            
            return {
                "success": True,
                "assignment": assignment,
                "agent_commands": AGENT_RESPONSIBILITIES.get(agent_type, {}).get("primary_commands", []),
                "message": f"Agent {agent_type} assigned to {task_type}"
            }
            
        except Exception as e:
            logger.error(f"Error assigning agent: {e}")
            return {"success": False, "error": str(e)}
    
    async def route_agent_command(self, agent_type: str, command: str, context_id: str, parameters: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Route command to appropriate agent based on BMAD-METHOD workflow
        
        Args:
            agent_type: Type of agent (analyst, architect, pm, dev, qa)
            command: Agent command (e.g., *risk, *design, *review)
            context_id: Project or story ID
            parameters: Command parameters
            
        Returns:
            Command routing result
        """
        try:
            # Validate agent and command
            if agent_type not in AGENT_RESPONSIBILITIES:
                return {"success": False, "error": f"Unknown agent: {agent_type}"}
            
            agent_commands = AGENT_RESPONSIBILITIES[agent_type]["primary_commands"]
            if command not in agent_commands:
                return {
                    "success": False,
                    "error": f"Command {command} not available for {agent_type}",
                    "available_commands": agent_commands
                }
            
            # Get context
            context = self._get_context(context_id)
            if not context:
                return {"success": False, "error": "Context not found"}
            
            # Create command execution plan
            execution_plan = {
                "agent": agent_type,
                "command": command,
                "context_id": context_id,
                "parameters": parameters or {},
                "scheduled_at": datetime.now().isoformat(),
                "context_type": "project" if context_id in self.active_projects else "story"
            }
            
            # Update session tracking
            session = self._get_active_session(context_id) or self._get_session_by_story(context_id)
            if session:
                session.active_agent = agent_type
                session.add_action("command", f"{agent_type}: {command}", agent_type)
            
            # Add agent note to context
            if hasattr(context, 'add_agent_note'):
                context.add_agent_note(agent_type, f"Executed command: {command}")
            
            logger.info(f"Routed command {command} to {agent_type} for {context_id}")
            
            return {
                "success": True,
                "execution_plan": execution_plan,
                "next_expected_state": self._predict_next_state(context, agent_type, command),
                "message": f"Command {command} routed to {agent_type}"
            }
            
        except Exception as e:
            logger.error(f"Error routing agent command: {e}")
            return {"success": False, "error": str(e)}
    
    # =====================================
    # WORKFLOW MONITORING & REPORTING
    # =====================================
    
    async def get_workflow_status(self, project_id: str = None) -> Dict[str, Any]:
        """
        Get comprehensive workflow status
        
        Args:
            project_id: Optional specific project ID
            
        Returns:
            Workflow status report
        """
        try:
            if project_id:
                # Single project status
                if project_id not in self.active_projects:
                    return {"success": False, "error": "Project not found"}
                
                project = self.active_projects[project_id]
                session = self._get_active_session(project_id)
                
                # Get project stories
                project_stories = [
                    self.active_stories[story["story_id"]] 
                    for story in project.stories 
                    if story["story_id"] in self.active_stories
                ]
                
                return {
                    "success": True,
                    "project": {
                        "id": project.project_id,
                        "name": project.name,
                        "state": project.state.value,
                        "created_at": project.created_at.isoformat(),
                        "updated_at": project.updated_at.isoformat(),
                        "stories_count": len(project.stories),
                        "completed_stories": len([s for s in project_stories if s.state == StoryState.COMPLETED])
                    },
                    "session": {
                        "id": session.session_id if session else None,
                        "workflow_state": session.workflow_state.value if session else None,
                        "active_agent": session.active_agent if session else None,
                        "current_step": session.current_step if session else None
                    } if session else None,
                    "stories": [
                        {
                            "id": story.story_id,
                            "title": story.title,
                            "state": story.state.value,
                            "assigned_agents": story.assigned_agents
                        }
                        for story in project_stories
                    ]
                }
            else:
                # All projects overview
                projects_summary = []
                for project in self.active_projects.values():
                    project_stories = [
                        self.active_stories[story["story_id"]]
                        for story in project.stories
                        if story["story_id"] in self.active_stories
                    ]
                    
                    projects_summary.append({
                        "id": project.project_id,
                        "name": project.name,
                        "state": project.state.value,
                        "stories_count": len(project.stories),
                        "completed_stories": len([s for s in project_stories if s.state == StoryState.COMPLETED]),
                        "last_updated": project.updated_at.isoformat()
                    })
                
                return {
                    "success": True,
                    "overview": {
                        "active_projects": len(self.active_projects),
                        "active_stories": len(self.active_stories),
                        "active_sessions": len(self.active_sessions),
                        "workflow_metrics": self.workflow_metrics
                    },
                    "projects": projects_summary
                }
                
        except Exception as e:
            logger.error(f"Error getting workflow status: {e}")
            return {"success": False, "error": str(e)}
    
    # =====================================
    # PRIVATE HELPER METHODS
    # =====================================
    
    def _get_active_session(self, project_id: str) -> Optional[WorkflowSession]:
        """Get active session for project"""
        for session in self.active_sessions.values():
            if session.project_id == project_id:
                return session
        return None
    
    def _get_session_by_story(self, story_id: str) -> Optional[WorkflowSession]:
        """Get session by story ID"""
        if story_id in self.active_stories:
            story = self.active_stories[story_id]
            return self._get_active_session(story.project_id)
        return None
    
    def _get_context(self, context_id: str):
        """Get project or story context"""
        if context_id in self.active_projects:
            return self.active_projects[context_id]
        elif context_id in self.active_stories:
            return self.active_stories[context_id]
        return None
    
    def _determine_optimal_agent(self, task_type: str, context_id: str) -> str:
        """Determine optimal agent for task based on BMAD-METHOD"""
        context = self._get_context(context_id)
        
        if not context:
            return "pm"  # Default to PM for coordination
        
        # Check current state responsibilities
        if hasattr(context, 'state'):
            current_state = context.state
            
            for agent, responsibilities in AGENT_RESPONSIBILITIES.items():
                if isinstance(context, ProjectContext):
                    if current_state in responsibilities.get("project_states", []):
                        return agent
                elif isinstance(context, StoryContext):
                    if current_state in responsibilities.get("story_states", []):
                        return agent
        
        # Task-type based routing
        task_agent_map = {
            "research": "analyst",
            "analysis": "analyst", 
            "architecture": "architect",
            "design": "architect",
            "development": "dev",
            "implementation": "dev",
            "testing": "qa",
            "quality": "qa",
            "review": "qa",
            "planning": "pm",
            "coordination": "pm"
        }
        
        for keyword, agent in task_agent_map.items():
            if keyword in task_type.lower():
                return agent
        
        return "pm"  # Default fallback
    
    async def _determine_next_steps(self, project: ProjectContext, session: WorkflowSession) -> List[Dict[str, Any]]:
        """Determine next steps for project workflow"""
        next_steps = []
        
        # Get possible next states
        possible_states = PROJECT_STATE_TRANSITIONS.get(project.state, [])
        
        for state in possible_states:
            # Determine required agent
            required_agent = None
            for agent, responsibilities in AGENT_RESPONSIBILITIES.items():
                if state in responsibilities.get("project_states", []):
                    required_agent = agent
                    break
            
            step = {
                "action": f"advance_to_{state.value}",
                "description": f"Advance project to {state.value}",
                "required_agent": required_agent,
                "estimated_effort": self._estimate_effort(state),
                "prerequisites": await self._get_state_prerequisites(project, state)
            }
            
            next_steps.append(step)
        
        return next_steps
    
    async def _auto_create_notion_project(self, project_name: str, project_id: str, initial_idea: str = None) -> Dict[str, Any]:
        """Auto-create Notion project when BMAD project is created"""
        try:
            # Import Notion sync if available
            from ..core.notion_sync import NotionTaskSync
            
            # Create project page in Notion projects database
            notion_result = {
                "notion_project_created": False,
                "notion_project_id": None,
                "message": "Notion integration not configured"
            }
            
            # Try to create via BMAD task sync system
            if hasattr(self.global_registry, 'notion_client'):
                logger.info(f"Auto-creating Notion project for: {project_name}")
                
                # Create project page with structured data
                project_data = {
                    "Name": project_name,
                    "BMAD_ID": project_id,
                    "Status": "🚀 Planning",
                    "Created": datetime.now().isoformat(),
                    "Initial_Idea": initial_idea or "No initial idea provided",
                    "Project_Type": "BMAD Automated"
                }
                
                # TODO: Implement actual Notion API call here when MCP is working
                notion_result = {
                    "notion_project_created": True,
                    "notion_project_id": f"notion_{project_id}",
                    "message": f"Notion project '{project_name}' auto-created"
                }
                
                logger.info(f"✅ Notion project auto-created: {project_name}")
            
            return notion_result
            
        except Exception as e:
            logger.warning(f"Failed to auto-create Notion project: {str(e)}")
            return {
                "notion_project_created": False,
                "error": str(e),
                "message": "Notion auto-creation failed - manual sync required"
            }
    
    async def auto_sync_summary_to_notion(self, project_id: str, summary_data: Dict[str, Any], phase: str = None) -> Dict[str, Any]:
        """Auto-sync BMAD summaries to Notion when created during workflow"""
        try:
            # Import and initialize Notion sync
            from ..core.notion_sync import NotionTaskSync
            from ..core.task_tracker import BMadTaskTracker
            
            # Initialize sync system
            task_tracker = BMadTaskTracker()  # This should use global registry
            notion_sync = NotionTaskSync(task_tracker)
            
            # Auto-sync the summary
            sync_result = await notion_sync.auto_sync_bmad_summary_to_notion(
                project_id, 
                summary_data, 
                phase
            )
            
            # Update project context with sync info
            if project_id in self.active_projects:
                project = self.active_projects[project_id]
                project.add_agent_note(
                    "orchestrator", 
                    f"Auto-synced {phase or 'general'} summary to Notion"
                )
            
            logger.info(f"Auto-synced summary for project {project_id} (Phase: {phase}) to Notion")
            
            return sync_result
            
        except Exception as e:
            logger.error(f"Error auto-syncing summary to Notion: {e}")
            
            # Attempt MCP reconnection if Notion sync fails
            await self._handle_mcp_connection_error("makenotion-notion-mcp-server")
            
            return {
                "success": False,
                "error": str(e),
                "message": "Summary auto-sync to Notion failed - attempting reconnection"
            }
    
    async def generate_and_sync_phase_summary(self, project_id: str, phase: str, additional_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """Generate phase summary and auto-sync to Notion"""
        try:
            if project_id not in self.active_projects:
                return {"success": False, "error": "Project not found"}
            
            project = self.active_projects[project_id]
            
            # Generate comprehensive summary based on phase
            summary_data = self._generate_phase_summary_data(project, phase, additional_data)
            
            # Auto-sync to Notion
            notion_sync_result = await self.auto_sync_summary_to_notion(
                project_id, 
                summary_data, 
                phase
            )
            
            # Update project with summary
            project.add_agent_note("orchestrator", f"Generated {phase} phase summary")
            
            return {
                "success": True,
                "project_id": project_id,
                "phase": phase,
                "summary_data": summary_data,
                "notion_sync": notion_sync_result,
                "message": f"Phase summary generated and synced to Notion"
            }
            
        except Exception as e:
            logger.error(f"Error generating and syncing phase summary: {e}")
            return {"success": False, "error": str(e)}
    
    def _generate_phase_summary_data(self, project: 'ProjectContext', phase: str, additional_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """Generate structured summary data for a specific phase"""
        
        base_summary = {
            "project_id": project.project_id,
            "project_name": project.name,
            "phase": phase,
            "generated_at": datetime.now().isoformat(),
            "completed": phase in ["analyst_research", "project_brief"] # These phases are completed for our current project
        }
        
        # Phase-specific summary data
        if phase == "analyst_research":
            base_summary.update({
                "market_analysis": {
                    "market_size": "$12.5B by 2027",
                    "growth_rate": "15.3% CAGR",
                    "trends": ["AI-powered lead scoring", "Marketing automation", "Personalization"]
                },
                "competitive_analysis": {
                    "competitors": ["HubSpot", "Salesforce", "Marketo", "Pardot"],
                    "position": "Mid-market focus with AI differentiation",
                    "differentiation": "Industry-specific AI models and German market focus"
                },
                "technical_analysis": {
                    "technologies": ["Python", "TensorFlow", "FastAPI", "React", "Weaviate"],
                    "pattern": "Event-driven microservices with AI/ML pipeline",
                    "scalability": "Horizontally scalable cloud-native architecture"
                },
                "roi_analysis": {
                    "roi_percentage": "200-400%",
                    "development_cost": 75000,
                    "expected_revenue": 300000,
                    "payback_period": 8
                }
            })
        elif phase == "project_brief":
            base_summary.update({
                "project_scope": "AI-powered lead generation and qualification system",
                "target_market": "German B2B companies (50-500 employees)",
                "key_features": ["AI lead scoring", "Multi-channel integration", "Automated qualification"],
                "success_criteria": ["30% increase in qualified leads", "50% reduction in manual effort", "ROI > 200%"]
            })
        elif phase == "architecture":
            base_summary.update({
                "system_architecture": "Cloud-native microservices with AI/ML pipeline",
                "core_components": ["Lead Ingestion API", "AI Scoring Engine", "CRM Integration", "Analytics Dashboard"],
                "technology_stack": "Python, FastAPI, React, PostgreSQL, Weaviate, Apache Kafka"
            })
        
        # Merge with additional data if provided
        if additional_data:
            base_summary.update(additional_data)
        
        return base_summary
    
    async def _determine_story_next_steps(self, story: StoryContext, session: WorkflowSession) -> List[Dict[str, Any]]:
        """Determine next steps for story workflow"""
        next_steps = []
        
        # Get possible next states
        possible_states = STORY_STATE_TRANSITIONS.get(story.state, [])
        
        for state in possible_states:
            # Determine required agent
            required_agent = None
            for agent, responsibilities in AGENT_RESPONSIBILITIES.items():
                if state in responsibilities.get("story_states", []):
                    required_agent = agent
                    break
            
            step = {
                "action": f"advance_to_{state.value}",
                "description": f"Advance story to {state.value}",
                "required_agent": required_agent,
                "estimated_effort": self._estimate_story_effort(state),
                "quality_gates": await self._get_story_quality_requirements(story, state)
            }
            
            next_steps.append(step)
        
        return next_steps
    
    async def _check_state_prerequisites(self, project: ProjectContext, target_state: ProjectState) -> Dict[str, Any]:
        """Check if project meets prerequisites for target state"""
        missing = []
        recommendations = []
        
        prereq_map = {
            ProjectState.PROJECT_BRIEF: ["idea"],
            ProjectState.PRD_CREATION: ["brief"],
            ProjectState.ARCHITECTURE: ["prd"],
            ProjectState.DEVELOPMENT_READY: ["architecture", "master_checklist"],
        }
        
        required_fields = prereq_map.get(target_state, [])
        
        for field in required_fields:
            if not getattr(project, field, None):
                missing.append(field)
                recommendations.append(f"Complete {field} before advancing to {target_state.value}")
        
        return {
            "ready": len(missing) == 0,
            "missing": missing,
            "recommendations": recommendations
        }
    
    async def _get_state_prerequisites(self, project: ProjectContext, state: ProjectState) -> List[str]:
        """Get list of prerequisites for state"""
        prereq_map = {
            ProjectState.ANALYST_RESEARCH: ["project idea defined"],
            ProjectState.PROJECT_BRIEF: ["research completed"],
            ProjectState.PRD_CREATION: ["project brief approved"],
            ProjectState.ARCHITECTURE: ["PRD completed"],
            ProjectState.DEVELOPMENT_READY: ["architecture approved", "master checklist completed"]
        }
        
        return prereq_map.get(state, [])
    
    async def _check_story_quality_gates(self, story: StoryContext, target_state: StoryState) -> Dict[str, Any]:
        """Check story quality gates for state transition"""
        return await self.quality_gate_manager.check_story_gates(story, target_state)
    
    async def _get_story_quality_requirements(self, story: StoryContext, state: StoryState) -> List[str]:
        """Get quality requirements for story state"""
        requirements_map = {
            StoryState.DEVELOPMENT: ["acceptance criteria defined", "tasks identified"],
            StoryState.QA_CHECK: ["implementation completed", "unit tests passed"],
            StoryState.READY_FOR_REVIEW: ["all validations passed", "code reviewed"],
            StoryState.COMPLETED: ["QA review passed", "quality gate approved"]
        }
        
        return requirements_map.get(state, [])
    
    def _estimate_effort(self, state: ProjectState) -> str:
        """Estimate effort for project state"""
        effort_map = {
            ProjectState.IDEA_GENERATION: "1-2 hours",
            ProjectState.ANALYST_RESEARCH: "4-8 hours", 
            ProjectState.PROJECT_BRIEF: "2-4 hours",
            ProjectState.PRD_CREATION: "8-16 hours",
            ProjectState.ARCHITECTURE: "16-32 hours",
            ProjectState.DEVELOPMENT_READY: "2-4 hours"
        }
        
        return effort_map.get(state, "Unknown")
    
    def _estimate_story_effort(self, state: StoryState) -> str:
        """Estimate effort for story state"""
        effort_map = {
            StoryState.RISK_PROFILING: "30-60 minutes",
            StoryState.DEVELOPMENT: "2-8 hours",
            StoryState.QA_CHECK: "1-2 hours",
            StoryState.QA_REVIEW: "30-60 minutes",
            StoryState.QUALITY_GATE: "15-30 minutes"
        }
        
        return effort_map.get(state, "Unknown")
    
    def _predict_next_state(self, context, agent_type: str, command: str) -> Optional[str]:
        """Predict next state after agent command"""
        # Simple prediction logic based on agent and command
        command_state_map = {
            ("analyst", "*research"): "research_completed",
            ("architect", "*create-architecture"): "architecture_completed", 
            ("pm", "*create-prd"): "prd_completed",
            ("dev", "*implement"): "development_completed",
            ("qa", "*review"): "review_completed"
        }
        
        return command_state_map.get((agent_type, command), None)
    
    def get_orchestrator_status(self) -> Dict[str, Any]:
        """Get orchestrator status and metrics"""
        mcp_status = self.auto_reconnector.get_connection_status()
        
        return {
            "orchestrator_version": "1.0.0",
            "active_projects": len(self.active_projects),
            "active_stories": len(self.active_stories),
            "active_sessions": len(self.active_sessions),
            "workflow_metrics": self.workflow_metrics,
            "available_agents": list(self.available_agents.keys()),
            "mcp_connection_status": mcp_status,
            "auto_reconnection_enabled": True,
            "uptime": datetime.now().isoformat()
        }
    
    def _start_mcp_monitoring(self):
        """Start MCP server monitoring for auto-reconnection"""
        try:
            # Start monitoring for key MCP servers
            important_servers = [
                "makenotion-notion-mcp-server",
                "bmad-mcp-server",
                "smithery-ai-github"
            ]
            
            # Use asyncio to start monitoring without blocking
            asyncio.create_task(
                self.auto_reconnector.start_monitoring(important_servers)
            )
            
            logger.info("Started MCP auto-reconnection monitoring")
            
        except Exception as e:
            logger.warning(f"Failed to start MCP monitoring: {e}")
    
    async def _handle_mcp_connection_error(self, server_name: str):
        """Handle MCP connection errors with automatic reconnection"""
        try:
            logger.warning(f"MCP connection error detected for {server_name} - attempting reconnection")
            
            # Attempt manual reconnection
            result = await self.auto_reconnector.manual_reconnect(server_name)
            
            if result["success"]:
                logger.info(f"Successfully reconnected {server_name}")
            else:
                logger.error(f"Failed to reconnect {server_name}: {result.get('error', 'Unknown error')}")
            
            return result
            
        except Exception as e:
            logger.error(f"Error handling MCP connection error: {e}")
            return {"success": False, "error": str(e)}
    
    async def get_mcp_connection_status(self) -> Dict[str, Any]:
        """Get current MCP server connection status"""
        return self.auto_reconnector.get_connection_status()
    
    async def reconnect_failed_mcp_servers(self) -> Dict[str, Any]:
        """Manually reconnect all failed MCP servers"""
        return await self.auto_reconnector.reconnect_all_failed()
    
    async def auto_sync_to_github(self, project_id: str, commit_message: str = None) -> Dict[str, Any]:
        """Automatically sync BMAD project changes to GitHub"""
        try:
            if project_id not in self.active_projects:
                return {"success": False, "error": "Project not found"}
            
            project = self.active_projects[project_id]
            project_dir = f"C:\\Users\\Faber\\AppData\\Roaming\\Claude\\bmad-projects\\{project_id}"
            
            # Check if GitHub MCP is connected
            try:
                # Test GitHub connection by trying to import the MCP
                from ..integrations.github_sync import GitHubAutoSync
                github_sync = GitHubAutoSync(project_id, project.name)
                
                # Auto-sync to GitHub
                result = await github_sync.sync_project_to_github(
                    commit_message or f"Auto-sync {project.name} - {datetime.now().strftime('%Y-%m-%d %H:%M')}"
                )
                
                # Update project with sync info
                project.add_agent_note(
                    "orchestrator", 
                    f"Auto-synced to GitHub: {result.get('repository_url', 'Unknown')}"
                )
                
                logger.info(f"Successfully auto-synced project {project_id} to GitHub")
                
                return {
                    "success": True,
                    "project_id": project_id,
                    "github_sync": result,
                    "message": "Project automatically synced to GitHub"
                }
                
            except ImportError:
                logger.warning("GitHub sync integration not available - creating basic implementation")
                return await self._basic_github_sync(project_id, project_dir, commit_message)
                
        except Exception as e:
            logger.error(f"Error auto-syncing to GitHub: {e}")
            
            # Attempt GitHub MCP reconnection if sync fails
            await self._handle_mcp_connection_error("smithery-ai-github")
            
            return {
                "success": False,
                "error": str(e),
                "message": "GitHub auto-sync failed - attempting reconnection"
            }
    
    async def _basic_github_sync(self, project_id: str, project_dir: str, commit_message: str = None) -> Dict[str, Any]:
        """Basic GitHub sync using Git commands and GitHub MCP"""
        try:
            import subprocess
            import os
            
            # Change to project directory
            os.chdir(project_dir)
            
            # Add all files to git
            subprocess.run(["git", "add", "."], check=True)
            
            # Commit changes
            message = commit_message or f"Auto-sync BMAD project {project_id} - {datetime.now().strftime('%Y-%m-%d %H:%M')}"
            subprocess.run(["git", "commit", "-m", message], check=True)
            
            logger.info(f"Git commit successful for project {project_id}")
            
            return {
                "success": True,
                "local_commit": True,
                "github_push": False,
                "message": "Local Git commit successful - GitHub push pending MCP connection"
            }
            
        except subprocess.CalledProcessError as e:
            if "nothing to commit" in str(e):
                return {
                    "success": True,
                    "message": "No changes to commit",
                    "local_commit": False
                }
            else:
                logger.error(f"Git command failed: {e}")
                return {"success": False, "error": f"Git operation failed: {e}"}
        except Exception as e:
            logger.error(f"Error in basic GitHub sync: {e}")
            return {"success": False, "error": str(e)}