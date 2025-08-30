from django.db import models
import uuid

class Listing(models.Model):
    """Model for property listings"""
    title = models.CharField(max_length=255)
    description = models.TextField()
    location = models.CharField(max_length=255)
    price_per_night = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


class Booking(models.Model):
    """Model for bookings"""
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name='bookings')
    user_name = models.CharField(max_length=255)  # Assuming a simple name field instead of FK to User model
    user_email = models.EmailField()
    start_date = models.DateField()
    end_date = models.DateField()
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(
        max_length=20,
        choices=[('pending', 'Pending'), ('confirmed', 'Confirmed'), ('canceled', 'Canceled')],
        default='pending'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Booking {self.id} - {self.user_name}"
    
class Payment(models.Model):
    payment_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    booking_reference = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_id = models.CharField(max_length=100, blank=True, null=True)
    status = models.CharField(max_length=20, default="Pending")  # Pending, Completed, Failed
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.booking_reference} - {self.status}"