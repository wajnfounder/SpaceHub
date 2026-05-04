from django.db import models
from django.contrib.auth.models import User
from spaces.models import Space


class Favorite(models.Model):
    user  = models.ForeignKey(User,  on_delete=models.CASCADE, related_name='favorites')
    space = models.ForeignKey(Space, on_delete=models.CASCADE, related_name='favorited_by')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user', 'space']
        ordering = ['-created_at']
        verbose_name = 'مفضلة'
        verbose_name_plural = 'المفضلات'

    def __str__(self):
        return f"{self.user.username} ← {self.space.title}"
