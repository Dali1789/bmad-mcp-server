"""
BMAD Time and Cost Tracker - Precise project billing and cost calculation
Extends the existing task tracking with detailed time and AI cost tracking
"""

import asyncio
import json
import logging
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
import threading
import time
import uuid

logger = logging.getLogger(__name__)


@dataclass
class TimeSession:
    """Represents a time tracking session for a specific task/project"""
    id: str
    task_id: str
    project_id: str
    agent: str
    start_time: str
    end_time: Optional[str] = None
    duration_seconds: int = 0
    ai_model_used: Optional[str] = None
    tokens_input: int = 0
    tokens_output: int = 0
    cost_usd: float = 0.0
    session_type: str = "development"  # development, analysis, testing, etc.
    description: Optional[str] = None
    created_at: str = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now().isoformat()

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TimeSession':
        return cls(**data)

    def calculate_duration(self) -> int:
        """Calculate session duration in seconds"""
        if self.end_time:
            start = datetime.fromisoformat(self.start_time)
            end = datetime.fromisoformat(self.end_time)
            self.duration_seconds = int((end - start).total_seconds())
        return self.duration_seconds

    def get_duration_hours(self) -> float:
        """Get duration in hours"""
        return self.duration_seconds / 3600.0


@dataclass
class ProjectBillingSummary:
    """Summary for project billing"""
    project_id: str
    project_name: str
    total_hours: float
    total_cost_usd: float
    sessions_count: int
    agents_breakdown: Dict[str, Dict[str, Any]]
    models_breakdown: Dict[str, Dict[str, Any]]
    time_period: Dict[str, str]
    generated_at: str


