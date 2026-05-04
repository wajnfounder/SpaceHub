from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from spaces.models import Space
from .models import Review
from .forms import ReviewForm


@login_required
def review_add(request, space_pk):
    space = get_object_or_404(Space, pk=space_pk)

    if request.user == space.owner:
        messages.error(request, 'لا يمكنك تقييم مساحتك الخاصة.')
        return redirect('spaces:detail', pk=space_pk)

    existing = Review.objects.filter(space=space, user=request.user).first()
    if existing:
        messages.warning(request, 'لقد قيّمت هذه المساحة مسبقاً.')
        return redirect('spaces:detail', pk=space_pk)

    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.space = space
            review.user = request.user
            review.save()
            messages.success(request, 'تم إضافة تقييمك بنجاح.')
            return redirect('spaces:detail', pk=space_pk)
    else:
        form = ReviewForm()

    return render(request, 'reviews/add.html', {'form': form, 'space': space})


@login_required
def review_delete(request, pk):
    review = get_object_or_404(Review, pk=pk, user=request.user)
    space_pk = review.space.pk
    review.delete()
    messages.success(request, 'تم حذف التقييم.')
    return redirect('spaces:detail', pk=space_pk)
