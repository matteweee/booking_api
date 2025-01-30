from fastapi import APIRouter, Depends, Request
from fastapi.templating import Jinja2Templates

from app.routers.hotels_router import search_hotel

router = APIRouter(
    prefix="/pages",
    tags=["Frontend"],
)

templates = Jinja2Templates(directory="app/templates")


@router.get("/hotels")
async def hotels(request: Request, hotels=Depends(search_hotel)):
    return templates.TemplateResponse(
        name="hotels.html", context={"request": request, "hotels": hotels}
    )
