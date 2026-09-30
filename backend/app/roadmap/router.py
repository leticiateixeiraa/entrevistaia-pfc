import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.audit.service import record_event
from app.auth.dependencies import get_current_user
from app.models.base import get_db
from app.roadmap.models import LearningRoadmap, LearningRoadmapItem
from app.roadmap.schemas import RoadmapCreate, RoadmapItemStatusIn, RoadmapOut

router = APIRouter(prefix="/roadmaps", tags=["roadmaps"])


def _to_response(db: Session, roadmap: LearningRoadmap) -> RoadmapOut:
    items = db.query(LearningRoadmapItem).filter(
        LearningRoadmapItem.roadmap_id == roadmap.id
    ).order_by(LearningRoadmapItem.order_index).all()
    return RoadmapOut.model_validate({"id": roadmap.id, "title": roadmap.title,
        "objective": roadmap.objective, "created_at": roadmap.created_at,
        "updated_at": roadmap.updated_at, "items": items})


@router.post("", response_model=RoadmapOut, status_code=status.HTTP_201_CREATED)
def create_roadmap(
    payload: RoadmapCreate,
    user_id: str = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    roadmap = LearningRoadmap(user_id=uuid.UUID(user_id), title=payload.title, objective=payload.objective)
    db.add(roadmap)
    db.flush()
    db.add_all(LearningRoadmapItem(roadmap_id=roadmap.id, order_index=index,
        title=item.title, description=item.description) for index, item in enumerate(payload.items))
    record_event(db, "roadmap.created", uuid.UUID(user_id), "roadmap", str(roadmap.id))
    db.commit()
    db.refresh(roadmap)
    return _to_response(db, roadmap)


@router.get("", response_model=list[RoadmapOut])
def list_roadmaps(user_id: str = Depends(get_current_user), db: Session = Depends(get_db)):
    roadmaps = db.query(LearningRoadmap).filter(
        LearningRoadmap.user_id == uuid.UUID(user_id)
    ).order_by(LearningRoadmap.created_at.desc()).all()
    return [_to_response(db, roadmap) for roadmap in roadmaps]


@router.patch("/{roadmap_id}/items/{item_id}", response_model=RoadmapOut)
def update_item_status(
    roadmap_id: uuid.UUID,
    item_id: uuid.UUID,
    payload: RoadmapItemStatusIn,
    user_id: str = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    roadmap = db.query(LearningRoadmap).filter(
        LearningRoadmap.id == roadmap_id, LearningRoadmap.user_id == uuid.UUID(user_id)
    ).first()
    item = db.query(LearningRoadmapItem).filter(
        LearningRoadmapItem.id == item_id, LearningRoadmapItem.roadmap_id == roadmap_id
    ).first()
    if not roadmap or not item:
        raise HTTPException(status_code=404, detail="Roadmap ou etapa não encontrada")
    item.status = payload.status
    record_event(db, "roadmap.item_updated", uuid.UUID(user_id), "roadmap_item", str(item.id), {"status": payload.status})
    db.commit()
    db.refresh(roadmap)
    return _to_response(db, roadmap)