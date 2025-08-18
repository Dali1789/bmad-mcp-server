"""
BMAD Workflow States
Definiert alle Workflow-Zustände basierend auf der BMAD-METHOD
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from datetime import datetime


class ProjectState(Enum):
    """Project-level workflow states"""
    IDEA_GENERATION = "idea_generation"
    ANALYST_RESEARCH = "analyst_research" 
    PROJECT_BRIEF = "project_brief"
    PRD_CREATION = "prd_creation"
    UX_DESIGN = "ux_design"
    ARCHITECTURE = "architecture"
    TEST_STRATEGY = "test_strategy"
    MASTER_CHECKLIST = "master_checklist"
    ALIGNMENT = "alignment"
    DEVELOPMENT_READY = "development_ready"
    IN_DEVELOPMENT = "in_development"
    COMPLETED = "completed"


class StoryState(Enum):
    """Story-level workflow states"""
    DRAFT = "draft"
    RISK_PROFILING = "risk_profiling"
    VALIDATION = "validation"
    DEVELOPMENT = "development"
    QA_CHECK = "qa_check"
    VALIDATION_TESTS = "validation_tests"
    READY_FOR_REVIEW = "ready_for_review"
    QA_REVIEW = "qa_review"
    QUALITY_GATE = "quality_gate"
    COMPLETED = "completed"
    BLOCKED = "blocked"


class WorkflowState(Enum):
    """Overall workflow states"""
    PLANNING = "planning"
    DEVELOPMENT = "development"
    QUALITY_ASSURANCE = "quality_assurance"
    REVIEW = "review"
    COMPLETED = "completed"
    PAUSED = "paused"
    ERROR = "error"


@dataclass
class ProjectContext:
    """Complete project context"""
    project_id: str
    name: str
    state: ProjectState
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    # Project artifacts
    idea: Optional[str] = None
    research: Optional[str] = None
    brief: Optional[str] = None
    prd: Optional[str] = None
    ux_design: Optional[str] = None
    architecture: Optional[str] = None
    test_strategy: Optional[str] = None
    master_checklist: Optional[Dict[str, Any]] = None
    
    # Agent assignments
    assigned_agents: Dict[str, str] = field(default_factory=dict)
    
    # Stories and epics
    epics: List[Dict[str, Any]] = field(default_factory=list)
    stories: List[Dict[str, Any]] = field(default_factory=list)
    
    # Quality metrics
    quality_gates: Dict[str, Any] = field(default_factory=dict)
    
    def update_state(self, new_state: ProjectState):
        """Update project state with timestamp"""
        self.state = new_state
        self.updated_at = datetime.now()


@dataclass
class StoryContext:
    """Individual story context"""
    story_id: str
    project_id: str
    title: str
    state: StoryState
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    # Story content
    description: Optional[str] = None
    acceptance_criteria: List[str] = field(default_factory=list)
    epic_id: Optional[str] = None
    
    # Development tracking
    tasks: List[Dict[str, Any]] = field(default_factory=list)
    current_task: Optional[str] = None
    
    # Quality tracking
    risk_profile: Optional[Dict[str, Any]] = None
    test_strategy: Optional[Dict[str, Any]] = None
    validation_results: Dict[str, Any] = field(default_factory=dict)
    qa_notes: List[str] = field(default_factory=list)
    
    # Agent tracking
    assigned_agents: Dict[str, str] = field(default_factory=dict)
    agent_notes: Dict[str, List[str]] = field(default_factory=dict)
    
    def update_state(self, new_state: StoryState):
        """Update story state with timestamp"""
        self.state = new_state
        self.updated_at = datetime.now()
    
    def add_agent_note(self, agent: str, note: str):
        """Add note from specific agent"""
        if agent not in self.agent_notes:
            self.agent_notes[agent] = []
        self.agent_notes[agent].append(f"{datetime.now().isoformat()}: {note}")


@dataclass
class WorkflowSession:
    """Current workflow session"""
    session_id: str
    project_id: str
    current_story_id: Optional[str]
    workflow_state: WorkflowState
    active_agent: Optional[str]
    
    # Session tracking
    started_at: datetime = field(default_factory=datetime.now)
    last_activity: datetime = field(default_factory=datetime.now)
    
    # Execution context
    current_step: Optional[str] = None
    pending_actions: List[Dict[str, Any]] = field(default_factory=list)
    completed_actions: List[Dict[str, Any]] = field(default_factory=list)
    
    # Quality tracking
    quality_checks: Dict[str, Any] = field(default_factory=dict)
    blockers: List[str] = field(default_factory=list)
    
    def update_activity(self):
        """Update last activity timestamp"""
        self.last_activity = datetime.now()
    
    def add_action(self, action_type: str, description: str, agent: str):
        """Add completed action"""
        action = {
            "type": action_type,
            "description": description,
            "agent": agent,
            "timestamp": datetime.now().isoformat(),
            "session_id": self.session_id
        }
        self.completed_actions.append(action)
        self.update_activity()
    
    def add_pending_action(self, action_type: str, description: str, assigned_agent: str):
        """Add pending action"""
        action = {
            "type": action_type,
            "description": description,
            "assigned_agent": assigned_agent,
            "created_at": datetime.now().isoformat(),
            "session_id": self.session_id
        }
        self.pending_actions.append(action)


# State Transition Maps
PROJECT_STATE_TRANSITIONS = {
    ProjectState.IDEA_GENERATION: [ProjectState.ANALYST_RESEARCH, ProjectState.PROJECT_BRIEF],
    ProjectState.ANALYST_RESEARCH: [ProjectState.PROJECT_BRIEF],
    ProjectState.PROJECT_BRIEF: [ProjectState.PRD_CREATION],
    ProjectState.PRD_CREATION: [ProjectState.UX_DESIGN, ProjectState.ARCHITECTURE],
    ProjectState.UX_DESIGN: [ProjectState.ARCHITECTURE],
    ProjectState.ARCHITECTURE: [ProjectState.TEST_STRATEGY, ProjectState.MASTER_CHECKLIST],
    ProjectState.TEST_STRATEGY: [ProjectState.MASTER_CHECKLIST],
    ProjectState.MASTER_CHECKLIST: [ProjectState.ALIGNMENT],
    ProjectState.ALIGNMENT: [ProjectState.DEVELOPMENT_READY],
    ProjectState.DEVELOPMENT_READY: [ProjectState.IN_DEVELOPMENT],
    ProjectState.IN_DEVELOPMENT: [ProjectState.COMPLETED],
}

STORY_STATE_TRANSITIONS = {
    StoryState.DRAFT: [StoryState.RISK_PROFILING, StoryState.VALIDATION, StoryState.DEVELOPMENT],
    StoryState.RISK_PROFILING: [StoryState.VALIDATION, StoryState.DEVELOPMENT],
    StoryState.VALIDATION: [StoryState.DEVELOPMENT],
    StoryState.DEVELOPMENT: [StoryState.QA_CHECK, StoryState.VALIDATION_TESTS, StoryState.READY_FOR_REVIEW],
    StoryState.QA_CHECK: [StoryState.DEVELOPMENT, StoryState.VALIDATION_TESTS],
    StoryState.VALIDATION_TESTS: [StoryState.READY_FOR_REVIEW, StoryState.DEVELOPMENT],
    StoryState.READY_FOR_REVIEW: [StoryState.QA_REVIEW],
    StoryState.QA_REVIEW: [StoryState.QUALITY_GATE, StoryState.DEVELOPMENT],
    StoryState.QUALITY_GATE: [StoryState.COMPLETED, StoryState.DEVELOPMENT],
}

# Agent Responsibility Mapping
AGENT_RESPONSIBILITIES = {
    "analyst": {
        "project_states": [ProjectState.ANALYST_RESEARCH],
        "story_states": [StoryState.RISK_PROFILING],
        "primary_commands": ["*research", "*analyze", "*risk"]
    },
    "architect": {
        "project_states": [ProjectState.ARCHITECTURE, ProjectState.TEST_STRATEGY],
        "story_states": [StoryState.DEVELOPMENT],
        "primary_commands": ["*create-architecture", "*design", "*review"]
    },
    "pm": {
        "project_states": [ProjectState.PROJECT_BRIEF, ProjectState.PRD_CREATION, ProjectState.MASTER_CHECKLIST],
        "story_states": [StoryState.DRAFT, StoryState.VALIDATION],
        "primary_commands": ["*create-prd", "*draft-story", "*validate"]
    },
    "dev": {
        "project_states": [ProjectState.IN_DEVELOPMENT],
        "story_states": [StoryState.DEVELOPMENT],
        "primary_commands": ["*implement", "*code", "*test"]
    },
    "qa": {
        "project_states": [ProjectState.TEST_STRATEGY, ProjectState.MASTER_CHECKLIST],
        "story_states": [StoryState.QA_CHECK, StoryState.QA_REVIEW, StoryState.QUALITY_GATE],
        "primary_commands": ["*risk", "*design", "*trace", "*nfr", "*review", "*gate"]
    }
}