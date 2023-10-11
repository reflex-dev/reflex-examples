from datetime import datetime
import json
from fastapi import APIRouter, Request
from fastapi.exceptions import HTTPException
import reflex as rx
from .model import Product


async def get_product(spec_id: int):
    with rx.session() as session:
        spec = session.query(Product).get(spec_id)
    return spec if spec else HTTPException(status_code=404)


async def list_product(req: Request):
    with rx.session() as session:
        specs = session.query(Product).all()
    return specs


async def add_product(req: Request):
    data = json.loads(await req.body())
    with rx.session() as session:
        now = datetime.now()
        code = data["code"]
        if not code:
            return HTTPException(status_code=402, detail="Invalid `code`")
        session.add(
            Product(
                code=code,
                created=now,
                updated=now,
                label=data["label"],
                image="/favicon.ico",
                quantity=data["quantity"],
                category=data["category"],
                seller=data["seller"],
                sender=data["sender"],
            )
        )
        session.commit()
    return "OK"


async def update_product(spec_id: int, req: Request):
    data = json.loads(await req.body())
    with rx.session() as session:
        spec = session.query(Product).get(spec_id)
        for k, v in data.items():
            spec.__setattr__(k, v)
            spec.__setattr__("updated", datetime.now())
        session.add(spec)
        session.commit()


async def delete_product(spec_id):
    with rx.session() as session:
        spec = session.query(Product).get(spec_id)
        session.delete(spec)
        session.commit()


product_router = APIRouter(prefix="/products", tags=["products"])

product_router.add_api_route("", add_product, methods=["POST"])
product_router.add_api_route("", list_product, methods=["GET"])
product_router.add_api_route("/{spec_id}", get_product, methods=["GET"])
product_router.add_api_route("/{spec_id}", update_product, methods=["PUT"])
product_router.add_api_route("/{spec_id}", delete_product, methods=["DELETE"])
