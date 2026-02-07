from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from booking.models import Venue, Hall, Seat, Movie, Showtime, ShowSeat


class Command(BaseCommand):
    help = 'Seed demo data for the ticketing engine.'

    def handle(self, *args, **options):
        venue, _ = Venue.objects.get_or_create(name='Metro Cineplex', city='Metro City')
        hall, _ = Hall.objects.get_or_create(venue=venue, name='Hall 1')

        seats = []
        for row in ['A', 'B', 'C', 'D']:
            for number in range(1, 11):
                seat, _ = Seat.objects.get_or_create(hall=hall, row=row, number=number)
                seats.append(seat)

        movie, _ = Movie.objects.get_or_create(title='Release Night', duration_minutes=120)
        start = timezone.now() + timedelta(days=1)
        end = start + timedelta(minutes=movie.duration_minutes)
        showtime, _ = Showtime.objects.get_or_create(movie=movie, hall=hall, starts_at=start, ends_at=end)

        for seat in seats:
            ShowSeat.objects.get_or_create(showtime=showtime, seat=seat)

        self.stdout.write(self.style.SUCCESS('Seed data created.'))
