from django.test import TestCase
from django.contrib.auth.models import User
from .models import Reservation, Tour, TourReservation
from datetime import date, timedelta


# Aby odpalić testy "python manage.py test"
class ReservationModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='john', password='pass1234')
        self.reservation = Reservation.objects.create(
            user=self.user,
            amount_of_children=2,
            amount_of_adults=2,
            is_confirmed=True,
            is_active=True
        )

    def test_reservation_creation(self):
        self.assertEqual(self.reservation.amount_of_children, 2)
        self.assertEqual(self.reservation.amount_of_adults, 2)
        self.assertTrue(self.reservation.is_confirmed)
        self.assertEqual(str(self.reservation), f"Reservation #{self.reservation.id} by {self.user}")


class TourModelTest(TestCase):
    def setUp(self):
        self.supervisor = User.objects.create_user(username='supervisor', password='superpass')
        self.tour = Tour.objects.create(
            supervisor=self.supervisor,
            max_number_of_participants=20,
            date_start=date.today(),
            date_end=date.today() + timedelta(days=7),
            place_id=1,
            tour_type='standard',
            price=999.99,
            country='Italy',
            region='Tuscany',
            city='Florence',
            accommodation='Hotel Florence',
            is_active=True
        )

    def test_tour_creation(self):
        self.assertEqual(self.tour.city, 'Florence')
        self.assertEqual(self.tour.price, 999.99)
        self.assertEqual(self.tour.tour_type, 'standard')
        self.assertEqual(str(self.tour), f"Tour #{self.tour.id} - Florence, Italy")

    def test_standard_tour_manager(self):
        standard_tours = Tour.standard_tours.all()
        self.assertIn(self.tour, standard_tours)


class TourReservationModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='client', password='clientpass')
        self.reservation = Reservation.objects.create(user=self.user)
        self.supervisor = User.objects.create_user(username='guide', password='guidepass')
        self.tour = Tour.objects.create(
            supervisor=self.supervisor,
            max_number_of_participants=10,
            date_start=date.today(),
            date_end=date.today() + timedelta(days=3),
            place_id=2,
            tour_type='exclusive',
            price=1500.00,
            country='France',
            region='Provence',
            city='Nice',
            accommodation='Luxury Inn',
            is_active=True
        )
        self.tour_reservation = TourReservation.objects.create(
            reservation=self.reservation,
            tour=self.tour,
            is_price_reduced=False
        )

    def test_tour_reservation_creation(self):
        self.assertFalse(self.tour_reservation.is_price_reduced)
        self.assertTrue(self.tour_reservation.is_active)
        self.assertEqual(
            str(self.tour_reservation),
            f"Reservation #{self.reservation.id} - Tour #{self.tour.id}"
        )


# GRAPHQL TEST
from graphene.test import Client
from .schema import schema


