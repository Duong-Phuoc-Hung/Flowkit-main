"""Flow Kit SDK — high-level domain-model interface."""

from agent.sdk.models.base import DomainModel  # noqa: F401
from agent.sdk.persistence.sqlite_repository import SQLiteRepository
from agent.sdk.services.operations import init_operations, OperationService

__all__ = ["DomainModel", "SQLiteRepository", "init_operations", "OperationService", "init_sdk"]


def init_sdk(flow_client) -> OperationService:
    """Bootstrap the SDK: create repo, wire into DomainModel, return OperationService."""
    repo = SQLiteRepository()
    return init_operations(flow_client, repo)
