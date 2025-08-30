from celery import shared_task
from django.core.mail import send_mail

@shared_task
def send_booking_confirmation(email, booking_id):
    subject = "Booking Confirmation"
    message = f"Your booking with ID {booking_id} has been confirmed!"
    send_mail(subject, message, "no-reply@alxtravel.com", [email])
