from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy.orm import selectinload
from sqlmodel import select, func, update, extract, case, or_
from sqlmodel.ext.asyncio.session import AsyncSession

from app.models import Pipeline, Contact, DealStage
from app.schemas import PipelineRequest, PipelineGetQuery, PipelineUpdateStage


class PipelineRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_client_by_id(self, client_id: UUID):
        query = select(Contact).where(Contact.id == client_id)
        return await self.db.scalar(query)

    async def get_by_id(self, pipeline_id: UUID, load_contact: bool = False):
        query = select(Pipeline).where(Pipeline.id == pipeline_id)
        if load_contact:
            query = query.options(selectinload(Pipeline.contact))
        return await self.db.scalar(query)

    async def create(self, payload: PipelineRequest, load_contact: bool = False):
        pipeline = Pipeline(**payload.model_dump())
        self.db.add(pipeline)
        await self.db.commit()
        await self.db.refresh(pipeline)

        return await self.get_by_id(pipeline_id=pipeline.id, load_contact=load_contact)

    async def get_all(self, query_params: PipelineGetQuery, load_contact: bool = False):
        now = datetime.now(timezone.utc)

        # FIX IT LATER (USE CORN JOB)
        # UPDATE IS CLOSED IF EXPECTED CLOSED LESS THAN NOW
        query = update(Pipeline).where(
            Pipeline.expected_close_date < now,
            Pipeline.deal_stage.notin_([DealStage.CLOSED_WON, DealStage.CLOSED_LOST]),
            Pipeline.is_deleted == False
        ).values(is_deleted=True)
        await self.db.execute(query)
        await self.db.commit()

        query = select(Pipeline)

        if load_contact:
            query = query.options(selectinload(Pipeline.contact))

        if query_params.limit == 0:
            total_data = select(func.count()).select_from(query.subquery())
            total = await self.db.scalar(total_data)
            result = await self.db.scalars(query.where(
                Pipeline.expected_close_date >= now,
                Pipeline.is_deleted == False
            ))
            pipelines = result.all()

            return pipelines, total

        # DATE RANGE OR DEFAULT DATETIME
        date_from = query_params.date_from or datetime(now.year, now.month, 1)
        date_to = query_params.date_to or datetime(now.year, now.month, 1).replace(
            day=31, hour=23, minute=59, second=59, microsecond=999999
        )
        query = query.where(Pipeline.created_at >= date_from)
        query = query.where(Pipeline.created_at <= date_to)

        # FILTERING
        if query_params.deal_stage:
            query = query.where(Pipeline.deal_stage == query_params.deal_stage)

        # SEARCH NAME
        if query_params.search:
            query = query.where(Pipeline.deal_name.ilike(f"%{query_params.search}%"))

        total_data = select(func.count()).select_from(query.subquery())
        total = await self.db.scalar(total_data)

        # PAGINATION
        offset = (query_params.page - 1) * query_params.limit
        result = await self.db.scalars(query.offset(offset).limit(query_params.limit))
        pipelines = result.all()

        return pipelines, total

    async def update(self, pipeline: Pipeline, payload: PipelineRequest, load_contact: bool = False):
        updated_data = payload.model_dump()

        for key, value in updated_data.items():
            setattr(pipeline, key, value)
        pipeline.updated_at = datetime.now(timezone.utc)

        await self.db.commit()
        await self.db.refresh(pipeline)

        return await self.get_by_id(pipeline_id=pipeline.id, load_contact=load_contact)

    async def update_stage(self, pipeline: Pipeline, payload: PipelineUpdateStage, load_contact: bool = False):
        pipeline.deal_stage = payload.deal_stage
        pipeline.updated_at = datetime.now(timezone.utc)

        await self.db.commit()
        await self.db.refresh(pipeline)

        return await self.get_by_id(pipeline_id=pipeline.id, load_contact=load_contact)

    async def get_pipeline_stats(self):
        now = datetime.now(timezone.utc)
        month = now.month
        year = now.year

        # Kondisi untuk total/avg: bulan ini & belum closed OR closed won/lost kapanpun
        total_condition = or_(
            ((Pipeline.deal_stage.notin_(["Closed - Won", "Closed - Lost"])) &
             (extract("month", Pipeline.expected_close_date) == month) &
             (extract("year", Pipeline.expected_close_date) == year) &
             (Pipeline.is_deleted == False)),
            ((Pipeline.deal_stage.in_(["Closed - Won", "Closed - Lost"])) &
             (Pipeline.is_deleted == False))
        )

        query = select(
            func.coalesce(func.sum(case((total_condition, Pipeline.amount))), 0).label("total_pipeline"),
            func.coalesce(func.avg(case((total_condition, Pipeline.amount))), 0).label("avg_pipeline"),
            # Winrate: closed won / total pipeline
            (func.coalesce(func.sum(case(((Pipeline.deal_stage == "Closed - Won") &
                                          (Pipeline.is_deleted == False), Pipeline.amount))), 0) /
             func.nullif(func.coalesce(func.sum(case((total_condition, Pipeline.amount))), 0), 0) * 100
             ).label("winrate_pipeline")
        )

        result = await self.db.execute(query)
        stats = result.one()
        print(stats)
        return {
            "total_pipeline": round(float(stats.total_pipeline or 0), 1),
            "avg_pipeline": round(float(stats.avg_pipeline or 0), 1),
            "winrate_pipeline": round(float(stats.winrate_pipeline or 0), 1),
        }
