from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User


class Reservation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reservations')
    date_of_reservation = models.DateField(default=timezone.now)
    amount_of_children = models.PositiveIntegerField(default=0)
    amount_of_adults = models.PositiveIntegerField(default=0)
    is_confirmed = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['is_confirmed']

    def __str__(self):
        return f"Reservation #{self.id} by {self.user}"


class StandardToursManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(tour_type='standard')


class Tour(models.Model):
    TOUR_TYPES = [
        ('all inclusive', 'All Inclusive'),
        ('standard', 'Standard'),
        ('exclusive', 'Exclusive'),
    ]

    supervisor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='supervised_tours')
    max_number_of_participants = models.PositiveIntegerField()
    date_start = models.DateField()
    date_end = models.DateField()
    place_id = models.IntegerField()
    tour_type = models.CharField(max_length=20, choices=TOUR_TYPES)
    price = models.DecimalField(max_digits=9, decimal_places=2)
    country = models.CharField(max_length=45)
    region = models.CharField(max_length=45)
    city = models.CharField(max_length=45)
    accommodation = models.CharField(max_length=45)
    is_active = models.BooleanField(default=True)
    objects = models.Manager()
    standard_tours = StandardToursManager()
    profile_pic = models.ImageField(upload_to='profile/', blank=True, null=True)

    class Meta:
        ordering = ['is_active']

    def __str__(self):
        return f"Tour #{self.id} - {self.city}, {self.country}"


class TourReservation(models.Model):
    reservation = models.ForeignKey(Reservation, on_delete=models.CASCADE, related_name='tour_links')
    tour = models.ForeignKey(Tour, on_delete=models.CASCADE, related_name='reservation_links')
    is_price_reduced = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['is_active']

    def __str__(self):
        return f"Reservation #{self.reservation.id} - Tour #{self.tour.id}"
