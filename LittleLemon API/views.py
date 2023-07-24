from django.db import IntegrityError, Error
from rest_framework.decorators import api_view, throttle_classes, permission_classes
from .models import Category, MenuItem, Cart, Order, OrderItem
from .serializers import CategorySerializer, MenuItemSerializer, MenuItemSerializers, MenuItemSerializerPost, UserSerializer, CartSerializer, OrderSerializer, OrderItemSerializer
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework import status
from decimal import Decimal
from rest_framework.permissions import IsAuthenticated, IsAdminUser, IsAuthenticatedOrReadOnly, AllowAny
from django.contrib.auth.models import User, Group
from rest_framework.throttling import AnonRateThrottle, UserRateThrottle
from django.core.paginator import Paginator, EmptyPage
# view for customers and delivery team and Managers
@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
@throttle_classes([AnonRateThrottle, UserRateThrottle])
def Menuitems(request):
    # for customers and Delivery_Team
    if (request.method == 'GET'):        
        items = MenuItem.objects.select_related('category').all()


        category_name = request.query_params.get("category")
        to_price = request.query_params.get('to_price')
        featured_filler = request.query_params.get('featured')

        search = request.query_params.get("search")

        if category_name:
            items = items.filter(category__title=category_name)

        if to_price:
            items = items.filter(price__lte=Decimal(to_price))

        if featured_filler and featured_filler.lower() in ['true', 'false']:
            if featured_filler.lower() == 'false':
                featured_filler = False
            elif featured_filler.lower() == 'true':
                featured_filler = True   
            items = items.filter(featured=featured_filler)   

        if search:
            items = items.filter(title__istartswith=search)
            
            # a different serializer can be viewed by the customer and delivery team 
        serializer_item =  MenuItemSerializer(items, many=True)
        return Response(serializer_item.data)
    # handles post request for managers 
    if request.method == 'POST':
        manager = request.user.groups.filter(name='Manager').exists()
        if not manager:
            return Response({'message': 'Access Denied'}, status=status.HTTP_403_FORBIDDEN)
        serialized_item = MenuItemSerializerPost(data = request.data)
        serialized_item.is_valid(raise_exception = True)
        serialized_item.save()
        return Response(serialized_item.data, status=status.HTTP_201_CREATED)

    else:
        
        manager = request.user.groups.filter(name='Manager').exists()
        if not manager:
            return Response({'message': 'Access Denied'}, status=status.HTTP_403_FORBIDDEN)
        items = MenuItem.objects.all()
        serialized_item = MenuItemSerializers(items,data = request.data)
        serialized_item.is_valid(raise_exception=True)
        serialized_item.save()
        return Response(serialized_item.data, status=status.HTTP_201_CREATED)



'''
    This function allows only managers to post put patch and delete menu items
    customers and delivery team can view a single item
    Throttling will be for authenticated user.
'''
@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
@permission_classes([IsAuthenticated])
@throttle_classes([UserRateThrottle])
def Singleitem(request, id):
    if request.method == 'GET':
        '''
        This code block allows all users to fetch a single item by id
        '''
        items = get_object_or_404(MenuItem, pk=id)
        serializer_item = MenuItemSerializer(items)
        return Response(serializer_item.data)

    else:
        '''
            This code block is manager specific.
        '''
        manager = request.user.groups.filter(name='Manager').exists()
        if not manager:
            return Response({'message': 'Access Denied'}, status=status.HTTP_403_FORBIDDEN)

        item = get_object_or_404(MenuItem, pk=id)

        if request.method == 'PUT' or request.method == 'PATCH':
            data_to_save  = MenuItemSerializers(item, data=request.data)
            data_to_save.is_valid(raise_exception=True)
            data_to_save.save()
            return Response(data_to_save.data, status=status.HTTP_206_PARTIAL_CONTENT)

        if request.method == 'DELETE':
            item.delete()
            return Response({'message': 'Item Deleted Succesfully'}, status=status.HTTP_200_OK)

    ''''
    Allows Managers to add(post) and retrieve members into the Manager group
    Getting users by group can also be done on Admin Panel
    '''