class GraphQLTestCase(TestCase):
    def setUp(self):
        self.client = Client(schema)
        self.user = User.objects.create(username="testuser")

        self.reservation = Reservation.objects.create(
            user=self.user,
            date_of_reservation=date.today(),
            amount_of_children=1,
            amount_of_adults=2,
            is_confirmed=True,
            is_active=True
        )

        self.tour = Tour.objects.create(
            supervisor=self.user,
            max_number_of_participants=10,
            date_start=date.today(),
            date_end=date.today(),
            place_id=1,
            tour_type="standard",
            price=199.99,
            country="Poland",
            region="Tatra",
            city="Zakopane",
            accommodation="Hotel",
            is_active=True
        )

        self.tour_reservation = TourReservation.objects.create(
            reservation=self.reservation,
            tour=self.tour,
            is_price_reduced=False
        )

    def test_get_all_reservations(self):
        query = """
        query {
            allReservations {
                amountOfAdults
                amountOfChildren
                isConfirmed
                isActive
            }
        }
        """
        response = self.client.execute(query)
        self.assertEqual(response["data"]["allReservations"][0]["amountOfAdults"], 2)

    def test_get_single_reservation(self):
        query = f"""
        query {{
            reservation(id: {self.reservation.id}) {{
                amountOfAdults
                amountOfChildren
            }}
        }}
        """
        response = self.client.execute(query)
        self.assertEqual(response["data"]["reservation"]["amountOfAdults"], 2)

    def test_create_reservation(self):
        mutation = f"""
        mutation {{
            createReservation(userId: {self.user.id}, amountOfChildren: 2, amountOfAdults: 3) {{
                reservation {{
                    amountOfChildren
                    amountOfAdults
                }}
            }}
        }}
        """
        response = self.client.execute(mutation)
        self.assertEqual(response["data"]["createReservation"]["reservation"]["amountOfAdults"], 3)

    def test_update_reservation(self):
        mutation = f"""
        mutation {{
            updateReservation(id: {self.reservation.id}, amountOfAdults: 4) {{
                reservation {{
                    amountOfAdults
                }}
            }}
        }}
        """
        response = self.client.execute(mutation)
        self.assertEqual(response["data"]["updateReservation"]["reservation"]["amountOfAdults"], 4)

    def test_delete_reservation(self):
        mutation = f"""
        mutation {{
            deleteReservation(id: {self.reservation.id}) {{
                success
            }}
        }}
        """
        response = self.client.execute(mutation)
        self.assertTrue(response["data"]["deleteReservation"]["success"])
        self.assertEqual(Reservation.objects.count(), 0)

    def test_get_all_tours(self):
        query = """
        query {
            allTours {
                tourType
                price
                city
            }
        }
        """
        response = self.client.execute(query)
        self.assertEqual(response["data"]["allTours"][0]["city"], "Zakopane")

    def test_get_single_tour(self):
        query = f"""
        query {{
            tour(id: {self.tour.id}) {{
                city
                country
                price
            }}
        }}
        """
        response = self.client.execute(query)
        self.assertEqual(response["data"]["tour"]["country"], "Poland")

    def test_create_tour(self):
        mutation = f"""
        mutation {{
            createTour(
                supervisorId: {self.user.id},
                maxNumberOfParticipants: 5,
                dateStart: "2025-06-01",
                dateEnd: "2025-06-07",
                placeId: 2,
                tourType: "standard",
                price: 299.99,
                country: "Germany",
                region: "Bavaria",
                city: "Munich",
                accommodation: "Hostel"
            ) {{
                tour {{
                    city
                    tourType
                }}
            }}
        }}
        """
        response = self.client.execute(mutation)
        self.assertEqual(response["data"]["createTour"]["tour"]["city"], "Munich")

    def test_update_tour(self):
        mutation = f"""
        mutation {{
            updateTour(id: {self.tour.id}, price: "250.99") {{
                tour {{
                    price
                }}
            }}
        }}
        """
        response = self.client.execute(mutation)
        self.assertEqual(response["data"]["updateTour"]["tour"]["price"], "250.99")

    def test_delete_tour(self):
        mutation = f"""
        mutation {{
            deleteTour(id: {self.tour.id}) {{
                success
            }}
        }}
        """
        response = self.client.execute(mutation)
        self.assertTrue(response["data"]["deleteTour"]["success"])
        self.assertEqual(Tour.objects.count(), 0)

    def test_get_all_tour_reservations(self):
        query = """
        query {
            allTourReservations {
                isPriceReduced
            }
        }
        """
        response = self.client.execute(query)
        self.assertFalse(response["data"]["allTourReservations"][0]["isPriceReduced"])

    def test_get_single_tour_reservation(self):
        query = f"""
        query {{
            tourReservation(id: {self.tour_reservation.id}) {{
                isPriceReduced
            }}
        }}
        """
        response = self.client.execute(query)
        self.assertFalse(response["data"]["tourReservation"]["isPriceReduced"])

    def test_create_tour_reservation(self):
        mutation = f"""
        mutation {{
            createTourReservation(
                reservationId: {self.reservation.id},
                tourId: {self.tour.id},
                isPriceReduced: true
            ) {{
                tourReservation {{
                    isPriceReduced
                }}
            }}
        }}
        """
        response = self.client.execute(mutation)
        self.assertTrue(response["data"]["createTourReservation"]["tourReservation"]["isPriceReduced"])

    def test_delete_tour_reservation(self):
        mutation = f"""
        mutation {{
            deleteTourReservation(id: {self.tour_reservation.id}) {{
                success
            }}
        }}
        """
        response = self.client.execute(mutation)
        self.assertTrue(response["data"]["deleteTourReservation"]["success"])
        self.assertEqual(TourReservation.objects.count(), 0)
