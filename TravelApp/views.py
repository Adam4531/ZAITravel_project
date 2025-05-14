from rest_framework import generics, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import User, Reservation, Tour, TourReservation
from .serializers import ReservationSerializer, TourSerializer, TourReservationSerializer, RegisterSerializer, \
    UserSerializer
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.pagination import PageNumberPagination
from rest_framework.reverse import reverse
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models import Count
from .permissions import IsReservedOrAdmin
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView




class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10


class LoginAPIView(TokenObtainPairView):
    permission_classes = [AllowAny]
    serializer_class = TokenObtainPairView.serializer_class


class TokenRefreshAPIView(TokenRefreshView):
    permission_classes = [AllowAny]


class UserList(generics.ListCreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    ordering_fields = ['email']
    permission_classes = [IsAdminUser]
    name = 'user-list'


class UserDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAdminUser]
    name = 'user-detail'


class ReservationList(generics.ListCreateAPIView):
    queryset = Reservation.objects.annotate(num_characters=Count('user')).all()
    # queryset = Reservation.objects.all()
    serializer_class = ReservationSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    ordering_fields = ['date_of_reservation']
    filterset_fields = ['user', 'is_confirmed', 'is_active']
    permission_classes = [IsAuthenticated]
    name = 'reservation-list'


class ReservationDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Reservation.objects.all()
    serializer_class = ReservationSerializer
    permission_classes = [IsReservedOrAdmin]
    name = 'reservation-detail'


class TourList(generics.ListCreateAPIView):
    queryset = Tour.objects.all()
    serializer_class = TourSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    ordering_fields = ['price', 'date_start']
    filterset_fields = ['tour_type', 'country', 'is_active']
    name = 'tour-list'

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAdminUser()]
        return [AllowAny()]


class TourDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Tour.objects.all()
    serializer_class = TourSerializer
    name = 'tour-detail'

    def get_permissions(self):
        if self.request.method in ['PUT', 'PATCH', 'DELETE']:
            return [IsAdminUser()]
        return [AllowAny()]


class TourReservationList(generics.ListCreateAPIView):
    queryset = TourReservation.objects.all()
    serializer_class = TourReservationSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    ordering_fields = ['reservation', 'tour']
    filterset_fields = ['is_price_reduced', 'is_active']
    permission_classes = [IsAuthenticated]
    name = 'tourreservation-list'


class TourReservationDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = TourReservation.objects.all()
    serializer_class = TourReservationSerializer
    permission_classes = [IsAuthenticated]
    name = 'tourreservation-detail'


class RegisterAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            refresh = RefreshToken.for_user(user)
            return Response({
                'user': RegisterSerializer(user).data,
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ApiRoot(APIView):
    name = 'api-root'

    def get(self, request, *args, **kwargs):
        return Response({
            'users': reverse(UserList.name, request=request),
            'reservations': reverse(ReservationList.name, request=request),
            'tours': reverse(TourList.name, request=request),
            'tour-reservations': reverse(TourReservationList.name, request=request),
        })