from django.contrib.auth.models import User, Group
from django.db import IntegrityError
from rest_framework import viewsets
from rest_framework.generics import ListAPIView
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework import status

from .models import MenuItem, Cart, Category
from .serializers import MenuItemSerializer, UserGroupSerializer,CartSerializer, CategorySerializer
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
    


# ----- Manager Group Endpoints ----- #

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated, IsManager])
def manager_users(request):
    """
    GET: Returns all users in the Manager group.
    POST: Assigns the user (provided via 'user_id' in payload) to the Manager group.
    """
    manager_group = Group.objects.get(name="Manager")
    
    if request.method == 'GET':
        managers = manager_group.user_set.all()
        serializer = UserGroupSerializer(managers, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    elif request.method == 'POST':
        user_id = request.data.get("user_id")
        try:
            user = User.objects.get(id=user_id)
            user.groups.add(manager_group)
            return Response({"message": "User added to Manager group"}, status=status.HTTP_201_CREATED)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated, IsManager])
def manager_user_delete(request, userId):
    """
    DELETE: Removes the user with the provided userId from the Manager group.
    """
    manager_group = Group.objects.get(name="Manager")
    try:
        user = User.objects.get(id=userId)
        user.groups.remove(manager_group)
        return Response({"message": "User removed from Manager group"}, status=status.HTTP_200_OK)
    except User.DoesNotExist:
        return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)


# ----- Delivery Crew Group Endpoints ----- #

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated, IsManager])
def delivery_crew_users(request):
    """
    GET: Returns all users in the Delivery Crew group.
    POST: Assigns the user (provided via 'user_id' in payload) to the Delivery Crew group.
    """
    delivery_group = Group.objects.get(name="Delivery crew")
    
    if request.method == 'GET':
        crew_members = delivery_group.user_set.all()
        serializer = UserGroupSerializer(crew_members, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    elif request.method == 'POST':
        user_id = request.data.get("user_id")
        try:
            user = User.objects.get(id=user_id)
            user.groups.add(delivery_group)
            return Response({"message": "User added to Delivery Crew group"}, status=status.HTTP_201_CREATED)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated, IsManager])
def delivery_crew_user_delete(request, userId):
    """
    DELETE: Removes the user with the provided userId from the Delivery Crew group.
    """
    delivery_group = Group.objects.get(name="Delivery crew")
    try:
        user = User.objects.get(id=userId)
        user.groups.remove(delivery_group)
        return Response({"message": "User removed from Delivery Crew group"}, status=status.HTTP_200_OK)
    except User.DoesNotExist:
        return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET', 'POST', 'DELETE'])
@permission_classes([IsAuthenticated])
def cart_menu_items(request):
    user = request.user

    if request.method == 'GET':
        # Return all cart items for the current user.
        cart_items = Cart.objects.filter(user=user)
        serializer = CartSerializer(cart_items, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    elif request.method == 'POST':
        # Add item to cart (unit_price & price auto-calculated in serializer)
        serializer = CartSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        # Remove all cart items for the current user
        Cart.objects.filter(user=user).delete()
        return Response({"message": "Cart cleared."}, status=status.HTTP_200_OK)

    

class CategoryListView(ListAPIView):
    queryset = Category.objects.all()  # Query all categories
    serializer_class = CategorySerializer  # Use the CategorySerializer to format the response
    permission_classes = [IsAuthenticatedOrReadOnly]  # Allows viewing by anyone, but modification is restricted