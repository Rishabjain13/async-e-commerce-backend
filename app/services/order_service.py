import asyncio
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.order import Order
from app.models.order_item import OrderItem
from app.models.payment import Payment


async def get_order_details(db: AsyncSession, order_id: int):
    """
    Fetch order, items, and payment concurrently.
    """

    async def fetch_order():
        result = await db.execute(
            select(Order).where(Order.id == order_id)
        )
        return result.scalar_one_or_none()

    async def fetch_items():
        result = await db.execute(
            select(OrderItem).where(OrderItem.order_id == order_id)
        )
        return result.scalars().all()

    async def fetch_payment():
        result = await db.execute(
            select(Payment).where(Payment.order_id == order_id)
        )
        return result.scalar_one_or_none()

    order, items, payment = await asyncio.gather(
        fetch_order(),
        fetch_items(),
        fetch_payment()
    )

    if not order:
        return None

    return {
        "order": order,
        "items": items,
        "payment": payment
    }
