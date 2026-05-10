from sqlalchemy.orm import Session
from app.models.order import Order,OrderStatus
from app.models.order_item import OrderItem
from app.schemas.checkout import CheckoutCreate
from app.services.cart_service import get_user_cart,get_cart_with_details,clear_cart
from app.services.coupon_service import get_coupon_by_code,calculate_discount
from app.services.trending_service import update_trending
from app.models.product import Product
from fastapi import HTTPException

def process_checkout(db:Session,user_id:int,data:CheckoutCreate)->Order:
    cart_details=get_cart_with_details(db,user_id)
    if not cart_details["items"]:
        raise HTTPException(status_code=400,detail="Cart is empty")
    subtotal=cart_details["total_amount"]
    discount=0.0
    coupon=None
    if data.discount_code:
        coupon=get_coupon_by_code(db,data.discount_code)
        if not coupon:
            raise HTTPException(status_code=400,detail="Invalid or inactive coupon")
        discount=calculate_discount(coupon,subtotal)
    final_amount=subtotal-discount
    try:
        order=Order(
            user_id=user_id,
            subtotal_amount=subtotal,
            discount_amount=discount,
            final_amount=final_amount,
            coupon_code=data.discount_code,
            status=OrderStatus.completed
        )
        db.add(order)
        db.flush() # Flush to get the order.id before committing
        for item in cart_details["items"]:
            product=db.query(Product).filter(Product.id==item["product_id"]).with_for_update().first()
            if not product or not product.is_active:
                raise HTTPException(status_code=400,detail=f"Product {item['product_id']} is no longer available")
            if product.product_stock<item["quantity"]:
                raise HTTPException(status_code=400,detail=f"Not enough stock for product {product.product_name}")
            product.product_stock-=item["quantity"]
            order_item=OrderItem(
                order_id=order.id,
                product_id=product.id,
                product_name_snapshot=product.product_name,
                price_snapshot=product.product_price,
                quantity=item["quantity"],
                line_total=item["subtotal"]
            )
            db.add(order_item)
            # Update Trending Stats
            update_trending(db,product.id,product.product_name,item["quantity"])
        # Clear the user's cart
        clear_cart(db,cart_details["id"])
        db.commit()
        db.refresh(order)
        return order
    except Exception as e:
        db.rollback()
        raise e
