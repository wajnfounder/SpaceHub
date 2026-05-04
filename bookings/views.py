from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from django.db.models import F
from spaces.models import Space
from .models import Booking, BookingStatus
from .forms import BookingForm


@login_required
def booking_create(request, space_pk):
    space = get_object_or_404(Space, pk=space_pk, status='available')

    if request.user.profile.is_owner():
        messages.error(request, 'أصحاب المساحات لا يمكنهم الحجز.')
        return redirect('spaces:detail', pk=space_pk)

    if space.owner == request.user:
        messages.error(request, 'لا يمكنك حجز مساحتك الخاصة.')
        return redirect('spaces:detail', pk=space_pk)

    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            date_from = form.cleaned_data['date_from']
            date_to = form.cleaned_data['date_to']

            # Check for overlapping confirmed bookings
            conflict = Booking.objects.filter(
                space=space,
                status=BookingStatus.CONFIRMED,
                date_from__lt=date_to,
                date_to__gt=date_from,
            ).exists()

            if conflict:
                messages.error(request, 'المساحة محجوزة في هذه الفترة، يرجى اختيار تواريخ أخرى.')
            else:
                days = (date_to - date_from).days or 1
                total = space.price_per_day * days

                # transaction.atomic ensures both the booking and any future stock update are atomic
                with transaction.atomic():
                    booking = Booking.objects.create(
                        space=space,
                        tenant=request.user,
                        date_from=date_from,
                        date_to=date_to,
                        total_price=total,
                        notes=form.cleaned_data.get('notes', ''),
                    )

                messages.success(request, f'تم إرسال طلب الحجز بنجاح! سيتم مراجعته من قبل المالك.')
                return redirect('bookings:my_bookings')
    else:
        form = BookingForm()

    context = {'form': form, 'space': space}
    return render(request, 'bookings/create.html', context)


@login_required
def my_bookings(request):
    bookings = Booking.objects.filter(tenant=request.user).select_related('space').order_by('-created_at')
    return render(request, 'bookings/my_bookings.html', {'bookings': bookings})


@login_required
def owner_bookings(request):
    if not request.user.profile.is_owner():
        return redirect('spaces:list')
    bookings = Booking.objects.filter(
        space__owner=request.user
    ).select_related('space', 'tenant').order_by('-created_at')
    return render(request, 'bookings/owner_bookings.html', {'bookings': bookings})


@login_required
def booking_confirm(request, pk):
    booking = get_object_or_404(Booking, pk=pk, space__owner=request.user)
    if booking.status == BookingStatus.PENDING:
        booking.status = BookingStatus.CONFIRMED
        booking.save()
        messages.success(request, 'تم تأكيد الحجز.')
    return redirect('bookings:owner_bookings')


@login_required
def booking_cancel(request, pk):
    booking = get_object_or_404(Booking, pk=pk)
    is_owner = booking.space.owner == request.user
    is_tenant = booking.tenant == request.user

    if not (is_owner or is_tenant):
        messages.error(request, 'ليس لديك صلاحية إلغاء هذا الحجز.')
        return redirect('spaces:list')

    if booking.status in (BookingStatus.PENDING, BookingStatus.CONFIRMED):
        booking.status = BookingStatus.CANCELLED
        booking.save()
        messages.success(request, 'تم إلغاء الحجز.')

    return redirect('bookings:owner_bookings' if is_owner else 'bookings:my_bookings')


@login_required
def booking_complete(request, pk):
    booking = get_object_or_404(Booking, pk=pk, space__owner=request.user)
    if booking.status == BookingStatus.CONFIRMED:
        booking.status = BookingStatus.COMPLETED
        booking.save()
        messages.success(request, 'تم تمييز الحجز كمكتمل.')
    return redirect('bookings:owner_bookings')
