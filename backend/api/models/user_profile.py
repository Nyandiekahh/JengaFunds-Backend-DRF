from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    credit_score = models.IntegerField(default=0)
    member_since = models.DateField(auto_now_add=True)
    rating = models.DecimalField(max_digits=3, decimal_places=1, default=0.0)
    total_invested = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_borrowed = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    active_investments = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.user.username}'s profile"