"""Testing utilities."""

from datetime import datetime, timedelta
from typing import Any, Sequence
from uuid import uuid4

from common.testing.factories import EmptyListFactory
from issues import IssueSeverity, PipelineAssetUnion
from polyfactory import Ignore, Use
from polyfactory.factories.sqlalchemy_factory import SQLAlchemyFactory

from ..models.testing import build_timestamp
from .models import IssueEntity, IssueFindingRelationEntity, ResourcesWrapper


class IssueEntityFactory(SQLAlchemyFactory[IssueEntity]):
    """Factory."""

    __set_as_default_factory_for_type__ = True

    finding_ids = EmptyListFactory
    issue_id = Use(lambda: str(uuid4()))

    @classmethod
    def build(
        cls,
        issue_finding_relations: list[IssueFindingRelationEntity] | None = None,
        resources: Sequence[PipelineAssetUnion] | None = None,
        resources_wrapper: ResourcesWrapper | Ignore | None = None,
        timestamp: datetime | timedelta | None = None,
        **kwargs: Any,
    ) -> IssueEntity:
        """Build model."""
        if "severity" not in kwargs:
            kwargs["severity"] = IssueSeverity.low

        if resources_wrapper is None:
            kwargs["resources_wrapper"] = build_resources(resources)

        kwargs["timestamp"] = build_timestamp(timestamp)

        entity = super().build(**kwargs)
        return entity
