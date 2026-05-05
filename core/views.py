from django.shortcuts import render, redirect
from spaces.models import Space
from django.contrib import messages
from .models import ContactMessage

def home(request):
    latest_spaces = Space.objects.filter(status='available').prefetch_related('images')[:3]
    return render(request, 'core/home.html', {'latest_spaces': latest_spaces})


def privacy(request):
    return render(request, 'core/privacy.html')

def terms(request):
    return render(request, 'core/terms.html')


def contact(request):
    if request.method == 'POST':
        name    = request.POST.get('name')
        email   = request.POST.get('email')
        subject = request.POST.get('subject')
        message = request.POST.get('message')

        ContactMessage.objects.create(
            name=name,
            email=email,
            subject=subject,
            message=message,
        )

        lang = request.session.get('lang', 'ar')
        if lang == 'en':
            messages.success(request, '✓ Your message has been sent successfully!')
        else:
            messages.success(request, '✓ تم إرسال رسالتك بنجاح!')

        return redirect('core:contact')

    return render(request, 'core/contact.html')

def privacy(request):
    return render(request, 'core/privacy.html')

def terms(request):
    return render(request, 'core/terms.html')