import graphene
from graphene_django.types import DjangoObjectType
from django.contrib.auth.models import User
from .models import Reservation, Tour, TourReservation
from django.utils import timezone
from decimal import Decimal

class UserType(DjangoObjectType):
    class Meta:
        model = User
        fields = "__all__"


class ReservationType(DjangoObjectType):
    class Meta:
        model = Reservation
        fields = "__all__"


class TourType(DjangoObjectType):
    class Meta:
        model = Tour
        fields = "__all__"


class TourReservationType(DjangoObjectType):
    class Meta:
        model = TourReservation
        fields = "__all__"

class Query(graphene.ObjectType):
    all_reservations = graphene.List(ReservationType)
    reservation = graphene.Field(ReservationType, id=graphene.Int())

    all_tours = graphene.List(TourType)
    tour = graphene.Field(TourType, id=graphene.Int())

    all_tour_reservations = graphene.List(TourReservationType)
    tour_reservation = graphene.Field(TourReservationType, id=graphene.Int())

    def resolve_all_reservations(self, info):
        return Reservation.objects.all()

    def resolve_reservation(self, info, id):
        return Reservation.objects.filter(id=id).first()

    def resolve_all_tours(self, info):
        return Tour.objects.all()

    def resolve_tour(self, info, id):
        return Tour.objects.filter(id=id).first()

    def resolve_all_tour_reservations(self, info):
        return TourReservation.objects.all()

    def resolve_tour_reservation(self, info, id):
        return TourReservation.objects.filter(id=id).first()


class CreateReservation(graphene.Mutation):
    class Arguments:
        user_id = graphene.Int(required=True)
        date_of_reservation = graphene.Date()
        amount_of_children = graphene.Int()
        amount_of_adults = graphene.Int()
        is_confirmed = graphene.Boolean()
        is_active = graphene.Boolean()

    reservation = graphene.Field(ReservationType)

    def mutate(self, info, user_id, date_of_reservation=None,
               amount_of_children=0, amount_of_adults=0,
               is_confirmed=True, is_active=True):
        user = User.objects.get(id=user_id)
        reservation = Reservation.objects.create(
            user=user,
            date_of_reservation=date_of_reservation or timezone.now().date(),
            amount_of_children=amount_of_children,
            amount_of_adults=amount_of_adults,
            is_confirmed=is_confirmed,
            is_active=is_active
        )
        return CreateReservation(reservation=reservation)


class UpdateReservation(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)
        amount_of_children = graphene.Int()
        amount_of_adults = graphene.Int()
        is_confirmed = graphene.Boolean()
        is_active = graphene.Boolean()

    reservation = graphene.Field(ReservationType)

    def mutate(self, info, id, **kwargs):
        reservation = Reservation.objects.get(id=id)
        for field, value in kwargs.items():
            setattr(reservation, field, value)
        reservation.save()
        return UpdateReservation(reservation=reservation)


class DeleteReservation(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)

    success = graphene.Boolean()

    def mutate(self, info, id):
        reservation = Reservation.objects.filter(id=id).first()
        if not reservation:
            return DeleteReservation(success=False)
        reservation.delete()
        return DeleteReservation(success=True)


class CreateTour(graphene.Mutation):
    class Arguments:
        supervisor_id = graphene.Int(required=True)
        max_number_of_participants = graphene.Int(required=True)
        date_start = graphene.Date(required=True)
        date_end = graphene.Date(required=True)
        place_id = graphene.Int(required=True)
        tour_type = graphene.String(required=True)
        price = graphene.Float(required=True)
        country = graphene.String(required=True)
        region = graphene.String(required=True)
        city = graphene.String(required=True)
        accommodation = graphene.String(required=True)
        is_active = graphene.Boolean()

    tour = graphene.Field(TourType)

    def mutate(self, info, supervisor_id, **kwargs):
        supervisor = User.objects.get(id=supervisor_id)
        tour = Tour.objects.create(supervisor=supervisor, **kwargs)
        return CreateTour(tour=tour)


class UpdateTour(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)
        max_number_of_participants = graphene.Int()
        tour_type = graphene.String()
        price = graphene.String()
        is_active = graphene.Boolean()

    tour = graphene.Field(TourType)

    def mutate(self, info, id, **kwargs):
        tour = Tour.objects.get(id=id)

        if 'price' in kwargs:
            kwargs['price'] = Decimal(kwargs['price'])

        for field, value in kwargs.items():
            setattr(tour, field, value)
        tour.save()
        return UpdateTour(tour=tour)

class DeleteTour(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)

    success = graphene.Boolean()

    def mutate(self, info, id):
        tour = Tour.objects.filter(id=id).first()
        if not tour:
            return DeleteTour(success=False)
        tour.delete()
        return DeleteTour(success=True)


class CreateTourReservation(graphene.Mutation):
    class Arguments:
        reservation_id = graphene.Int(required=True)
        tour_id = graphene.Int(required=True)
        is_price_reduced = graphene.Boolean()

    tour_reservation = graphene.Field(TourReservationType)

    def mutate(self, info, reservation_id, tour_id, is_price_reduced=False):
        reservation = Reservation.objects.get(id=reservation_id)
        tour = Tour.objects.get(id=tour_id)
        tr = TourReservation.objects.create(
            reservation=reservation,
            tour=tour,
            is_price_reduced=is_price_reduced
        )
        return CreateTourReservation(tour_reservation=tr)


class DeleteTourReservation(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)

    success = graphene.Boolean()

    def mutate(self, info, id):
        tr = TourReservation.objects.filter(id=id).first()
        if not tr:
            return DeleteTourReservation(success=False)
        tr.delete()
        return DeleteTourReservation(success=True)


class Mutation(graphene.ObjectType):
    create_reservation = CreateReservation.Field()
    update_reservation = UpdateReservation.Field()
    delete_reservation = DeleteReservation.Field()

    create_tour = CreateTour.Field()
    update_tour = UpdateTour.Field()
    delete_tour = DeleteTour.Field()

    create_tour_reservation = CreateTourReservation.Field()
    delete_tour_reservation = DeleteTourReservation.Field()


schema = graphene.Schema(query=Query, mutation=Mutation)
