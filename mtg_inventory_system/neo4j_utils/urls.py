from django.urls import path

from . import views

urlpatterns = [
    path('', views.ConnectionsListView.as_view(), name='Card Connections'),
    path('temp', views.TempConnectionsListView.as_view(), name='Temp Card Connections'),
    path('temp/new', views.propose_connection_view, name='Create New Temp Connection'),
]
