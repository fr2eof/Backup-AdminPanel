from backup_log_system_back import settings
from core.models import BackupSettings


def update_backup_location():
    settings_obj = BackupSettings.objects.first()
    if settings_obj:
        settings.BASE_BACKUP_DIR['location'] = settings_obj.backup_location


import os
from django.core.exceptions import PermissionDenied


def check_folder_access(folder_path):
    if not os.path.exists(folder_path):
        raise FileNotFoundError("Folder does not exist.")
    if not os.access(folder_path, os.R_OK):
        raise PermissionDenied("Access to the folder is denied.")
