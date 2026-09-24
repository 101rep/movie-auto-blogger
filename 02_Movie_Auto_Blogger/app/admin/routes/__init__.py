from fastapi import APIRouter

from app.admin.routes.auth_settings import router as auth_router
from app.admin.routes.dashboard import router as dashboard_router
from app.admin.routes.posts import router as posts_router
from app.admin.routes.sites import router as sites_router
from app.admin.routes.experience import router as experience_router
from app.admin.routes.api import router as api_router
from app.admin.routes.enterprise import router as enterprise_router

from fastapi.responses import RedirectResponse

# Master Admin Router with backward-compatible prefix
router = APIRouter(prefix="/admin", tags=["admin"])

@router.get("", include_in_schema=False)
async def admin_root_redirect():
    """Redirect /admin to /admin/ seamlessly."""
    return RedirectResponse(url="/admin/", status_code=302)

router.include_router(dashboard_router)
router.include_router(auth_router)
router.include_router(posts_router)
router.include_router(sites_router)
router.include_router(experience_router)
router.include_router(api_router)
router.include_router(enterprise_router)

