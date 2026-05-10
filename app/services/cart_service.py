from typing import Optional
from sqlalchemy.orm import Session
from app.models.cart import Cart
from app.models.cart_item import CartItem
from app.models.product import Product
from app.schemas.cart import AddCartItem
from fastapi import HTTPException

def get_user_cart(db:Session,user_id:int)->Cart:
    cart=db.query(Cart).filter(Cart.user_id==user_id).first()
    if not cart:
        cart=Cart(user_id=user_id)
        db.add(cart)
        db.commit()
        db.refresh(cart)
    return cart

def get_cart_with_details(db:Session,user_id:int)->dict:
    cart=get_user_cart(db,user_id)
    items=db.query(CartItem).filter(CartItem.cart_id==cart.id).all()
    response_items=[]
    total_amount=0.0
    for item in items:
        product=db.query(Product).filter(Product.id==item.product_id).first()
        if not product:
            continue
        subtotal=product.product_price*item.quantity
        total_amount+=subtotal
        
        response_items.append({
            "id":item.id,
            "product_id":item.product_id,
            "quantity":item.quantity,
            "subtotal":subtotal
        })
    return {
        "id":cart.id,
        "items":response_items,
        "total_amount":total_amount,
        "discount_amount":0.0,
        "final_amount":total_amount
    }

def add_item_to_cart(db:Session,user_id:int,data:AddCartItem)->CartItem:
    cart=get_user_cart(db,user_id)
    product=db.query(Product).filter(Product.id==data.product_id,Product.is_active==True).first()
    if not product:
        raise HTTPException(status_code=404,detail="Product not found or inactive")
    if product.product_stock<data.quantity:
        raise HTTPException(status_code=400,detail="Not enough stock")
    cart_item=db.query(CartItem).filter(CartItem.cart_id==cart.id,CartItem.product_id==data.product_id).first()
    if cart_item:
        cart_item.quantity+=data.quantity
        if product.product_stock<cart_item.quantity:
            raise HTTPException(status_code=400,detail="Not enough stock")
    else:
        cart_item=CartItem(
            cart_id=cart.id,
            product_id=data.product_id,
            quantity=data.quantity
        )
        db.add(cart_item)
    db.commit()
    db.refresh(cart_item)
    return cart_item

def update_cart_item(db:Session,user_id:int,item_id:int,quantity:int)->Optional[CartItem]:
    cart=get_user_cart(db,user_id)
    cart_item=db.query(CartItem).filter(CartItem.id==item_id,CartItem.cart_id==cart.id).first()
    if not cart_item:
        return None
    if quantity<=0:
        db.delete(cart_item)
        db.commit()
        return None
    product=db.query(Product).filter(Product.id==cart_item.product_id).first()
    if product.product_stock<quantity:
        raise HTTPException(status_code=400,detail="Not enough stock")
    cart_item.quantity=quantity
    db.commit()
    db.refresh(cart_item)
    return cart_item

def remove_cart_item(db:Session,user_id:int,item_id:int)->bool:
    cart=get_user_cart(db,user_id)
    cart_item=db.query(CartItem).filter(CartItem.id==item_id,CartItem.cart_id==cart.id).first()
    if not cart_item:
        return False
    db.delete(cart_item)
    db.commit()
    return True

def clear_cart(db:Session,cart_id:int)->None:
    db.query(CartItem).filter(CartItem.cart_id==cart_id).delete()
    db.commit()
