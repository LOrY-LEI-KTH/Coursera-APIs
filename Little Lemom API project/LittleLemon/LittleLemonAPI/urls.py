from django.urls import path,include
from rest_framework.routers import DefaultRouter

from . import views


router = DefaultRouter()
router.register(r'menu-items', views.MenuItemViewSet, basename='menu-items')


urlpatterns = [
  path('', include(router.urls))
]
