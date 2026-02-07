from django.contrib import admin

from .models import Venue, Hall, Seat, Movie, Showtime, ShowSeat, Booking

admin.site.register(Venue)
admin.site.register(Hall)
admin.site.register(Seat)
admin.site.register(Movie)
admin.site.register(Showtime)
admin.site.register(ShowSeat)
admin.site.register(Booking)
