from datetime import datetime, timezone

from sqlmodel import select, func
from sqlmodel.ext.asyncio.session import AsyncSession

from app.models import Pipeline
from app.schemas import PipelineRequest, PipelineGetQuery, PipelineUpdateStage


class PipelineRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, pipeline_id):
        query = select(Pipeline).where(Pipeline.id == pipeline_id)
        return await self.db.scalar(query)

    async def create(self, payload: PipelineRequest):
        pipeline = Pipeline(**payload.model_dump())
        self.db.add(pipeline)
        await self.db.commit()
        await self.db.refresh(pipeline)

        return await self.get_by_id(pipeline_id=pipeline.id)

    async def get_all(self, query_params: PipelineGetQuery):
        query = select(Pipeline)

        # FILTERING
        if query_params.deal_stage:
            query = query.where(Pipeline.deal_stage.in_(query_params.deal_stage))

        # DATE RANGE
        if query_params.date_from:
            query = query.where(Pipeline.created_at >= datetime.combine(query_params.date_from, datetime.min.time()))
        if query_params.date_to:
            query = query.where(Pipeline.created_at <= datetime.combine(query_params.date_to, datetime.min.time()))

        # SEARCH NAME
        if query_params.search:
            query = query.where(Pipeline.deal_name.ilike(f"%{query_params.search}%"))

        total_data = select(func.count()).select_from(query.subquery())
        total = await  self.db.scalar(total_data)

        # PAGINATION
        offset = (query_params.page - 1) * query_params.limit
        result = await  self.db.scalars(query.offset(offset).limit(query_params.limit))
        pipelines = result.all()

        return pipelines, total

    async def update(self, pipeline: Pipeline, payload: PipelineRequest):
        updated_data = payload.model_dump()

        for key, value in updated_data.items():
            setattr(pipeline, key, value)
        pipeline.updated_at = datetime.now(timezone.utc)

        await self.db.commit()
        await self.db.refresh(pipeline)

        return await self.get_by_id(pipeline_id=pipeline.id)

    async def update_stage(self, pipeline: Pipeline, payload: PipelineUpdateStage):
        pipeline.deal_stage = payload.deal_stage
        pipeline.updated_at = datetime.now(timezone.utc)

        await self.db.commit()
        await self.db.refresh(pipeline)

        return await self.get_by_id(pipeline_id=pipeline.id)
