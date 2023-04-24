from django.urls import path

from . import views

urlpatterns = [
    path('', views.ConnectionsListView.as_view(), name='Card Connections'),
    path('temp', views.TempConnectionsListView.as_view(), name='Temp Card Connections'),
    path('temp/new', views.PickSourceCardListView.as_view(), name='Create New Temp Connection'),
    path('temp/new/<slug:pk>/', views.PickDestinationCardListView.as_view(), name='choose_dst_card'),
    path('temp/new/<slug:src_pk>/<slug:dst_pk>/')
]
