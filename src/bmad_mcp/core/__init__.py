"""
BMAD Core System - Project detection and BMAD configuration loading
"""

from .bmad_loader import BMadLoader
from .project_detector import ProjectDetector

__all__ = ["BMadLoader", "ProjectDetector"]