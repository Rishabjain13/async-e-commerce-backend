from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import select as core_select
from app.models.cart import Cart
from app.models.cart_item import CartItem
from app.models.inventory import Inventory
from app.models.order import Order
from app.models.order_item import OrderItem
from app.models.price import Price


async def place_order(db: AsyncSession, user_id: int):
    async with db.begin():

        # Get cart
        result = await db.execute(
            select(Cart).where(Cart.user_id == user_id)
        )
        cart = result.scalar_one_or_none()

        if not cart:
            return None

        # Get cart items
        result = await db.execute(
            select(CartItem).where(CartItem.cart_id == cart.id)
        )
        items = result.scalars().all()

        if not items:
            return None

        total = 0
        order_items = []

        for item in items:
            # Lock inventory row
            result = await db.execute(
                core_select(Inventory)
                .where(Inventory.variant_id == item.variant_id)
                .with_for_update()
            )
            inventory = result.scalar_one()

            if inventory.quantity < item.quantity:
                raise Exception("Out of stock")

            # Deduct stock
            inventory.quantity -= item.quantity

            # Get price
            price_result = await db.execute(
                select(Price)
                .join_from(Price, Inventory,
                           Price.product_id == Inventory.variant_id)
            )

            price = price_result.scalar_one_or_none()
            item_price = price.amount if price else 0

            total += item_price * item.quantity

            order_items.append({
                "variant_id": item.variant_id,
                "quantity": item.quantity,
                "price": item_price
            })

        # Create order
        order = Order(
            user_id=user_id,
            total_amount=total
        )
        db.add(order)
        await db.flush()

        # Create order items
        for oi in order_items:
            db.add(
                OrderItem(
                    order_id=order.id,
                    variant_id=oi["variant_id"],
                    quantity=oi["quantity"],
                    price=oi["price"]
                )
            )

        # Clear cart
        await db.execute(
            core_select(CartItem)
            .where(CartItem.cart_id == cart.id)
            .execution_options(synchronize_session="fetch")
        )
        for item in items:
            await db.delete(item)

    return order
