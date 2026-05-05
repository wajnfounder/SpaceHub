from urllib import request

from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
from django.contrib import messages
import favorites
from spaces.models import Space
from .models import Favorite


@login_required
def toggle_favorite(request, space_pk):
    space = get_object_or_404(Space, pk=space_pk)
    fav, created = Favorite.objects.get_or_create(user=request.user, space=space)
    if not created:
        fav.delete()
        messages.info(request, f'تمت إزالة "{space.title}" من المفضلة.')
    else:
        messages.success(request, f'تمت إضافة "{space.title}" إلى المفضلة.')
    return redirect(request.META.get('HTTP_REFERER', 'spaces:list'))


@login_required
def my_favorites(request):
    favorites = Favorite.objects.filter(user=request.user).select_related('space')
    return render(request, 'favorites/list.html', {'favorites': favorites})
