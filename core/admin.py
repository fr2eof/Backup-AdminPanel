from django.contrib import admin
from .models import BackupSettings, Log


@admin.register(BackupSettings)
class BackupSettingsAdmin(admin.ModelAdmin):
    list_display = ('interval', 'max_size_gb', 'backup_location')
    list_filter = ('interval', 'max_size_gb')
    search_fields = ('interval',)


@admin.register(Log)
class LogAdmin(admin.ModelAdmin):
    list_display = (
        'date',
        'operation',
    )
    list_filter = ('date', 'operation')
    search_fields = (
        'date',
        'operation',
    )
