from django.urls import path
from . import views

urlpatterns = [
    path('menu-items/', views.Menuitems),
    path('menu-items/<int:id>/', views.Singleitem),
    path('group/manager/users', views.ViewGroups),
    path('group/manager/users/<int:userId>', views.SingleViewGroup),
    path('group/delivery/users/', views.ViewGroupsDelivery),
    path('group/delivery/users/<int:userId>', views.SingleViewGroupsDelivery),
    path('cart/menu-items',views.ViewCart),
    path('orders/',views.OrderView),
   path("orders/<int:id>/",views.singleOrderView),
    #path("categories/",views.categoriesView),
    #path("categories/<int:categoryID>/",views.categoryView),
    
]