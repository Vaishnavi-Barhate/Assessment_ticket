from django.contrib.auth import get_user_model
from rest_framework import serializers

from .models import Showtime, ShowSeat

User = get_user_model()


class SeatStatusSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    row = serializers.CharField()
    number = serializers.IntegerField()
    status = serializers.CharField()
    locked_by = serializers.IntegerField(allow_null=True)
    locked_until = serializers.DateTimeField(allow_null=True)


class HallLayoutSerializer(serializers.Serializer):
    show_id = serializers.IntegerField()
    hall_name = serializers.CharField()
    venue_name = serializers.CharField()
    movie_title = serializers.CharField()
    starts_at = serializers.DateTimeField()
    seats = SeatStatusSerializer(many=True)


class BookSeatSerializer(serializers.Serializer):
    user_id = serializers.IntegerField()
    seat_id = serializers.IntegerField()
    show_id = serializers.IntegerField()

    def validate(self, attrs):
        if not User.objects.filter(id=attrs['user_id']).exists():
            raise serializers.ValidationError({'user_id': 'User not found.'})
        if not Showtime.objects.filter(id=attrs['show_id']).exists():
            raise serializers.ValidationError({'show_id': 'Showtime not found.'})
        if not ShowSeat.objects.filter(showtime_id=attrs['show_id'], seat_id=attrs['seat_id']).exists():
            raise serializers.ValidationError({'seat_id': 'Seat not part of this showtime.'})
        return attrs


class HoldSeatSerializer(BookSeatSerializer):
    pass
