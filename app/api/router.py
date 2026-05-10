from fastapi import APIRouter
from app.api.v1 import auth as auth_v1
from app.api.routes import admin,products,cart,checkout,trending,search

api_router=APIRouter()

api_router.include_router(auth_v1.router,prefix="/auth",tags=["Auth"])
api_router.include_router(admin.router,prefix="/admin",tags=["Admin"])
api_router.include_router(products.router,prefix="/products",tags=["Products"])
api_router.include_router(cart.router,prefix="/cart",tags=["Cart"])
api_router.include_router(checkout.router,prefix="/checkout",tags=["Checkout"])
api_router.include_router(trending.router,prefix="/trending",tags=["Trending"])
api_router.include_router(search.router,prefix="/search",tags=["Search"])
