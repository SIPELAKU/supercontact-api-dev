from math import ceil
from uuid import UUID

from app.exceptions import AppException
from app.repositories import PipelineRepository
from app.schemas import PipelineRequest, PipelineGetQuery, ErrorCode, PipelineUpdateStage


class PipelineService:
    def __init__(self, db):
        self.repo = PipelineRepository(db)

    # CREATE NEW PIPELINE
    async def create_pipeline(self, user_id: UUID, payload: PipelineRequest):
        client = await self.repo.get_client_by_id(client_id=payload.client_account)
        if not client:
            raise AppException(
                status_code=404,
                code=ErrorCode.NOT_FOUND,
                message="Client account not found"
            )
        return await self.repo.create(
            user_id=user_id,
            payload=payload,
            load_user=True,
            load_contact=True,
        )

    # GET ALL PIPELINES
    async def find_all_pipelines(self, query_params: PipelineGetQuery):
        pipelines, total = await self.repo.get_all(
            query_params=query_params,
            load_user=True,
            load_contact=True,
        )
        if not total or not query_params.limit:
            total_pages = 1
            query_params.page = 1
        else:
            total_pages = ceil(total / query_params.limit)
        stats = await self.repo.get_pipeline_stats()
        return {
            "total": total,
            "page": query_params.page,
            "limit": query_params.limit,
            "total_pages": total_pages,
            "stats": stats,
            "pipelines": pipelines,
        }

    # GET ONE PIPELINE
    async def find_one_pipeline(self, pipeline_id: UUID):
        pipeline = await self.repo.get_by_id(
            pipeline_id=pipeline_id,
            load_user=True,
            load_contact=True,
        )
        if not pipeline:
            raise AppException(
                status_code=404,
                code=ErrorCode.NOT_FOUND,
                message="Pipeline not found"
            )
        return pipeline

    # UPDATE PIPELINE
    async def update_pipeline(self, pipeline_id: UUID, payload: PipelineRequest):
        pipeline = await self.repo.get_by_id(pipeline_id=pipeline_id)
        if not pipeline:
            raise AppException(
                status_code=404,
                code=ErrorCode.NOT_FOUND,
                message="Pipeline not found"
            )
        client = await self.repo.get_client_by_id(client_id=payload.client_account)
        if not client:
            raise AppException(
                status_code=404,
                code=ErrorCode.NOT_FOUND,
                message="Client account not found"
            )

        return await self.repo.update(
            pipeline=pipeline,
            payload=payload,
            load_user=True,
            load_contact=True,
        )

    # UPDATE DEAL STAGE
    async def update_deal_stage(self, pipeline_id: UUID, payload: PipelineUpdateStage):
        pipeline = await self.repo.get_by_id(pipeline_id=pipeline_id)
        if not pipeline:
            raise AppException(
                status_code=404,
                code=ErrorCode.NOT_FOUND,
                message="Pipeline not found"
            )

        return await self.repo.update_stage(
            pipeline=pipeline,
            payload=payload,
            load_user=True,
            load_contact=True,
        )

    # FIND ACTIVE ASSIGNED USERS
    async def find_active_assigned_users(self):
        users = await self.repo.get_active_assigned_users()
        return {
            "total": len(users),
            "users": users,
        }
