"""
Core MG8 Gate Engine
Deterministic DAG execution with ADSR gating control
"""

from .executor import Executor
from .loader import load_project, MGateProject
from .validator import validate_mg8, validate_gate_contract, validate_qson
from .audit import AuditLog
from .model_adapter import call_model

__all__ = [
    "Executor",
    "load_project",
    "MGateProject",
    "validate_mg8",
    "validate_gate_contract",
    "validate_qson",
    "AuditLog",
    "call_model",
]
