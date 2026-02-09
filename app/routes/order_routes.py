from fastapi import APIRouter, Depends, HTTPException
from app.database.session import get_db
from app.controllers.order_controller import place_order

router = APIRouter(prefix="/orders", tags=["Orders"])

USER_ID = 1


@router.post("/")
async def create_order(db=Depends(get_db)):
    order = await place_order(db, USER_ID)
    if not order:
        raise HTTPException(status_code=400, detail="Cart is empty")
    return {
        "order_id": order.id,
        "total_amount": order.total_amount,
        "status": order.status
    }
