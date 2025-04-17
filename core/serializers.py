from rest_framework import serializers
from .models import BackupSettings, Log


class BackupSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = BackupSettings
        fields = '__all__'


class LogSerializer(serializers.ModelSerializer):
    class Meta:
        model = Log
        fields = ['id', 'date', 'operation']
