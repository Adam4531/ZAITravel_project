from django.urls import path
from . import views

urlpatterns = [
    path('', views.ApiRoot.as_view(), name='api-root'),

    path('register/', views.RegisterAPIView.as_view(), name='register'),
    path('login/', views.LoginAPIView.as_view(), name='login'),
    path('token/refresh/', views.TokenRefreshAPIView.as_view(), name='token_refresh'),

    path('api/users/', views.UserList.as_view(), name='user-list'),
    path('api/users/<int:pk>/', views.UserDetail.as_view(), name='user-detail'),

    path('api/reservations/', views.ReservationList.as_view(), name='reservation-list'),
    path('api/reservations/<int:pk>/', views.ReservationDetail.as_view(), name='reservation-detail'),

    path('api/tours/', views.TourList.as_view(), name='tour-list'),
    path('api/tours/<int:pk>/', views.TourDetail.as_view(), name='tour-detail'),

    path('api/tour-reservations/', views.TourReservationList.as_view(), name='tourreservation-list'),
    path('api/tour-reservations/<int:pk>/', views.TourReservationDetail.as_view(), name='tourreservation-detail'),
]