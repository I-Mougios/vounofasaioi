# src/reservations/routers/events.py
from typing import AsyncGenerator

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from database.schema import EventORM
from models.responses import EventResponse
from models.schema import AdminModel, EventModel
from reservations.dependencies import get_current_admin, open_async_session

router = APIRouter(prefix="/events", tags=["events"])


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
    session: AsyncGenerator[AsyncSession, None] = Depends(open_async_session),
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
