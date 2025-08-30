from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .models import Listing, Booking
from .serializers import ListingSerializer, BookingSerializer
from django.conf import settings
from django.http import JsonResponse
from .models import Payment

### LISTINGS CRUD ###

@swagger_auto_schema(
    method='get',
    responses={200: ListingSerializer(many=True)}
)
@swagger_auto_schema(
    method='post',
    request_body=ListingSerializer,
    responses={201: ListingSerializer}
)
@api_view(['GET', 'POST'])
def listing_list_create(request):
    """Retrieve all listings or create a new listing"""
    if request.method == 'GET':
        listings = Listing.objects.all()
        serializer = ListingSerializer(listings, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = ListingSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(
    method='get',
    responses={200: ListingSerializer}
)
@swagger_auto_schema(
    method='put',
    request_body=ListingSerializer,
    responses={200: ListingSerializer}
)
@swagger_auto_schema(
    method='delete',
    responses={204: 'No Content'}
)
@api_view(['GET', 'PUT', 'DELETE'])
def listing_detail(request, pk):
    """Retrieve, update, or delete a listing by ID"""
    try:
        listing = Listing.objects.get(pk=pk)
    except Listing.DoesNotExist:
        return Response({"error": "Listing not found"}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = ListingSerializer(listing)
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = ListingSerializer(listing, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        listing.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


### BOOKINGS CRUD ###

@swagger_auto_schema(
    method='get',
    responses={200: BookingSerializer(many=True)}
)
@swagger_auto_schema(
    method='post',
    request_body=BookingSerializer,
    responses={201: BookingSerializer}
)
@api_view(['GET', 'POST'])
def booking_list_create(request):
    """Retrieve all bookings or create a new booking"""
    if request.method == 'GET':
        bookings = Booking.objects.all()
        serializer = BookingSerializer(bookings, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = BookingSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(
    method='get',
    responses={200: BookingSerializer}
)
@swagger_auto_schema(
    method='put',
    request_body=BookingSerializer,
    responses={200: BookingSerializer}
)
@swagger_auto_schema(
    method='delete',
    responses={204: 'No Content'}
)
@api_view(['GET', 'PUT', 'DELETE'])
def booking_detail(request, pk):
    """Retrieve, update, or delete a booking by ID"""
    try:
        booking = Booking.objects.get(pk=pk)
    except Booking.DoesNotExist:
        return Response({"error": "Booking not found"}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = BookingSerializer(booking)
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = BookingSerializer(booking, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        booking.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    

def initiate_payment(request):
    # Example booking data
    booking_reference = request.POST.get("booking_reference")
    amount = request.POST.get("amount")

    payment = Payment.objects.create(
        booking_reference=booking_reference,
        amount=amount
    )

    payload = {
        "amount": amount,
        "currency": "ETB",
        "email": "yonas@gmail.com", 
        "tx_ref": str(payment.payment_id),
        "callback_url": "http://localhost:8000/listings/verify-payment/",
        "first_name": "Yonas",
        "last_name": "Yonas"
    }

    headers = {
        "Authorization": f"Bearer {settings.CHAPA_SECRET_KEY}",
        "Content-Type": "application/json"
    }

    response = requests.post(f"{settings.CHAPA_BASE_URL}/transaction/initialize", json=payload, headers=headers)
    data = response.json()

    if response.status_code == 200 and data.get("status") == "success":
        payment.transaction_id = data["data"]["id"]
        payment.save()
        return JsonResponse({"payment_url": data["data"]["checkout_url"]})
    return JsonResponse({"error": data.get("message", "Failed to initiate payment")}, status=400)


def verify_payment(request):
    tx_ref = request.GET.get("tx_ref")  # or transaction_id
    payment = Payment.objects.get(payment_id=tx_ref)

    headers = {
        "Authorization": f"Bearer {settings.CHAPA_SECRET_KEY}"
    }

    response = requests.get(f"{settings.CHAPA_BASE_URL}/transaction/verify/{payment.transaction_id}", headers=headers)
    data = response.json()

    if response.status_code == 200 and data.get("status") == "success":
        payment.status = "Completed"
    else:
        payment.status = "Failed"
    payment.save()

    return JsonResponse({
        "payment_id": payment.payment_id,
        "status": payment.status
    })

