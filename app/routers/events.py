from fastapi import APIRouter, HTTPException, status
from sqlmodel import select

from app.data.db import SessionDep
from app.models.event import Event
from app.models.user import User
from app.models.registration import Registration


router = APIRouter(prefix="/events", tags=["events"])


@router.post("/{id}/register", status_code=status.HTTP_201_CREATED)
def register_user_to_event(id: int, user: User, session: SessionDep) -> Registration:
    """Register a user to an event."""
    event = session.get(Event, id)

    if event is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found."
        )

    existing_user = session.get(User, user.username)

    if existing_user is None:
        session.add(user)
        session.commit()
        session.refresh(user)

    existing_registration = session.get(Registration, (user.username, id))

    if existing_registration is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User already registered to this event."
        )

    registration = Registration(username=user.username, event_id=id)

    session.add(registration)
    session.commit()
    session.refresh(registration)

    return registration


@router.delete("")
def delete_all_events(session: SessionDep) -> dict[str, str]:
    """Delete all events and all associated registrations."""
    registrations = session.exec(select(Registration)).all()

    for registration in registrations:
        session.delete(registration)

    events = session.exec(select(Event)).all()

    for event in events:
        session.delete(event)

    session.commit()

    return {"message": "All events deleted successfully."}


@router.delete("/{id}")
def delete_event(id: int, session: SessionDep) -> dict[str, str]:
    """Delete an event by id and all associated registrations."""
    event = session.get(Event, id)

    if event is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found."
        )

    registrations = session.exec(
        select(Registration).where(Registration.event_id == id)
    ).all()

    for registration in registrations:
        session.delete(registration)

    session.delete(event)
    session.commit()

    return {"message": "Event deleted successfully."}