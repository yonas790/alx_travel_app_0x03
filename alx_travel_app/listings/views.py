from .tasks import send_booking_confirmation

def perform_create(self, serializer):
    booking = serializer.save()
    send_booking_confirmation.delay(booking.user.email, booking.id)
