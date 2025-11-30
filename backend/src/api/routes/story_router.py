from fastapi import APIRouter
from ...storytelling.story_service import generate_story_for_item

router = APIRouter()

@router.get("/items/{item_id}/story")
def get_item_story(item_id: int):
    return generate_story_for_item(item_id)
