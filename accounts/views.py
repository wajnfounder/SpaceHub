from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import Group

from accounts.models import UserProfile
from .forms import RegisterForm, ProfileForm


def set_language(request):
    """Toggle UI language between Arabic and English."""
    lang = request.GET.get('lang', 'ar')
    request.session['lang'] = lang if lang in ('ar', 'en') else 'ar'
    next_url = request.GET.get('next', '/')
    return redirect(next_url)


def register_view(request):
    if request.user.is_authenticated:
        return redirect('spaces:list')

    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()

            # Authorization: add user to the appropriate Group
            role = user.profile.role
            group_name = 'Owner' if role == 'owner' else 'Tenant'
            group, _ = Group.objects.get_or_create(name=group_name)
            user.groups.add(group)

            login(request, user)
            messages.success(request, f'مرحباً {user.username}! تم إنشاء حسابك بنجاح.')
            return redirect('spaces:list')
        else:
            messages.error(request, 'يرجى تصحيح الأخطاء أدناه.')
    else:
        form = RegisterForm()

    return render(request, 'accounts/register.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('spaces:list')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            messages.success(request, f'أهلاً {user.username}!')
            next_url = request.GET.get('next', 'spaces:list')
            return redirect(next_url)
        else:
            messages.error(request, 'اسم المستخدم أو كلمة المرور غير صحيحة.')

    return render(request, 'accounts/login.html')


@login_required
def logout_view(request):
    logout(request)
    messages.info(request, 'تم تسجيل الخروج بنجاح.')
    return redirect('accounts:login')


@login_required
def profile_view(request):
    profile = request.user.profile

    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            # Update User first/last name
            request.user.first_name = form.cleaned_data.get('first_name', '')
            request.user.last_name = form.cleaned_data.get('last_name', '')
            request.user.save()
            form.save()
            messages.success(request, 'تم تحديث الملف الشخصي بنجاح.')
            return redirect('accounts:profile')
    else:
        form = ProfileForm(instance=profile, initial={
            'first_name': request.user.first_name,
            'last_name': request.user.last_name,
        })

    return render(request, 'accounts/profile.html', {'form': form, 'profile': profile})


@login_required
def dashboard_view(request):
    user = request.user
    profile, created = UserProfile.objects.get_or_create(user=user)
    context = {'profile': profile}

    if profile.is_owner():
        from spaces.models import Space
        from bookings.models import Booking, BookingStatus
        my_spaces = Space.objects.filter(owner=user).prefetch_related('images', 'bookings')
        pending_bookings = Booking.objects.filter(
            space__owner=user,
            status=BookingStatus.PENDING
        ).select_related('space', 'tenant')
        context.update({'my_spaces': my_spaces, 'pending_bookings': pending_bookings})
    else:
        from bookings.models import Booking
        my_bookings = Booking.objects.filter(tenant=user).select_related('space')
        context['my_bookings'] = my_bookings

    return render(request, 'accounts/dashboard.html', context)
