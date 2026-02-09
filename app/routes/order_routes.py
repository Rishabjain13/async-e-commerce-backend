from fastapi import APIRouter, Depends, HTTPException
from app.database.session import get_db
from app.controllers.order_controller import place_order
from app.services.order_service import get_order_details

router = APIRouter(prefix="/orders", tags=["Orders"])

USER_ID = 1

@router.get("/{order_id}")
async def order_details(order_id: int, db=Depends(get_db)):
    data = await get_order_details(db, order_id)
    if not data:
        raise HTTPException(status_code=404, detail="Order not found")
    return data


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
