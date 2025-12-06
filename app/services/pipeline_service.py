from math import ceil

from app.repositories import PipelineRepository
from app.schemas import PipelineRequest, PipelineGetQuery


class PipelineService:
    def __init__(self, db):
        self.repo = PipelineRepository(db)

    # CREATE NEW PIPELINE
    async def create_pipeline(self, payload: PipelineRequest):
        return await self.repo.create(payload=payload)

    # GET ALL PIPELINES
    async def get_all_pipelines(self, query_params: PipelineGetQuery):
        pipelines, total = await self.repo.get_all(query_params=query_params)
        total_pages = ceil(total / query_params.limit) if total else 1

        return {
            "total": total,
            "page": query_params.page,
            "limit": query_params.limit,
            "total_pages": total_pages,
            "pipelines": pipelines,
        }
