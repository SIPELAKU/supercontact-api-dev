from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.db import get_async_session
from app.models import User
from app.schemas import PipelineGetQuery, ResponseModel, PipelineRequest, PipelineResponse, PipelineUpdateStage, \
    PipelineAssignedUsers
from app.schemas.pipeline_schema import PipelineListResponse
from app.services import PipelineService

router = APIRouter(prefix="/pipelines", tags=["Pipelines"])


def get_pipeline_service(db: AsyncSession = Depends(get_async_session)):
    return PipelineService(db)


# GET ALL PIPELINES
@router.get(
    "",
    response_model=ResponseModel[PipelineListResponse],
    # dependencies=[Depends(auth_require)],
)
async def get_all_pipelines(
        query_params: PipelineGetQuery = Depends(),
        service: PipelineService = Depends(get_pipeline_service)
):
    data = await service.find_all_pipelines(query_params=query_params)
    return ResponseModel(data=PipelineListResponse(**data))


# FIND ACTIVE ASSIGNED USERS
@router.get(
    "/active-users",
    response_model=ResponseModel[PipelineAssignedUsers],
    #     dependencies=[Depends(auth_require)],
)
async def get_active_assigned_users(
        service: PipelineService = Depends(get_pipeline_service)
):
    data = await service.find_active_assigned_users()
    return ResponseModel(data=PipelineAssignedUsers(**data))


# GET ONE PIPELINE
@router.get(
    "/{pipeline_id}",
    response_model=ResponseModel[PipelineResponse],
    #     dependencies=[Depends(auth_require)],
)
async def get_pipeline_by_id(
        pipeline_id: UUID,
        service: PipelineService = Depends(get_pipeline_service)
):
    data = await service.find_one_pipeline(pipeline_id=pipeline_id)
    return ResponseModel(data=data)


# CREATE NEW PIPELINE
@router.post(
    "",
    response_model=ResponseModel[PipelineResponse],
)
async def create_new_pipeline(
        payload: PipelineRequest,
        # current_user=Depends(auth_require),
        db: AsyncSession = Depends(get_async_session),
        service: PipelineService = Depends(get_pipeline_service),
):
    query = await db.scalars(select(User))
    users = query.all()
    data = await service.create_pipeline(user_id=users[0].id, payload=payload)
    return ResponseModel(data=data)


# UPDATE OLD PIPELINE
@router.put(
    "/{pipeline_id}",
    response_model=ResponseModel[PipelineResponse],
    #     dependencies=[Depends(auth_require)],
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
    response_model=ResponseModel[PipelineResponse],
    #     dependencies=[Depends(auth_require)],
)
async def update_deal_stage_pipeline(
        pipeline_id: UUID,
        payload: PipelineUpdateStage,
        service: PipelineService = Depends(get_pipeline_service)
):
    data = await service.update_deal_stage(pipeline_id=pipeline_id, payload=payload)
    return ResponseModel(data=data)
