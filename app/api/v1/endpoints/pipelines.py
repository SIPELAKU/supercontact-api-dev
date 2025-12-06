from uuid import UUID

from fastapi import APIRouter, Depends
from sqlmodel.ext.asyncio.session import AsyncSession

from app.db import get_async_session
from app.schemas import PipelineGetQuery, ResponseModel, PipelineRequest, PipelineResponse, PipelineUpdateStage
from app.schemas.pipeline_schema import PipelineListResponse
from app.services import PipelineService

router = APIRouter(prefix="/pipelines", tags=["Pipelines"])


def get_pipeline_service(db: AsyncSession = Depends(get_async_session)):
    return PipelineService(db)


# GET ALL PIPELINES
@router.get(
    "",
    response_model=ResponseModel[PipelineListResponse]
)
async def get_all_pipelines(
        query_params: PipelineGetQuery = Depends(),
        service: PipelineService = Depends(get_pipeline_service)
):
    data = await service.find_all_pipelines(query_params=query_params)
    return ResponseModel(data=PipelineListResponse(**data))


# CREATE NEW PIPELINE
@router.post(
    "",
    response_model=ResponseModel[PipelineResponse]
)
async def create_new_pipeline(
        payload: PipelineRequest,
        service: PipelineService = Depends(get_pipeline_service)
):
    data = await service.create_pipeline(payload=payload)
    return ResponseModel(data=data)


# UPDATE OLD PIPELINE
@router.put(
    "/{pipeline_id}",
    response_model=ResponseModel[PipelineResponse]
)
async def update_pipeline_by_id(
        pipeline_id: UUID,
        payload: PipelineRequest,
        service: PipelineService = Depends(get_pipeline_service)
):
    data = await service.update_pipeline(pipeline_id=pipeline_id, payload=payload)
    return ResponseModel(data=data)


# UPDATE OLD PIPELINE
@router.patch(
    "/{pipeline_id}/stage",
    response_model=ResponseModel[PipelineResponse]
)
async def update_deal_stage_pipeline(
        pipeline_id: UUID,
        payload: PipelineUpdateStage,
        service: PipelineService = Depends(get_pipeline_service)
):
    data = await service.update_deal_stage(pipeline_id=pipeline_id, payload=payload)
    return ResponseModel(data=data)
