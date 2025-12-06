from math import ceil
from uuid import UUID

from app.exceptions import AppException
from app.repositories import PipelineRepository
from app.schemas import PipelineRequest, PipelineGetQuery, ErrorCode, PipelineUpdateStage


class PipelineService:
    def __init__(self, db):
        self.repo = PipelineRepository(db)

    # CREATE NEW PIPELINE
    async def create_pipeline(self, payload: PipelineRequest):
        return await self.repo.create(payload=payload)

    # GET ALL PIPELINES
    async def find_all_pipelines(self, query_params: PipelineGetQuery):
        pipelines, total = await self.repo.get_all(query_params=query_params)
        total_pages = ceil(total / query_params.limit) if total else 1

        return {
            "total": total,
            "page": query_params.page,
            "limit": query_params.limit,
            "total_pages": total_pages,
            "pipelines": pipelines,
        }

    # UPDATE PIPELINE
    async def update_pipeline(self, pipeline_id: UUID, payload: PipelineRequest):
        pipeline = await  self.repo.get_by_id(pipeline_id=pipeline_id)
        if not pipeline:
            raise AppException(
                status_code=404,
                code=ErrorCode.NOT_FOUND,
                message="Pipeline not found"
            )

        return await self.repo.update(pipeline=pipeline, payload=payload)

    # UPDATE DEAL STAGE
    async def update_deal_stage(self, pipeline_id: UUID, payload: PipelineUpdateStage):
        pipeline = await  self.repo.get_by_id(pipeline_id=pipeline_id)
        if not pipeline:
            raise AppException(
                status_code=404,
                code=ErrorCode.NOT_FOUND,
                message="Pipeline not found"
            )

        return await self.repo.update_stage(pipeline=pipeline, payload=payload)
