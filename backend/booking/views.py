from datetime import timedelta

from django.contrib.auth import get_user_model
from django.db import IntegrityError, transaction
from django.db.models import F
from django.utils import timezone
from rest_framework import status
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import ShowSeat, Showtime, Booking
from .serializers import HallLayoutSerializer, BookSeatSerializer, HoldSeatSerializer

User = get_user_model()
HOLD_DURATION = timedelta(minutes=5)


def _release_expired_holds(show_id):
    now = timezone.now()
    ShowSeat.objects.filter(
        showtime_id=show_id,
        status=ShowSeat.STATUS_HELD,
        locked_until__lt=now,
    ).update(status=ShowSeat.STATUS_AVAILABLE, locked_by=None, locked_until=None)


@api_view(['GET'])
def hall_layout(request, show_id):
    _release_expired_holds(show_id)
    show = get_object_or_404(Showtime.objects.select_related('hall__venue', 'movie'), id=show_id)
    seats = (
        ShowSeat.objects
        .filter(showtime_id=show_id)
        .select_related('seat')
        .values(
            'seat_id',
            'seat__row',
            'seat__number',
            'status',
            'locked_by_id',
            'locked_until',
        )
        .order_by('seat__row', 'seat__number')
    )

    seat_list = []
    for seat in seats:
        seat_list.append({
            'id': seat['seat_id'],
            'row': seat['seat__row'],
            'number': seat['seat__number'],
            'status': seat['status'],
            'locked_by': seat['locked_by_id'],
            'locked_until': seat['locked_until'],
        })

    payload = {
        'show_id': show.id,
        'hall_name': show.hall.name,
        'venue_name': show.hall.venue.name,
        'movie_title': show.movie.title,
        'starts_at': show.starts_at,
        'seats': seat_list,
    }
    serializer = HallLayoutSerializer(payload)
    return Response(serializer.data)


@api_view(['POST'])
def hold_seat(request):
    serializer = HoldSeatSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    data = serializer.validated_data
    now = timezone.now()

    _release_expired_holds(data['show_id'])

    try:
        with transaction.atomic():
            show_seat = get_object_or_404(
                ShowSeat.objects.select_for_update().select_related('seat'),
                showtime_id=data['show_id'],
                seat_id=data['seat_id'],
            )

            if show_seat.status == ShowSeat.STATUS_BOOKED:
                return Response({'detail': 'Seat already booked.'}, status=status.HTTP_409_CONFLICT)

            if show_seat.status == ShowSeat.STATUS_HELD and show_seat.locked_until and show_seat.locked_until > now:
                if show_seat.locked_by_id != data['user_id']:
                    return Response({'detail': 'Seat currently held by another user.'}, status=status.HTTP_409_CONFLICT)

            show_seat.status = ShowSeat.STATUS_HELD
            show_seat.locked_by_id = data['user_id']
            show_seat.locked_until = now + HOLD_DURATION
            show_seat.save(update_fields=['status', 'locked_by', 'locked_until'])
    except IntegrityError:
        return Response({'detail': 'Seat currently unavailable.'}, status=status.HTTP_409_CONFLICT)

    return Response({'detail': 'Seat held.'}, status=status.HTTP_200_OK)


@api_view(['POST'])
def book_seat(request):
    serializer = BookSeatSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    data = serializer.validated_data
    now = timezone.now()

    _release_expired_holds(data['show_id'])

    try:
        with transaction.atomic():
            show_seat = get_object_or_404(
                ShowSeat.objects.select_for_update().select_related('seat'),
                showtime_id=data['show_id'],
                seat_id=data['seat_id'],
            )

            if show_seat.status == ShowSeat.STATUS_BOOKED:
                return Response({'detail': 'Seat already booked.'}, status=status.HTTP_409_CONFLICT)

            if show_seat.status == ShowSeat.STATUS_HELD:
                if show_seat.locked_until and show_seat.locked_until > now and show_seat.locked_by_id != data['user_id']:
                    return Response({'detail': 'Seat currently held by another user.'}, status=status.HTTP_409_CONFLICT)

            show_seat.status = ShowSeat.STATUS_BOOKED
            show_seat.locked_by_id = data['user_id']
            show_seat.locked_until = None
            show_seat.booked_at = now
            show_seat.save(update_fields=['status', 'locked_by', 'locked_until', 'booked_at'])

            Booking.objects.create(
                user_id=data['user_id'],
                showtime_id=data['show_id'],
                seat_id=data['seat_id'],
            )
    except IntegrityError:
        return Response({'detail': 'Seat already booked.'}, status=status.HTTP_409_CONFLICT)

    return Response({'detail': 'Booking confirmed.'}, status=status.HTTP_201_CREATED)
