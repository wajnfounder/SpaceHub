from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, Avg, Count
from .models import Space, SpaceImage, SpaceType, City, SpaceAmenity, AdditionalService, RentalType
from .forms import SpaceForm, SpaceImageForm, SpaceAmenityFormSet, AdditionalServiceFormSet


def smart_match(query_text, spaces_qs, top_n=3):
    keywords = query_text.lower().split()
    scored = []
    for space in spaces_qs:
        text = f"{space.title} {space.description} {space.get_space_type_display()} {space.get_city_display()} {space.address}".lower()
        score = sum(1 for kw in keywords if kw in text)
        if score > 0:
            scored.append((score, space))
    scored.sort(key=lambda x: -x[0])
    return [s for _, s in scored[:top_n]]


def space_list(request):
    spaces = Space.objects.filter(status='available').select_related('owner').prefetch_related('images')

    query       = request.GET.get('q', '')
    space_type  = request.GET.get('type', '')
    city        = request.GET.get('city', '')
    min_price   = request.GET.get('min_price', '')
    max_price   = request.GET.get('max_price', '')
    min_cap     = request.GET.get('min_cap', '')
    rental_type = request.GET.get('rental', '')
    smart       = request.GET.get('smart', '')

    smart_results = []
    if smart:
        smart_results = smart_match(smart, spaces)

    if query:
        spaces = spaces.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query) |
            Q(address__icontains=query)
        )
    if space_type:
        spaces = spaces.filter(space_type=space_type)
    if city:
        spaces = spaces.filter(city=city)
    if min_price:
        spaces = spaces.filter(price_per_day__gte=min_price)
    if max_price:
        spaces = spaces.filter(price_per_day__lte=max_price)
    if min_cap:
        spaces = spaces.filter(capacity__gte=min_cap)
    if rental_type:
        spaces = spaces.filter(rental_type=rental_type)

    spaces = spaces.annotate(avg_rating=Avg('id'), review_count=Count('id'))

    paginator = Paginator(spaces, 9)
    page_obj  = paginator.get_page(request.GET.get('page'))

    fav_ids = set()
    if request.user.is_authenticated:
        try:
            fav_ids = set(request.user.favorites.values_list('space_id', flat=True))
        except:
            fav_ids = set()

    context = {
        'page_obj':        page_obj,
        'query':           query,
        'space_types':     SpaceType.choices,
        'cities':          City.choices,
        'rental_types':    RentalType.choices,
        'selected_type':   space_type,
        'selected_city':   city,
        'selected_rental': rental_type,
        'min_price':       min_price,
        'max_price':       max_price,
        'min_cap':         min_cap,
        'smart':           smart,
        'smart_results':   smart_results,
        'fav_ids':         fav_ids,
    }
    return render(request, 'spaces/list.html', context)


def space_detail(request, pk):
    space = get_object_or_404(
        Space.objects.select_related('owner')
                     .prefetch_related('images', 'amenities', 'additional_services'),
        pk=pk
    )
    user_review = None
    is_favorite = False
    if request.user.is_authenticated:
        try:
            user_review = space.reviews.filter(user=request.user).first()
        except:
            user_review = None
        try:
            is_favorite = request.user.favorites.filter(space=space).exists()
        except:
            is_favorite = False

    criteria_labels = [
        ('cleanliness',  'النظافة'),
        ('internet',     'الإنترنت'),
        ('parking_rate', 'المواقف'),
        ('quietness',    'الهدوء'),
        ('host_service', 'خدمة المالك'),
    ]

    context = {
        'space':           space,
        'user_review':     user_review,
        'avg_rating':      space.average_rating(),
        'is_favorite':     is_favorite,
        'criteria_labels': criteria_labels,
    }
    return render(request, 'spaces/detail.html', context)


@login_required
def space_add(request):
    if not request.user.profile.is_owner():
        messages.error(request, 'فقط أصحاب المساحات يمكنهم إضافة مساحات.')
        return redirect('spaces:list')

    if request.method == 'POST':
        form       = SpaceForm(request.POST)
        image_form = SpaceImageForm(request.POST, request.FILES)
        if form.is_valid():
            space       = form.save(commit=False)
            space.owner = request.user
            space.save()
            if image_form.is_valid() and request.FILES.get('image'):
                img         = image_form.save(commit=False)
                img.space   = space
                img.is_main = True
                img.save()
            messages.success(request, 'تمت إضافة المساحة بنجاح.')
            return redirect('spaces:detail', pk=space.pk)
    else:
        form       = SpaceForm()
        image_form = SpaceImageForm()

    return render(request, 'spaces/add.html', {'form': form, 'image_form': image_form})


@login_required
def space_edit(request, pk):
    space = get_object_or_404(Space, pk=pk, owner=request.user)
    if request.method == 'POST':
        form = SpaceForm(request.POST, instance=space)
        if form.is_valid():
            form.save()
            messages.success(request, 'تم تحديث المساحة بنجاح.')
            return redirect('spaces:detail', pk=space.pk)
    else:
        form = SpaceForm(instance=space)
    return render(request, 'spaces/edit.html', {'form': form, 'space': space})


@login_required
def space_delete(request, pk):
    space = get_object_or_404(Space, pk=pk, owner=request.user)
    if request.method == 'POST':
        space.delete()
        messages.success(request, 'تم حذف المساحة بنجاح.')
        return redirect('accounts:dashboard')
    return render(request, 'spaces/confirm_delete.html', {'space': space})


@login_required
def space_add_image(request, pk):
    space = get_object_or_404(Space, pk=pk, owner=request.user)
    if request.method == 'POST':
        form = SpaceImageForm(request.POST, request.FILES)
        if form.is_valid():
            img       = form.save(commit=False)
            img.space = space
            img.save()
            messages.success(request, 'تمت إضافة الصورة.')
            return redirect('spaces:detail', pk=space.pk)
    else:
        form = SpaceImageForm()
    return render(request, 'spaces/add_image.html', {'form': form, 'space': space})