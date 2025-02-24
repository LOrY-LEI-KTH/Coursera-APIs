from django.urls import path,include
from rest_framework.routers import DefaultRouter


from .views import (MenuItemViewSet,
    manager_users, manager_user_delete,
    delivery_crew_users, delivery_crew_user_delete,
    cart_menu_items, CategoryListView
)



router = DefaultRouter()
router.register(r'menu-items', MenuItemViewSet, basename='menu-items')


urlpatterns = [
    # categories
     path('categories/', CategoryListView.as_view(), name='category-list'),

    # menuitems
    path('', include(router.urls)),

    # Manager group endpoints
    path('groups/manager/users', manager_users, name="manager-users"),
    path('groups/manager/users/<int:userId>', manager_user_delete, name="manager-user-delete"),

    # Delivery Crew group endpoints
    path('groups/delivery-crew/users', delivery_crew_users, name="delivery-crew-users"),
    path('groups/delivery-crew/users/<int:userId>', delivery_crew_user_delete, name="delivery-crew-user-delete"),

    # Cart
    path('cart/menu-items', cart_menu_items, name="cart-menu-items"),
]