@api_view(['GET', 'POST'])
@permission_classes([IsAdminUser])
@throttle_classes([UserRateThrottle])
def ViewGroups(request):
    managers = Group.objects.get(name = 'Manager').user_set.all()
    serialized_manager = UserSerializer(managers, many = True)
    if request.method == 'GET':
        return Response(serialized_manager.data, status.HTTP_200_OK)
    if request.method =='POST':
        username = request.data['username']
        if username:
            user = get_object_or_404(User,username = username)
            managers.user_set.add(user)
            return Response({'message': 'ok'},status.HTTP_201_CREATED)

        return Response({'message': 'error'}, status.HTTP_400_BAD_REQEST)

    '''
    Allows Managers to delete members into a group
    '''
@api_view(['DELETE'])
@permission_classes([IsAdminUser])
@throttle_classes([UserRateThrottle])
def SingleViewGroup(request, userId):
    if request.user.groups.filter(name = 'Manager').exists:
        user = User.objects.get(pk = userId)
        group = Group.objects.get(name = 'Manager')
        user.groups.remove(group)
        return Response(status.HTTP_200_OK)
    else:
        return Response(status.HTTP_404_NOT_FOUND)

'''
    Allows Managers to add(post) and retrieve members into Delivery Team group
    Getting users by group can also be done on Admin Panel
'''

@api_view(['GET', 'POST'])
@permission_classes([IsAdminUser])
@throttle_classes([UserRateThrottle])
def ViewGroupsDelivery(request):
       if request.user.groups.filter(name ='Manager').exists():
        delivery_crew = Group.objects.get(name = 'Delivery_Team').user_set.all()
        if request.method == 'GET':
            serialized_crew = UserSerializer(delivery_crew, many = True)
            return Response(serialized_crew.data, status.HTTP_200_OK)
        if request.method =='POST':
            user = get_object_or_404(User, username = request.data['username'])
            user.groups.add(Group.objects.get(name = 'Delivery_Team'))
    
            return Response(status.HTTP_201_CREATED)

'''
    Allows Managers to delete members into a group
'''

@api_view(['DELETE'])
@permission_classes([IsAdminUser])
@throttle_classes([UserRateThrottle])
def SingleViewGroupsDelivery(request, userId):
    if request.user.groups.filter(name = 'Manager').exists:
        user = User.objects.get(pk = userId)
        group = Group.objects.get(name = 'Delivery_Team')
        user.groups.remove(group)
        return Response(status.HTTP_200_OK)
    else:
        return Response(status.HTTP_404_NOT_FOUND)


