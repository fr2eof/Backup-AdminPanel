import datetime
import logging
import os

from django.core.management import call_command
from django.db import connection

from core.cryption import encrypt_file, load_key
from core.models import Log

logger = logging.getLogger(__name__)


def get_database_size():
    cursor = connection.cursor()
    cursor.execute("SELECT pg_database_size(current_database())")
    result = cursor.fetchone()
    return result[0] / (1024 * 1024 * 1024)


# you can change on it

# def get_table_size(table_name):
#     cursor = connection.cursor()
#     cursor.execute(f"SELECT pg_total_relation_size(%s)", [table_name])
#     result = cursor.fetchone()
#     return result[0] / (1024 * 1024 * 1024)


def run_manual_backup(backup_dir):
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)

    filename = (
        f"backup_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.sql"
    )

    file_path = os.path.join(backup_dir, filename)

    call_command('dbbackup', output_path=file_path, output_filename=filename)

    key = load_key()
    encrypt_file(file_path, key)

    os.remove(file_path)

    Log.objects.create(operation=f"Backup created: {filename}")
