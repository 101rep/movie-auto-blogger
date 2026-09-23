from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from database.connection import get_db
from services.product_service import ProductService
from domain_types.schemas import ProductSaveRequest, ProductDTO
from utils.cache import app_cache

router = APIRouter(prefix="/api/products", tags=["Products"])

@router.get("/search")
def search_external_products(
    query: Optional[str] = None,
    category: Optional[str] = None,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=50),
    db: Session = Depends(get_db)
):
    service = ProductService(db)
    return service.search_external_products(query=query, category=category, page=page, limit=limit)

@router.post("/save")
def save_product(req: ProductSaveRequest, db: Session = Depends(get_db)):
    service = ProductService(db)
    prod = service.save_product(req.model_dump())
    app_cache.clear_prefix("products_list:")
    return {
        "status": "SUCCESS",
        "message": "상품이 성공적으로 저장되었습니다.",
        "product_id": prod.id,
        "external_id": prod.external_id
    }

@router.get("")
def list_saved_products(
    query: Optional[str] = None,
    category: Optional[str] = None,
    min_price: Optional[int] = None,
    max_price: Optional[int] = None,
    min_rating: Optional[float] = None,
    sort_by: str = "recent",
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    cache_key = f"products_list:{query}:{category}:{min_price}:{max_price}:{min_rating}:{sort_by}:{skip}:{limit}"
    cached = app_cache.get(cache_key)
    if cached is not None:
        return cached

    service = ProductService(db)
    prods = service.list_products(
        query=query,
        category=category,
        min_price=min_price,
        max_price=max_price,
        min_rating=min_rating,
        sort_by=sort_by,
        skip=skip,
        limit=limit
    )
    res = [
        {
            "id": p.id,
            "external_id": p.external_id,
            "name": p.name,
            "category": p.category,
            "price": p.price,
            "original_price": p.original_price,
            "rating": p.rating,
            "review_count": p.review_count,
            "shipping_type": p.shipping_type,
            "url": p.url,
            "image_url": p.image_url,
            "source": p.source,
            "created_at": p.created_at.isoformat() if p.created_at else None
        }
        for p in prods
    ]
    app_cache.set(cache_key, res, ttl=60)
    return res

@router.get("/{product_id}")
def get_product_detail(product_id: int, db: Session = Depends(get_db)):
    service = ProductService(db)
    prod = service.get_product(product_id)
    if not prod:
        raise HTTPException(status_code=404, detail="상품을 찾을 수 없습니다.")
    return prod

@router.delete("/{product_id}")
def delete_product(product_id: int, db: Session = Depends(get_db)):
    service = ProductService(db)
    success = service.delete_product(product_id)
    if not success:
        raise HTTPException(status_code=404, detail="상품을 찾을 수 없습니다.")
    app_cache.clear_prefix("products_list:")
    return {"status": "SUCCESS", "message": "상품이 삭제되었습니다."}