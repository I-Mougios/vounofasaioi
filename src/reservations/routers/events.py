# src/reservations/routers/events.py
from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import PlainTextResponse
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from database.schema import EventORM
from models.responses import EventResponse
from models.schema import AdminModel, EventModel
from reservations.dependencies import get_current_admin, open_async_session

router = APIRouter(prefix="/events", tags=["events"])


@router.get(
    "",
    response_model=EventResponse,
    status_code=status.HTTP_200_OK,
    summary="Get event by name",
    responses={
        status.HTTP_200_OK: {"Description": "Event found"},
        status.HTTP_404_NOT_FOUND: {"Description": "Event not found"},
    },
)
async def get_event_by_name(
    event_name: str, session: AsyncSession = Depends(open_async_session)
) -> EventResponse:
    result = await session.execute(select(EventORM).filter_by(name=event_name))
    event_orm = result.scalar_one_or_none()
    if not event_orm:
        raise HTTPException(status_code=404, detail="Event not found")

    event_response = EventResponse.model_validate(event_orm)
    return event_response


@router.post(
    "/register",
    response_model=EventResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new event",
    description="""
Create a new event in the system.

This endpoint is restricted to administrators only.
Only authenticated users with admin privileges are allowed to register events.

Example: \n
{
    "id": 1,\n
    "name": "Beach Getaway",\n
    "description": "Relaxing weekend trip to the beach.",\n
    "status": "active",\n
    "start_location": "Athens",\n
    "destination": "Santorini",\n
    "departure_time_to": "2025-08-15T08:00:00+03:00",\n
    "arrival_time_to": "2025-08-15T12:00:00+03:00",\n
    "departure_time_return": "2025-08-17T17:00:00+03:00",\n
    "arrival_time_return": "2025-08-17T21:00:00+03:00",\n
    "event_start_date": "2025-08-15",\n
    "event_end_date": "2025-08-17",\n
    "reserved_seats": 15,\n
    "total_seats": 30,\n
    "price_per_seat": "120.00"
}
""",
    responses={
        status.HTTP_201_CREATED: {"description": "Event successfully created"},
        status.HTTP_400_BAD_REQUEST: {"description": "Invalid input or event creation failed"},
        status.HTTP_401_UNAUTHORIZED: {"description": "Authentication required"},
    },
)
async def register(
    event_model: EventModel,
    session: AsyncSession = Depends(open_async_session),
    _current_admin: AdminModel = Depends(get_current_admin),
) -> EventResponse:
    event_orm = EventORM.from_attributes(event_model)
    try:
        session.add(event_orm)
        await session.flush()
        await session.commit()
    except SQLAlchemyError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    await session.refresh(event_orm)

    return EventResponse.model_validate(event_orm)


@router.delete(
    "/delete",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete an event",
    description="Delete an event by name",
    responses={
        status.HTTP_204_NO_CONTENT: {"description": "Event successfully deleted"},
        status.HTTP_404_NOT_FOUND: {"description": "Invalid input or event creation failed"},
    },
)
async def delete_event(
    _get_current_admin: AdminModel = Depends(get_current_admin),
    session: AsyncSession = Depends(open_async_session),
    event_name: str = Query(
        ...,
        min_length=1,
        strip_whitespace=True,
        description="Name of the event to delete",
    ),
) -> PlainTextResponse:
    result = await session.execute(select(EventORM).filter_by(name=event_name))
    event_orm = result.scalar_one_or_none()

    if event_orm:
        await session.delete(event_orm)
        await session.commit()
        return PlainTextResponse(
            f"Event with name {event_name} successfully deleted.",
            status_code=status.HTTP_204_NO_CONTENT,
        )

    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found")
