from typing import Annotated

from fastapi import APIRouter, HTTPException, Path
from sqlmodel import select

from app.data.db import SessionDep
from app.models.event import Event, EventCreate, EventPublic


router = APIRouter(prefix="/events")


@router.get("/")
def get_all_events(session: SessionDep) -> list[EventPublic]:
    """Restituisce la lista di tutti gli eventi disponibili."""
    events = session.exec(select(Event)).all()
    return events


@router.post("/")
def add_event(session: SessionDep, event: EventCreate):
    """Aggiunge un nuovo evento."""
    session.add(Event.model_validate(event))
    session.commit()
    return "Event successfully added"


@router.get("/{id}")
def get_event_by_id(
    session: SessionDep,
    id: Annotated[int, Path(description="The ID of the event to get")]
) -> EventPublic:
    """Restituisce l'evento con l'id specificato."""
    event = session.get(Event, id)

    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    return event


@router.put("/{id}")
def update_event(
    session: SessionDep,
    id: Annotated[int, Path(description="The ID of the event to update")],
    new_event: EventCreate
):
    """Aggiorna l'evento con l'id specificato."""
    event = session.get(Event, id)

    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    event.title = new_event.title
    event.description = new_event.description
    event.date = new_event.date
    event.location = new_event.location

    session.add(event)
    session.commit()

    return "Event successfully updated"