'''Allows Customers to add menu item to cart, and get all menu items in a cart. Customers can also delete menu item from cart'''
@api_view(['GET', 'POST', 'DELETE'])
@permission_classes([IsAdminUser])
@throttle_classes([UserRateThrottle])
def ViewCart(request):
    if request.method == 'POST':
        serialized_cart = CartSerializer(data = request.data)
        if serialized_cart.is_valid():
            try:
                serialized_cart.validated_data['user'] = request.user
                serialized_cart.save()
            except IntegrityError as e:
                return Response({'error': str(e)}, status=400)
            return Response(serialized_cart.data, status.HTTP_201_CREATED)
        return Response(serialized_cart.errors, status.HTTP_400_BAD_REQUEST)

    carts = Cart.objects.filter(user_id = request.user.id)
    serialized_cart = CartSerializer(carts, many=True)
    if request.method == 'GET':
        return Response(serialized_cart.data, status.HTTP_200_OK)
    if request.method =='DELETE':
        carts.delete()
        return Response({'message':'successfully deleted'}, status.HTTP_200_OK)

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
@throttle_classes([UserRateThrottle])
def OrderView(request):
    if request.method =='GET':
        if request.user.groups.filter(name ='Manager').exists():
            order_items = OrderItem.objects.select_related('order').all()
            order_date = request.query_params.get('date')
            order_status = request.query_params.get('status')
            ordering = request.query_params.get('ordering')
            perpage = request.query_params.get('perpage', default=2)
            page = request.query_params.get('page', default=1)
            if order_date:
                order_items = order_items.filter(order__date = order_date)

            if order_status:
                order_items = order_items.filter(order__status = order_status)
            
            if ordering:
                order_fields = ordering.split(',')
                order_items = order_items.order_by(order_fields)

            paginator = Paginator(item, per_page=perpage)
            try:
                item = paginator.page(number=page)
            except EmptyPage:
                item = []
            serialized_order = OrderItemSerializer(order_items, many = True)
            return Response(serialized_order.data, status.HTTP_200_OK)
        
        if request.user.groups.filter(name = 'Delivery_Team').exists():
            orders = Order.objects.filter(delivery_crew=request.user)
            order_items = OrderItem.objects.select_related('order').filter(order__in = orders)
            serialized_order = OrderItemSerializer(order_items, many=True)
            return Response(serialized_order.data, status.HTTP_200_OK)
        else:
            orders = Order.objects.filter(user_id=request.user.id)
            order_items = OrderItem.objects.select_related('order').filter(order__in =orders)
            serialized_order = OrderItemSerializer(order_items, many=True)
            return Response(serialized_order.data, status.HTTP_200_OK)
        
    if request.method =='POST':
        cart_item = get_object_or_404(Cart, user_id = request.user.id)
        payload = request.data
        serialized_order = OrderSerializer(data = payload)
        if serialized_order.is_valid():
            try:
                serialized_order.validated_data['user'] = request.user
                serialized_order.validated_data['total'] = cart_item.price
                serialized_order.validated_data['date'] = date.today()
                serialized_order.save()
                serialized_order_item = OrderItemSerializer(data = cart_item.__dict__)
                serialized_order_item.is_valid(raise_exception=True)
                    # try:
                serialized_order_item.validated_data['order'] = serialized_order.create(serialized_order.validated_data)
                serialized_order_item.validated_data['menuitem'] = cart_item.menuitem
                serialized_order_item.validated_data['quantity'] = cart_item.quantity
                serialized_order_item.validated_data['unit_price'] = cart_item.unit_price
                serialized_order_item.validated_data['price'] = cart_item.price
                serialized_order_item.save()
                cart_item.delete()
                        # return Response(serialized_order_item.data, status.HTTP_201_CREATED)
                    # except Error as e:
                        # return Response({'orderItemError':str(e)}, status.HTTP_404_NOT_FOUND)
            except Error as e:
                return Response({'orderError':str(e)}, status.HTTP_404_NOT_FOUND)

        return Response(serialized_order_item.data,status.HTTP_201_CREATED)
    # pass


@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
@throttle_classes([UserRateThrottle])
@permission_classes([IsAuthenticated])
def singleOrderView(request, id):
    order =get_object_or_404(Order,pk = id )
    order_item = get_object_or_404(OrderItem, order = order)
    if request.method == 'GET':
        serialized_item = OrderItemSerializer(order_item)
        return Response(serialized_item.data, status.HTTP_200_OK)
    
    if request.method =='PUT' or request.method == 'PATCH':
        if request.user.groups.filter(name = 'Delivery_Team').exists():
            status_data = request.data['status']
            serialized_order = OrderSerializer(data=status_data)
            serialized_order.is_valid(raise_exception=True)
            serialized_order.save()
            return Response(serialized_order.data, status.HTTP_200_OK)
        else:
            serialized_order = OrderSerializer(data=request.data)
            serialized_order.is_valid(raise_exception=True)
            serialized_order.save()
            return Response(serialized_order.data, status.HTTP_200_OK)
    if request.method =='DELETE':
        if request.user.groups.filter(name = 'Manager').exists():
            order_item.delete()
            return Response({'message':'item deleted'}, status.HTTP_200_OK)