import datetime
from django.contrib.auth.models import User, Group
from django.shortcuts import get_object_or_404

from rest_framework import viewsets
from rest_framework.generics import ListAPIView
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework import status

from .models import MenuItem, Cart, Category, Order, OrderItem
from .serializers import MenuItemSerializer, UserGroupSerializer,CartSerializer, CategorySerializer, OrderSerializer
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




@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def orders_list(request):
    """
    GET /api/orders/:
      - For Managers: return all orders.
      - For Delivery Crew: return orders where delivery_crew == request.user.
      - For Customers: return orders where order.user == request.user.
    
    POST /api/orders/ (only allowed for Customers):
      - Creates a new order for the current customer from their cart items.
    """
    user = request.user
    
    # -----------------------
    # GET: List orders based on role
    # -----------------------
    if request.method == 'GET':
        if user.groups.filter(name="Manager").exists():
            orders = Order.objects.all()
        elif user.groups.filter(name="Delivery crew").exists():
            orders = Order.objects.filter(delivery_crew=user)
        else:
            orders = Order.objects.filter(user=user)
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    # -----------------------
    # POST: Create a new order (for Customers only)
    # -----------------------
    elif request.method == 'POST':
        # Only customers can create orders
        if user.groups.filter(name="Manager").exists() or user.groups.filter(name="Delivery crew").exists():
            return Response({"error": "Only customers can create orders."}, status=status.HTTP_403_FORBIDDEN)
        
        # Create order from current cart items.
        cart_items = Cart.objects.filter(user=user)
        if not cart_items.exists():
            return Response({"error": "Cart is empty."}, status=status.HTTP_400_BAD_REQUEST)
        
        # Create a new order for the customer; set date to today and total initially 0.
        order = Order.objects.create(
            user=user,
            total=0,
            date=datetime.date.today()
        )
        total = 0
        for item in cart_items:
            # Create an OrderItem for each cart item
            OrderItem.objects.create(
                order=order,
                menuitem=item.menuitem,
                quantity=item.quantity,
                unit_price=item.unit_price,
                price=item.price
            )
            total += item.price
        order.total = total
        order.save()
        # Clear the cart
        cart_items.delete()
        serializer = OrderSerializer(order)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
@permission_classes([IsAuthenticated])
def order_detail(request, order_id):
    """
    /api/orders/{order_id}/ endpoint:
    
    GET:
      - For Customers: allowed only if order.user == request.user.
      - For Managers and Delivery Crew: allowed for any order.
      
    PUT/PATCH:
      - For Managers: update any order fields (e.g., assign delivery crew, update status).
      - For Delivery Crew: allowed only to update the 'status' field.
      - Customers: not allowed to update orders.
      
    DELETE:
      - Only Managers can delete orders.
    """
    order = get_object_or_404(Order, id=order_id)
    user = request.user

    # -----------------------
    # GET: Retrieve order details.
    # -----------------------
    if request.method == 'GET':
        # Customers can only view their own orders.
        if not (user.groups.filter(name="Manager").exists() or user.groups.filter(name="Delivery crew").exists()):
            if order.user != user:
                return Response({"error": "Not authorized to view this order."}, status=status.HTTP_403_FORBIDDEN)
        serializer = OrderSerializer(order)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    # -----------------------
    # PUT/PATCH: Update an order.
    # -----------------------
    elif request.method in ['PUT', 'PATCH']:
        # Manager: can update any field.
        if user.groups.filter(name="Manager").exists():
            serializer = OrderSerializer(order, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        # Delivery Crew: can only update the 'status' field.
        elif user.groups.filter(name="Delivery crew").exists():
            if set(request.data.keys()) != {'status'}:
                return Response({"error": "Delivery crew can only update the 'status' field."}, status=status.HTTP_400_BAD_REQUEST)
            serializer = OrderSerializer(order, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"error": "Not authorized to update this order."}, status=status.HTTP_403_FORBIDDEN)
    
    # -----------------------
    # DELETE: Delete an order.
    # -----------------------
    elif request.method == 'DELETE':
        if user.groups.filter(name="Manager").exists():
            order.delete()
            return Response({"message": "Order deleted."}, status=status.HTTP_200_OK)
        else:
            return Response({"error": "Not authorized to delete this order."}, status=status.HTTP_403_FORBIDDEN)