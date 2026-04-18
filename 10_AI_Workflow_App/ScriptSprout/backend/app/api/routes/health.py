from fastapi import APIRouter, status

from app.schemas.health import HealthResponse

router = APIRouter()


@router.get(
    "/health",
    response_model=HealthResponse,
    status_code=status.HTTP_200_OK,
    summary="Liveness check",
    description="Returns 200 when the API process is running. Does not check downstream services.",
    tags=["health"],
)
def get_health() -> HealthResponse:
    """Retrieve data needed for this operation.

    Returns:
        Result generated for the caller.

    """

    return HealthResponse(status="ok", service="scriptsprout")
