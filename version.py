"""
Centralized Version Management for HealthWatch AI
Single source of truth for all version numbers across the project
"""

# Application version
__version__ = "1.0.0"

# Project metadata
PROJECT_NAME = "HealthWatch AI"
PROJECT_FULL_NAME = "HealthWatch AI - Digital Twin System"
PROJECT_DESCRIPTION = "Digital Twin for Hospital Records"
PROJECT_SUBTITLE = "Predictive Healthcare Analytics System"
PROJECT_STATUS = "Production Ready"

# Document metadata
DOCUMENT_TYPE = "Complete Project Workflow"

def get_version():
    """Get the current version string"""
    return __version__

def get_project_metadata():
    """Get all project metadata as a dictionary"""
    return {
        "name": PROJECT_NAME,
        "full_name": PROJECT_FULL_NAME,
        "description": PROJECT_DESCRIPTION,
        "subtitle": PROJECT_SUBTITLE,
        "version": __version__,
        "status": PROJECT_STATUS,
        "document_type": DOCUMENT_TYPE
    }