class BMadTimeCostTracker:
    """Advanced time and cost tracking system for precise project billing"""
    
    def __init__(self, global_registry=None):
        self.global_registry = global_registry
        self.db_path = self._get_db_path()
        self.active_sessions: Dict[str, TimeSession] = {}
        self.ai_model_costs = self._load_model_costs()
        self.auto_tracking = False
        self.tracking_thread = None
        
        # Initialize database
        self._init_database()
    
    def _get_db_path(self) -> Path:
        """Get the database file path"""
        if self.global_registry:
            return Path(self.global_registry.global_bmad_home) / "time_cost_tracking.db"
        else:
            return Path.home() / ".bmad-global" / "time_cost_tracking.db"
    
    def _load_model_costs(self) -> Dict[str, Dict[str, float]]:
        """Load AI model costs per 1K tokens"""
        return {
            "claude-sonnet-4": {"input": 0.015, "output": 0.075},
            "claude-opus": {"input": 0.015, "output": 0.075},
            "claude-haiku": {"input": 0.00025, "output": 0.00125},
            "gpt-4o": {"input": 0.0025, "output": 0.01},
            "gpt-4o-mini": {"input": 0.00015, "output": 0.0006},
            "gpt-4": {"input": 0.03, "output": 0.06},
            "perplexity-sonar": {"input": 0.001, "output": 0.001},
            "gemini-pro": {"input": 0.0005, "output": 0.0015},
            "default": {"input": 0.001, "output": 0.002}
        }
    
    def _init_database(self):
        """Initialize SQLite database for time and cost tracking"""
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create time sessions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS time_sessions (
                id TEXT PRIMARY KEY,
                task_id TEXT NOT NULL,
                project_id TEXT NOT NULL,
                agent TEXT NOT NULL,
                start_time TEXT NOT NULL,
                end_time TEXT,
                duration_seconds INTEGER DEFAULT 0,
                ai_model_used TEXT,
                tokens_input INTEGER DEFAULT 0,
                tokens_output INTEGER DEFAULT 0,
                cost_usd REAL DEFAULT 0.0,
                session_type TEXT DEFAULT 'development',
                description TEXT,
                created_at TEXT NOT NULL
            )
        ''')
        
        # Create project billing cache table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS project_billing_cache (
                project_id TEXT PRIMARY KEY,
                last_calculation TEXT NOT NULL,
                total_hours REAL DEFAULT 0.0,
                total_cost_usd REAL DEFAULT 0.0,
                sessions_count INTEGER DEFAULT 0,
                cache_data TEXT NOT NULL
            )
        ''')
        
        # Create indexes for better performance
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_sessions_project ON time_sessions(project_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_sessions_task ON time_sessions(task_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_sessions_time ON time_sessions(start_time)')
        
        conn.commit()
        conn.close()
        
        logger.info("Time and cost tracking database initialized")
    
    def start_session(
        self,
        task_id: str,
        project_id: str,
        agent: str,
        session_type: str = "development",
        description: Optional[str] = None
    ) -> TimeSession:
        """Start a new time tracking session"""
        session_id = str(uuid.uuid4())
        
        session = TimeSession(
            id=session_id,
            task_id=task_id,
            project_id=project_id,
            agent=agent,
            start_time=datetime.now().isoformat(),
            session_type=session_type,
            description=description
        )
        
        self.active_sessions[session_id] = session
        logger.info(f"Started time session: {session_id} for task {task_id}")
        
        return session
    
    def end_session(
        self,
        session_id: str,
        ai_model_used: Optional[str] = None,
        tokens_input: int = 0,
        tokens_output: int = 0
    ) -> Optional[TimeSession]:
        """End a time tracking session and calculate costs"""
        session = self.active_sessions.get(session_id)
        if not session:
            logger.error(f"Session not found: {session_id}")
            return None
        
        # Set end time and calculate duration
        session.end_time = datetime.now().isoformat()
        session.calculate_duration()
        
        # Set AI model usage and calculate costs
        if ai_model_used:
            session.ai_model_used = ai_model_used
            session.tokens_input = tokens_input
            session.tokens_output = tokens_output
            session.cost_usd = self._calculate_ai_cost(ai_model_used, tokens_input, tokens_output)
        
        # Save to database
        self._save_session(session)
        
        # Remove from active sessions
        del self.active_sessions[session_id]
        
        logger.info(f"Ended session: {session_id}, Duration: {session.get_duration_hours():.2f}h, Cost: ${session.cost_usd:.4f}")
        
        return session
    
    def _calculate_ai_cost(self, model: str, input_tokens: int, output_tokens: int) -> float:
        """Calculate AI cost based on model and token usage"""
        costs = self.ai_model_costs.get(model, self.ai_model_costs["default"])
        
        input_cost = (input_tokens / 1000) * costs["input"]
        output_cost = (output_tokens / 1000) * costs["output"]
        
        return input_cost + output_cost
    
    def _save_session(self, session: TimeSession):
        """Save session to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO time_sessions 
            (id, task_id, project_id, agent, start_time, end_time, duration_seconds,
             ai_model_used, tokens_input, tokens_output, cost_usd, session_type, 
             description, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            session.id, session.task_id, session.project_id, session.agent,
            session.start_time, session.end_time, session.duration_seconds,
            session.ai_model_used, session.tokens_input, session.tokens_output,
            session.cost_usd, session.session_type, session.description, session.created_at
        ))
        
        conn.commit()
        conn.close()
    
    def get_project_billing_summary(
        self,
        project_id: str,
        project_name: str = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> ProjectBillingSummary:
        """Generate comprehensive billing summary for a project"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Build query with optional date filters
        query = '''
            SELECT * FROM time_sessions 
            WHERE project_id = ?
        '''
        params = [project_id]
        
        if start_date:
            query += ' AND start_time >= ?'
            params.append(start_date)
        
        if end_date:
            query += ' AND start_time <= ?'
            params.append(end_date)
        
        query += ' ORDER BY start_time DESC'
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        # Column names
        columns = [desc[0] for desc in cursor.description]
        sessions = [dict(zip(columns, row)) for row in rows]
        
        conn.close()
        
        if not sessions:
            return ProjectBillingSummary(
                project_id=project_id,
                project_name=project_name or project_id,
                total_hours=0.0,
                total_cost_usd=0.0,
                sessions_count=0,
                agents_breakdown={},
                models_breakdown={},
                time_period={"start": start_date or "N/A", "end": end_date or "N/A"},
                generated_at=datetime.now().isoformat()
            )
        
        # Calculate totals
        total_hours = sum(s['duration_seconds'] for s in sessions) / 3600.0
        total_cost = sum(s['cost_usd'] for s in sessions)
        
        # Agent breakdown
        agents_breakdown = {}
        for session in sessions:
            agent = session['agent']
            if agent not in agents_breakdown:
                agents_breakdown[agent] = {
                    "hours": 0.0,
                    "cost_usd": 0.0,
                    "sessions": 0,
                    "avg_hourly_cost": 0.0
                }
            
            agents_breakdown[agent]["hours"] += session['duration_seconds'] / 3600.0
            agents_breakdown[agent]["cost_usd"] += session['cost_usd']
            agents_breakdown[agent]["sessions"] += 1
        
        # Calculate average hourly cost for agents
        for agent_data in agents_breakdown.values():
            if agent_data["hours"] > 0:
                agent_data["avg_hourly_cost"] = agent_data["cost_usd"] / agent_data["hours"]
        
        # Model breakdown
        models_breakdown = {}
        for session in sessions:
            if session['ai_model_used']:
                model = session['ai_model_used']
                if model not in models_breakdown:
                    models_breakdown[model] = {
                        "usage_count": 0,
                        "total_input_tokens": 0,
                        "total_output_tokens": 0,
                        "total_cost_usd": 0.0
                    }
                
                models_breakdown[model]["usage_count"] += 1
                models_breakdown[model]["total_input_tokens"] += session['tokens_input']
                models_breakdown[model]["total_output_tokens"] += session['tokens_output']
                models_breakdown[model]["total_cost_usd"] += session['cost_usd']
        
        return ProjectBillingSummary(
            project_id=project_id,
            project_name=project_name or project_id,
            total_hours=total_hours,
            total_cost_usd=total_cost,
            sessions_count=len(sessions),
            agents_breakdown=agents_breakdown,
            models_breakdown=models_breakdown,
            time_period={"start": start_date or "N/A", "end": end_date or "N/A"},
            generated_at=datetime.now().isoformat()
        )
    
    def get_daily_tracking_report(self, date: Optional[str] = None) -> Dict[str, Any]:
        """Generate daily time tracking report"""
        if not date:
            date = datetime.now().strftime("%Y-%m-%d")
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM time_sessions 
            WHERE date(start_time) = date(?)
            ORDER BY start_time ASC
        ''', (date,))
        
        rows = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]
        sessions = [dict(zip(columns, row)) for row in rows]
        
        conn.close()
        
        # Calculate daily totals
        total_seconds = sum(s['duration_seconds'] for s in sessions)
        total_hours = total_seconds / 3600.0
        total_cost = sum(s['cost_usd'] for s in sessions)
        
        # Project breakdown
        projects = {}
        for session in sessions:
            project_id = session['project_id']
            if project_id not in projects:
                projects[project_id] = {
                    "hours": 0.0,
                    "cost": 0.0,
                    "sessions": []
                }
            
            projects[project_id]["hours"] += session['duration_seconds'] / 3600.0
            projects[project_id]["cost"] += session['cost_usd']
            projects[project_id]["sessions"].append({
                "time": session['start_time'],
                "task": session['task_id'],
                "agent": session['agent'],
                "duration": session['duration_seconds'] / 3600.0,
                "description": session['description']
            })
        
        return {
            "date": date,
            "total_hours": total_hours,
            "total_cost_usd": total_cost,
            "sessions_count": len(sessions),
            "projects": projects,
            "generated_at": datetime.now().isoformat()
        }
    
    def export_billing_data(
        self,
        project_id: str,
        export_format: str = "json",
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> str:
        """Export billing data in various formats"""
        summary = self.get_project_billing_summary(project_id, None, start_date, end_date)
        
        if export_format.lower() == "json":
            return json.dumps(asdict(summary), indent=2, ensure_ascii=False)
        
        elif export_format.lower() == "csv":
            return self._export_to_csv(project_id, start_date, end_date)
        
        elif export_format.lower() == "invoice":
            return self._generate_invoice_format(summary)
        
        else:
            raise ValueError(f"Unsupported export format: {export_format}")
    
    def _export_to_csv(self, project_id: str, start_date: Optional[str] = None, end_date: Optional[str] = None) -> str:
        """Export sessions to CSV format"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        query = '''
            SELECT task_id, agent, start_time, end_time, duration_seconds, 
                   ai_model_used, tokens_input, tokens_output, cost_usd, 
                   session_type, description
            FROM time_sessions 
            WHERE project_id = ?
        '''
        params = [project_id]
        
        if start_date:
            query += ' AND start_time >= ?'
            params.append(start_date)
        
        if end_date:
            query += ' AND start_time <= ?'
            params.append(end_date)
        
        query += ' ORDER BY start_time'
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        conn.close()
        
        # Create CSV content
        csv_lines = [
            "Task ID,Agent,Start Time,End Time,Duration (hours),AI Model,Input Tokens,Output Tokens,Cost (USD),Session Type,Description"
        ]
        
        for row in rows:
            duration_hours = row[4] / 3600.0 if row[4] else 0.0
            csv_lines.append(
                f'"{row[0]}","{row[1]}","{row[2]}","{row[3]}",{duration_hours:.2f},'
                f'"{row[5] or ""}",{row[6]},{row[7]},{row[8]:.4f},'
                f'"{row[9]}","{row[10] or ""}"'
            )
        
        return "\n".join(csv_lines)
    
    def _generate_invoice_format(self, summary: ProjectBillingSummary) -> str:
        """Generate invoice-style billing report"""
        invoice = f"""
BMAD PROJECT BILLING INVOICE
{'=' * 50}

Project: {summary.project_name} ({summary.project_id})
Period: {summary.time_period['start']} to {summary.time_period['end']}
Generated: {summary.generated_at}

SUMMARY:
--------
Total Hours: {summary.total_hours:.2f} h
Total Cost: ${summary.total_cost_usd:.2f}
Sessions: {summary.sessions_count}

AGENT BREAKDOWN:
----------------
"""
        
        for agent, data in summary.agents_breakdown.items():
            invoice += f"{agent:15} | {data['hours']:8.2f}h | ${data['cost_usd']:8.2f} | ${data['avg_hourly_cost']:6.2f}/h\n"
        
        if summary.models_breakdown:
            invoice += "\nAI MODEL USAGE:\n---------------\n"
            for model, data in summary.models_breakdown.items():
                invoice += f"{model:20} | {data['usage_count']:3} uses | ${data['total_cost_usd']:8.2f}\n"
        
        invoice += f"\n{'=' * 50}\nTOTAL AMOUNT: ${summary.total_cost_usd:.2f}\n{'=' * 50}"
        
        return invoice
    
    def get_active_sessions(self) -> List[TimeSession]:
        """Get all currently active sessions"""
        return list(self.active_sessions.values())
    
    def auto_end_stale_sessions(self, max_hours: int = 8):
        """Automatically end sessions that have been running too long"""
        current_time = datetime.now()
        ended_sessions = []
        
        for session_id, session in list(self.active_sessions.items()):
            start_time = datetime.fromisoformat(session.start_time)
            duration = current_time - start_time
            
            if duration.total_seconds() / 3600 > max_hours:
                # Auto-end the stale session
                ended_session = self.end_session(session_id)
                if ended_session:
                    ended_sessions.append(ended_session)
                    logger.warning(f"Auto-ended stale session: {session_id} (duration: {duration})")
        
        return ended_sessions
    
    def cleanup_database(self, days_to_keep: int = 365):
        """Clean up old tracking data"""
        cutoff_date = (datetime.now() - timedelta(days=days_to_keep)).isoformat()
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM time_sessions WHERE start_time < ?', (cutoff_date,))
        deleted_count = cursor.rowcount
        
        conn.commit()
        conn.close()
        
        logger.info(f"Cleaned up {deleted_count} old tracking records")
        return deleted_count