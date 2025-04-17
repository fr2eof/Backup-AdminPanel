from django.utils import timezone

from django.db import models


class BackupSettings(models.Model):
    INTERVAL_CHOICES = [
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
        ('yearly', 'Yearly'),
    ]
    interval = models.CharField(
        max_length=10, choices=INTERVAL_CHOICES, default='daily'
    )
    max_size_gb = models.FloatField(default=0.5)
    backup_location = models.CharField(max_length=255, default='/backup')

    def __str__(self):
        return f"Backup {self.interval} at {self.backup_location}, max size {self.max_size_gb} GB"


class Log(models.Model):
    date = models.DateTimeField(auto_now_add=True)
    operation = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.date} - {self.operation}"


class PendingUser(models.Model):
    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128)
    created_at = models.DateTimeField(default=timezone.now)
    activation_token = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.username
