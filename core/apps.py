from django.apps import AppConfig
from backup_log_system_back import settings
from threading import Thread
import time
from datetime import datetime
import os


class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core'
    last_backup_date = None

    def ready(self):
        if not os.environ.get('RUN_MAIN', ''):
            from core.cron import get_database_size, run_manual_backup

            def should_run_backup(schedule):
                today = datetime.today()
                if schedule.interval == 'daily':
                    return True
                elif schedule.interval == 'weekly':
                    return today.weekday() == 0
                elif schedule.interval == 'monthly':
                    return today.day == 1
                elif schedule.interval == 'yearly':
                    return today.month == 1 and today.day == 1
                return False

            def run_periodically():
                while True:
                    from core.models import (
                        BackupSettings,
                    )

                    db_size = get_database_size()

                    admin_settings = BackupSettings.objects.first()
                    if not admin_settings:
                        time.sleep(60)
                        continue

                    backup_dir = os.path.join(
                        settings.BASE_BACKUP_DIR['location'],
                        admin_settings.backup_location.lstrip('/'),
                    )
                    schedule = BackupSettings.objects.first()
                    today_date = datetime.today().date()

                    if schedule and (
                        should_run_backup(schedule)
                        or (db_size > admin_settings.max_size_gb)
                    ):
                        if self.last_backup_date != today_date:
                            run_manual_backup(backup_dir)
                            self.last_backup_date = today_date
                    time.sleep(3600)

            Thread(target=run_periodically, daemon=True).start()
