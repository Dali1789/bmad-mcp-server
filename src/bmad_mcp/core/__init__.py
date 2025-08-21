"""
BMAD Core - Core functionality and system components
"""

from .bmad_core_loader import BMadCoreLoader as BMadLoader
from .project_detector import ProjectDetector
from .global_registry import BMadGlobalRegistry, global_registry
from .task_tracker import BMadTaskTracker, BMadTask
from .todowrite_bridge import TodoWriteBridge
from .notion_sync import NotionTaskSync
from .console_formatter import BMadConsoleFormatter
from .realtime_updater import BMadRealtimeUpdater
from .project_templates import BMadProjectTemplates, template_manager
from .time_monitor import BMadTimeMonitor, BMadWorkDaySimulator

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
    'BMadRealtimeUpdater',
    'BMadProjectTemplates',
    'template_manager',
    'BMadTimeMonitor',
    'BMadWorkDaySimulator'
]