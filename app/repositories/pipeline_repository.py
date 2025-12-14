from datetime import datetime, timezone
from uuid import UUID

from dateutil.relativedelta import relativedelta
from sqlalchemy.orm import selectinload
from sqlmodel import select, func, update, or_, and_, case
from sqlmodel.ext.asyncio.session import AsyncSession

from app.models import Pipeline, Contact, DealStage, User
from app.schemas import PipelineRequest, PipelineGetQuery, PipelineUpdateStage


def calculate_change_and_trend(current: float, previous: float) -> dict:
    """
    Hitung persentase perubahan dan trend berdasarkan current vs previous
    """
    if previous == 0:
        change = 100.0 if current > 0 else 0.0
    else:
        change = ((current - previous) / previous) * 100

    if change > 0:
        trend = "up"
    elif change < 0:
        trend = "down"
    else:
        trend = "flat"

    return {"percent": round(change), "trend": trend}


class PipelineRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_client_by_id(self, client_id: UUID):
        query = select(Contact).where(Contact.id == client_id)
        return await self.db.scalar(query)

    async def get_active_assigned_users(self):
        query = (
            select(
                User.id,
                User.fullname,
                func.count(Pipeline.id).label("active_pipeline_count")
            )
            .join(Pipeline.user)
            .where(Pipeline.is_deleted == False)
            .group_by(User.id, User.fullname)
            .order_by(func.count(Pipeline.id).desc())
        )
        result = await self.db.exec(query)
        return result.all()

    async def get_by_id(
            self,
            pipeline_id: UUID,
            load_user: bool = False,
            load_contact: bool = False,
    ):
        query = select(Pipeline).where(Pipeline.id == pipeline_id)
        if load_user:
            query = query.options(selectinload(Pipeline.user))
        if load_contact:
            query = query.options(selectinload(Pipeline.contact))
        return await self.db.scalar(query)

    async def create(
            self,
            user_id: UUID,
            payload: PipelineRequest,
            load_user: bool = False,
            load_contact: bool = False
    ):
        pipeline = Pipeline(**payload.model_dump())
        pipeline.assigned_to = user_id
        self.db.add(pipeline)
        await self.db.commit()
        await self.db.refresh(pipeline)

        return await self.get_by_id(
            pipeline_id=pipeline.id,
            load_user=load_user,
            load_contact=load_contact
        )

    async def get_all(
            self,
            query_params: PipelineGetQuery,
            load_user: bool = False,
            load_contact: bool = False,
    ):
        now = datetime.now(timezone.utc)

        # FIX IT LATER (USE CORN JOB)
        # UPDATE IS CLOSED IF EXPECTED CLOSED LESS THAN NOW
        query = update(Pipeline).where(
            Pipeline.expected_close_date < now,
            Pipeline.deal_stage.notin_([DealStage.CLOSED_WON, DealStage.CLOSED_LOST]),
            Pipeline.is_deleted == False
        ).values(is_deleted=True)
        await self.db.exec(query)
        await self.db.commit()

        query = select(Pipeline)

        if load_user:
            query = query.options(selectinload(Pipeline.user))
        if load_contact:
            query = query.options(selectinload(Pipeline.contact))

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
            search = f"%{query_params.search}%"
            query = (
                query
                .join(Pipeline.contact)
                .where(
                    or_(
                        Pipeline.deal_name.ilike(search),
                        Contact.company.ilike(search),
                    )
                )
            )

        result = select(func.count()).select_from(Pipeline)
        total = await self.db.scalar(result)

        # PAGINATION
        result = await self.db.scalars(query)
        pipelines = result.all()

        return pipelines, total

    async def update(
            self,
            pipeline: Pipeline,
            payload: PipelineRequest,
            load_user: bool = False,
            load_contact: bool = False
    ):
        updated_data = payload.model_dump()

        for key, value in updated_data.items():
            setattr(pipeline, key, value)
        pipeline.updated_at = datetime.now(timezone.utc)

        await self.db.commit()
        await self.db.refresh(pipeline)

        return await self.get_by_id(
            pipeline_id=pipeline.id,
            load_user=load_user,
            load_contact=load_contact
        )

    async def update_stage(
            self,
            pipeline: Pipeline,
            payload: PipelineUpdateStage,
            load_user: bool = False,
            load_contact: bool = False
    ):
        pipeline.deal_stage = payload.deal_stage
        pipeline.updated_at = datetime.now(timezone.utc)

        await self.db.commit()
        await self.db.refresh(pipeline)

        return await self.get_by_id(
            pipeline_id=pipeline.id,
            load_user=load_user,
            load_contact=load_contact
        )

    async def get_pipeline_stats(self):
        now = datetime.now(timezone.utc)

        this_month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        next_month_start = this_month_start + relativedelta(months=1)
        last_month_start = this_month_start - relativedelta(months=1)

        # CONDITION FOR TOTAL AND AVERAGE
        pipeline_this_month_condition = or_(
            (
                    Pipeline.deal_stage.notin_([DealStage.CLOSED_WON, DealStage.CLOSED_LOST]) &
                    (Pipeline.is_deleted == False) &
                    (Pipeline.expected_close_date >= this_month_start) &
                    (Pipeline.expected_close_date < next_month_start)
            ),
            (
                    Pipeline.deal_stage.in_([DealStage.CLOSED_WON, DealStage.CLOSED_LOST]) &
                    (Pipeline.expected_close_date >= this_month_start) &
                    (Pipeline.expected_close_date < next_month_start)
            )
        )
        pipeline_last_month_condition = or_(
            (
                    Pipeline.deal_stage.notin_([DealStage.CLOSED_WON, DealStage.CLOSED_LOST]) &
                    (Pipeline.is_deleted == False) &
                    (Pipeline.expected_close_date >= last_month_start) &
                    (Pipeline.expected_close_date < this_month_start)
            ),
            (
                    Pipeline.deal_stage.in_([DealStage.CLOSED_WON, DealStage.CLOSED_LOST]) &
                    (Pipeline.expected_close_date >= last_month_start) &
                    (Pipeline.expected_close_date < this_month_start)
            )
        )

        # CONDITION FOR WINRATE
        closed_this_month = (
                Pipeline.deal_stage.in_([DealStage.CLOSED_WON, DealStage.CLOSED_LOST]) &
                (Pipeline.expected_close_date >= this_month_start) &
                (Pipeline.expected_close_date < next_month_start)
        )
        closed_last_month = (
                Pipeline.deal_stage.in_([DealStage.CLOSED_WON, DealStage.CLOSED_LOST]) &
                (Pipeline.expected_close_date >= last_month_start) &
                (Pipeline.expected_close_date < this_month_start)
        )

        total_this = func.coalesce(func.sum(case((pipeline_this_month_condition, Pipeline.amount))), 0)
        total_last = func.coalesce(func.sum(case((pipeline_last_month_condition, Pipeline.amount))), 0)
        avg_this = func.coalesce(func.avg(case((pipeline_this_month_condition, Pipeline.amount))), 0)
        avg_last = func.coalesce(func.avg(case((pipeline_last_month_condition, Pipeline.amount))), 0)

        total_closed_this = func.sum(case((closed_this_month, 1), else_=0))
        won_closed_this = func.sum(
            case((and_(closed_this_month, Pipeline.deal_stage == DealStage.CLOSED_WON), 1), else_=0))

        total_closed_last = func.sum(case((closed_last_month, 1), else_=0))
        won_closed_last = func.sum(
            case((and_(closed_last_month, Pipeline.deal_stage == DealStage.CLOSED_WON), 1), else_=0))

        winrate_this = (won_closed_this * 100.0 / func.nullif(total_closed_this, 0))
        winrate_last = (won_closed_last * 100.0 / func.nullif(total_closed_last, 0))

        query = select(
            total_this.label("total_this_month"),
            total_last.label("total_last_month"),
            avg_this.label("avg_this_month"),
            avg_last.label("avg_last_month"),
            winrate_this.label("winrate_this_month"),
            winrate_last.label("winrate_last_month"),
        )
        result = await self.db.exec(query)
        stats = result.one()

        total_info = calculate_change_and_trend(
            float(stats.total_this_month or 0), float(stats.total_last_month or 0)
        )
        avg_info = calculate_change_and_trend(
            float(stats.avg_this_month or 0), float(stats.avg_last_month or 0)
        )
        winrate_info = calculate_change_and_trend(
            float(stats.winrate_this_month or 0), float(stats.winrate_last_month or 0)
        )

        return {
            "total_pipeline": {
                "value": round(stats.total_this_month or 0),
                **total_info,
            },
            "avg_pipeline": {
                "value": round(stats.avg_this_month or 0),
                **avg_info,
            },
            "winrate_pipeline": {
                "value": round(stats.winrate_this_month or 0),
                **winrate_info,
            }
        }
