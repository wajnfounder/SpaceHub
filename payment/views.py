import uuid
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from bookings.models import Booking, BookingStatus
from .models import Payment, PaymentMethod, PaymentStatus


@login_required
def checkout(request, booking_pk):
    booking = get_object_or_404(Booking, pk=booking_pk, tenant=request.user)

    # Already paid?
    if hasattr(booking, 'payment') and booking.payment.status == PaymentStatus.COMPLETED:
        messages.info(request, 'تم الدفع مسبقاً لهذا الحجز.')
        return redirect('bookings:my_bookings')

    if request.method == 'POST':
        method = request.POST.get('method', PaymentMethod.MADA)
        ref    = str(uuid.uuid4())[:12].upper()   # mock reference

        payment, _ = Payment.objects.get_or_create(
            booking=booking,
            defaults={'user': request.user, 'amount': booking.total_price}
        )
        payment.method    = method
        payment.status    = PaymentStatus.COMPLETED
        payment.reference = ref
        payment.amount    = booking.total_price
        payment.save()

        # Auto-confirm booking after payment
        booking.status = BookingStatus.CONFIRMED
        booking.save()

        return redirect('payment:success', booking_pk=booking.pk)

    context = {
        'booking':  booking,
        'methods':  PaymentMethod.choices,
    }
    return render(request, 'payment/checkout.html', context)


@login_required
def payment_success(request, booking_pk):
    booking = get_object_or_404(Booking, pk=booking_pk, tenant=request.user)
    payment = get_object_or_404(Payment, booking=booking)
    return render(request, 'payment/success.html', {'booking': booking, 'payment': payment})
