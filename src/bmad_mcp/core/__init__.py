"""
BMAD Core - Core functionality and system components
"""

from .bmad_loader import BMadLoader
from .project_detector import ProjectDetector
from .global_registry import BMadGlobalRegistry, global_registry
from .task_tracker import BMadTaskTracker, BMadTask
from .todowrite_bridge import TodoWriteBridge
from .notion_sync import NotionTaskSync
from .console_formatter import BMadConsoleFormatter
from .time_monitor import BMadTimeMonitor
from .simulator import BMadWorkDaySimulator
from .realtime_updater import BMadRealtimeUpdater
from .project_templates import BMadProjectTemplates, template_manager

__all__ = [
    'BMadLoader',
    'ProjectDetector', 
    'BMadGlobalRegistry',
    'global_registry',
    'BMadTaskTracker',
    'BMadTask',
    'TodoWriteBridge',
    'NotionTaskSync',
    'BMadConsoleFormatter',
    'BMadTimeMonitor',
    'BMadWorkDaySimulator',
    'BMadRealtimeUpdater',
    'BMadProjectTemplates',
    'template_manager'
]