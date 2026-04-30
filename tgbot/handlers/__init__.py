"""Import all routers and add them to routers_list."""
from .admin import admin_router
from .echo import echo_router
from .onboarding import onboarding_router
from .results import results_router
from .user import user_router
from .food_tracking import food_tracking_router

routers_list = [
    admin_router,
    onboarding_router,
    results_router,
    user_router,
    food_tracking_router,
    echo_router,  # echo_router must be last
]

__all__ = [
    "routers_list",
]
