from django.urls import path

from . import views

urlpatterns = [
    path('', views.ConnectionsListView.as_view(), name='Card Connections'),
    path('temp', views.TempConnectionsListView.as_view(), name='Temp Card Connections'),
    path('temp/new', views.PickSourceCardListView.as_view(), name='Create New Temp Connection'),
    path('temp/new/<slug:pk>/', views.PickDestinationCardListView.as_view(), name='choose_dst_card'),
    path('temp/new/<slug:src_pk>/<slug:dst_pk>/', views.ProposeConnectionFormView.as_view(), name='create_connection'),
    path('temp/vote/<slug:pk>/', views.VoteConnectionView.as_view(), name='Vote on Connection'),
    path('temp/vote/<str:connection_id>/<str:connection_is_correct>/', views.insert_vote_on_connection, name='cast_vote'),
    path('export', views.ExportCardConnectionsToCypherView.as_view(), name='Export Card Connections'),
]
