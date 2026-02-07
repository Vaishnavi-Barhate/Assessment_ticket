from django.conf import settings
from django.db import models


class Venue(models.Model):
    name = models.CharField(max_length=200)
    city = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.name} ({self.city})"


class Hall(models.Model):
    venue = models.ForeignKey(Venue, on_delete=models.CASCADE, related_name='halls')
    name = models.CharField(max_length=200)

    def __str__(self):
        return f"{self.venue.name} - {self.name}"


class Seat(models.Model):
    hall = models.ForeignKey(Hall, on_delete=models.CASCADE, related_name='seats')
    row = models.CharField(max_length=5)
    number = models.PositiveIntegerField()

    class Meta:
        unique_together = ('hall', 'row', 'number')
        indexes = [
            models.Index(fields=['hall', 'row', 'number']),
        ]

    def __str__(self):
        return f"{self.hall.name} {self.row}{self.number}"


class Movie(models.Model):
    title = models.CharField(max_length=200)
    duration_minutes = models.PositiveIntegerField()

    def __str__(self):
        return self.title


class Showtime(models.Model):
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name='showtimes')
    hall = models.ForeignKey(Hall, on_delete=models.CASCADE, related_name='showtimes')
    starts_at = models.DateTimeField()
    ends_at = models.DateTimeField()

    class Meta:
        indexes = [
            models.Index(fields=['hall', 'starts_at']),
        ]

    def __str__(self):
        return f"{self.movie.title} @ {self.starts_at.isoformat()}"


class ShowSeat(models.Model):
    STATUS_AVAILABLE = 'available'
    STATUS_HELD = 'held'
    STATUS_BOOKED = 'booked'

    STATUS_CHOICES = [
        (STATUS_AVAILABLE, 'Available'),
        (STATUS_HELD, 'Held'),
        (STATUS_BOOKED, 'Booked'),
    ]

    showtime = models.ForeignKey(Showtime, on_delete=models.CASCADE, related_name='show_seats')
    seat = models.ForeignKey(Seat, on_delete=models.CASCADE, related_name='show_seats')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_AVAILABLE)
    locked_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='held_seats',
    )
    locked_until = models.DateTimeField(null=True, blank=True)
    booked_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ('showtime', 'seat')
        indexes = [
            models.Index(fields=['showtime', 'status']),
        ]

    def __str__(self):
        return f"{self.showtime} - {self.seat}"


class Booking(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='bookings')
    showtime = models.ForeignKey(Showtime, on_delete=models.PROTECT, related_name='bookings')
    seat = models.ForeignKey(Seat, on_delete=models.PROTECT, related_name='bookings')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('showtime', 'seat')
        indexes = [
            models.Index(fields=['showtime', 'created_at']),
        ]

    def __str__(self):
        return f"Booking {self.showtime} - {self.seat}"
