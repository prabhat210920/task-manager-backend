from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Goal(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='goals')
    title = models.CharField(max_length=200)
    total_units = models.IntegerField(help_text="Total value to achieve (e.g., 500 pages)")
    units_completed = models.IntegerField(default=0)
    unit_name = models.CharField(max_length=50, help_text="e.g. Pages, KMs")
    start_date = models.DateField()
    end_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    @property
    def progress_percentage(self):
        if self.total_units == 0:
            return 0
        return (self.units_completed / self.total_units) * 100

class DailyLog(models.Model):
    goal = models.ForeignKey(Goal, on_delete=models.CASCADE, related_name='logs')
    date = models.DateField()
    amount = models.IntegerField()
    note = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('goal', 'date')
        ordering = ['-date']

    def __str__(self):
        return f"{self.date} - {self.amount} {self.goal.unit_name}"
