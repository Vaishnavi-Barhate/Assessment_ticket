from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Venue',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('city', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='Hall',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('venue', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='halls', to='booking.venue')),
            ],
        ),
        migrations.CreateModel(
            name='Movie',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('duration_minutes', models.PositiveIntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='Seat',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('row', models.CharField(max_length=5)),
                ('number', models.PositiveIntegerField()),
                ('hall', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='seats', to='booking.hall')),
            ],
            options={
                'unique_together': {('hall', 'row', 'number')},
            },
        ),
        migrations.CreateModel(
            name='Showtime',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('starts_at', models.DateTimeField()),
                ('ends_at', models.DateTimeField()),
                ('hall', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='showtimes', to='booking.hall')),
                ('movie', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='showtimes', to='booking.movie')),
            ],
        ),
        migrations.CreateModel(
            name='ShowSeat',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(choices=[('available', 'Available'), ('held', 'Held'), ('booked', 'Booked')], default='available', max_length=20)),
                ('locked_until', models.DateTimeField(blank=True, null=True)),
                ('booked_at', models.DateTimeField(blank=True, null=True)),
                ('locked_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='held_seats', to=settings.AUTH_USER_MODEL)),
                ('seat', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='show_seats', to='booking.seat')),
                ('showtime', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='show_seats', to='booking.showtime')),
            ],
            options={
                'unique_together': {('showtime', 'seat')},
            },
        ),
        migrations.CreateModel(
            name='Booking',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('seat', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='bookings', to='booking.seat')),
                ('showtime', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='bookings', to='booking.showtime')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='bookings', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'unique_together': {('showtime', 'seat')},
            },
        ),
        migrations.AddIndex(
            model_name='seat',
            index=models.Index(fields=['hall', 'row', 'number'], name='booking_sea_hall_id_3fd3b2_idx'),
        ),
        migrations.AddIndex(
            model_name='showtime',
            index=models.Index(fields=['hall', 'starts_at'], name='booking_sho_hall_id_2d2e38_idx'),
        ),
        migrations.AddIndex(
            model_name='showseat',
            index=models.Index(fields=['showtime', 'status'], name='booking_sho_showtim_9a2891_idx'),
        ),
        migrations.AddIndex(
            model_name='booking',
            index=models.Index(fields=['showtime', 'created_at'], name='booking_boo_showtim_5829d5_idx'),
        ),
    ]
