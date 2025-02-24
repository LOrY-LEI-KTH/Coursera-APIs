from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import MenuItem
from .serializers import MenuItemSerializer
from .permissions import IsManager

# Create your views here.


class MenuItemViewSet(viewsets.ModelViewSet):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer

    def get_permissions(self):
        """Assign permissions based on user groups."""
        if self.request.method in ['POST', 'PUT', 'PATCH', 'DELETE']:
            return [IsAuthenticated(), IsManager()]  # Only managers can modify

        # Customers and Delivery Crew can view (GET), Managers can also view (GET) if needed
        if self.request.method == 'GET':
            return [IsAuthenticated()]  # All authenticated users can view (GET)

        return []  # Default to no permissions (not really needed)