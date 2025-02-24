from rest_framework import permissions
from django.contrib.auth.models import Group

class IsManager(permissions.BasePermission):
    """Allow only users in the 'Manager' group to modify menu items."""

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.groups.filter(name="Manager").exists()


# class IsCustomerOrDelivery(permissions.BasePermission):
#     """Allow customers and delivery crew to read-only access."""

#     def has_permission(self, request, view):
#         return request.user.is_authenticated and (
#             request.user.groups.filter(name="Customer").exists() or
#             request.user.groups.filter(name="Delivery Crew").exists()
#         )