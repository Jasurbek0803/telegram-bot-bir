from aiogram import Router

from app.handlers.superadmin.create_test_admin_superadmin import router as create_test_router
from app.handlers.superadmin.add_admin import router as add_admin_router
from app.handlers.superadmin.remove_admin import router as remove_admin_router
from app.handlers.superadmin.delete_test_allAdmins import router as delete_test_router
from app.handlers.superadmin.view_test_allAdmin import router as view_tests_router

from app.handlers.superadmin.test_natijalar import router as test_natijalar_router
from app.handlers.superadmin.admin_nazorati import router as admin_nazorati_router
from app.handlers.superadmin.reklama import router as reklama_router
from app.handlers.superadmin.about_users import router as about_users_router

router = Router()

router.include_router(add_admin_router)
router.include_router(admin_nazorati_router)
router.include_router(about_users_router)
router.include_router(reklama_router)
router.include_router(remove_admin_router)
router.include_router(create_test_router)
router.include_router(delete_test_router)
router.include_router(view_tests_router)
router.include_router(test_natijalar_router)



