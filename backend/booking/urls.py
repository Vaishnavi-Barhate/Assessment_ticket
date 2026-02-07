from django.urls import path

from . import views

urlpatterns = [
    path('hall-layout/<int:show_id>/', views.hall_layout, name='hall-layout'),
    path('hold-seat/', views.hold_seat, name='hold-seat'),
    path('book-seat/', views.book_seat, name='book-seat'),
]
