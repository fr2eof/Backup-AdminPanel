import uuid

from django.contrib.auth.models import User
from django.contrib.sites.shortcuts import get_current_site
from django.core.exceptions import PermissionDenied
from django.core.mail import send_mail
from django.http import FileResponse
from django.shortcuts import render
from django.template.loader import render_to_string
from django.utils.encoding import force_str, force_bytes
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response

from .cryption import verify_encrypted_file
from .serializers import BackupSettingsSerializer
from core.cron import *
from core.tokens import CustomTokenGenerator

from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate

from .utils import check_folder_access


# AUTHORIZATION
class LoginView(APIView):
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')

        user = authenticate(request, username=username, password=password)
        if user is not None:
            refresh = RefreshToken.for_user(user)
            return Response(
                {
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                }
            )
        return Response(
            {'error': 'Invalid credentials'},
            status=status.HTTP_400_BAD_REQUEST,
        )


class RegisterView(APIView):
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        email = request.data.get('email')

        if not username or not password or not email:
            return Response(
                {'error': 'Username, password, and email are required'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if (
            PendingUser.objects.filter(username=username).exists()
            or User.objects.filter(username=username).exists()
        ):
            return Response(
                {'error': 'Username already exists'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if (
            PendingUser.objects.filter(email=email).exists()
            or User.objects.filter(email=email).exists()
        ):
            return Response(
                {'error': 'Email already exists'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        pending_user = PendingUser.objects.create(
            username=username, email=email, password=password
        )

        token = CustomTokenGenerator().make_token(pending_user)
        uid = urlsafe_base64_encode(force_bytes(pending_user.pk))
        current_site = get_current_site(request)
        mail_subject = 'Подтвердите ваш email'
        message = render_to_string(
            'account/email_activation.html',
            {
                'user': pending_user,
                'domain': current_site.domain,
                'uid': uid,
                'token': token,
            },
        )

        try:
            send_mail(
                mail_subject, message, None, [email], html_message=message
            )
        except Exception as e:
            pending_user.delete()
            return Response(
                {'error': f'Ошибка при отправке письма'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        return Response(
            {
                'message': 'Пожалуйста, подтвердите ваш email для завершения регистрации.'
            },
            status=status.HTTP_201_CREATED,
        )


class ActivateAccountView(APIView):
    def get(self, request, uidb64, token):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            pending_user = PendingUser.objects.get(pk=uid)

            if CustomTokenGenerator().check_token(pending_user, token):
                user = User.objects.create_user(
                    username=pending_user.username,
                    email=pending_user.email,
                    password=pending_user.password,
                )
                user.is_active = True
                user.save()

                pending_user.delete()

                current_site = get_current_site(request)
                return render(
                    request,
                    'account/email_confirmation.html',
                    {
                        'success': True,
                        'domain': current_site.domain,
                    },
                )
            else:
                current_site = get_current_site(request)
                return render(
                    request,
                    'account/email_confirmation.html',
                    {
                        'success': False,
                        'domain': current_site.domain,
                    },
                    status=400,
                )
        except (TypeError, ValueError, PendingUser.DoesNotExist):
            current_site = get_current_site(request)
            return render(
                request,
                'account/email_confirmation.html',
                {
                    'success': False,
                    'domain': current_site.domain,
                },
                status=400,
            )


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data.get('refresh_token')
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(
                {'message': 'Logout successful'},
                status=status.HTTP_205_RESET_CONTENT,
            )
        except Exception as e:
            return Response(
                {'error': 'Invalid token'}, status=status.HTTP_400_BAD_REQUEST
            )


class PasswordResetRequestView(APIView):
    def post(self, request):
        email = request.data.get('email')

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response(
                {'error': 'Пользователь с таким email не найден'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        token = CustomTokenGenerator().make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        current_site = get_current_site(request)
        reset_url = f"http://{current_site.domain}/api/reset-password-confirm/{uid}/{token}/"

        mail_subject = 'Сброс пароля'
        message = render_to_string(
            'account/password_reset_email.html',
            {
                'user': user,
                'reset_url': reset_url,
            },
        )
        try:
            send_mail(
                mail_subject, message, None, [email], html_message=message
            )
        except Exception:
            return Response(
                {'error': f'Ошибка при отправке письма'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        return Response(
            {'message': 'Ссылка для сброса пароля отправлена на ваш email'},
            status=status.HTTP_200_OK,
        )


class PasswordResetConfirmView(APIView):
    def get(self, request, uidb64, token):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)

            if not CustomTokenGenerator().check_token(user, token):
                return Response(
                    {'error': 'Неверная ссылка для сброса пароля'},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            return render(
                request,
                'account/password_reset.html',
                {
                    'uidb64': uidb64,
                    'token': token,
                },
            )

        except (TypeError, ValueError, User.DoesNotExist):
            return Response(
                {'error': 'Неверная ссылка для сброса пароля'},
                status=status.HTTP_400_BAD_REQUEST,
            )

    def post(self, request, uidb64, token):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)

            if not CustomTokenGenerator().check_token(user, token):
                return render(
                    request,
                    'account/password_reset.html',
                    {
                        'error': 'Неверная ссылка для сброса пароля',
                    },
                )

            new_password = request.data.get('new_password')
            if not new_password:
                return render(
                    request,
                    'account/password_reset.html',
                    {
                        'error': 'Новый пароль не предоставлен',
                    },
                )

            user.set_password(new_password)
            user.save()

            return render(
                request,
                'account/password_reset.html',
                {
                    'success': True,
                    'message': 'Пароль успешно изменен',
                },
            )

        except (TypeError, ValueError, User.DoesNotExist):
            return render(
                request,
                'account/password_reset.html',
                {
                    'error': 'Неверная ссылка для сброса пароля',
                },
            )


# DATA TABLES
from .models import Log, BackupSettings, PendingUser
from .serializers import LogSerializer


class LogListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        logs = Log.objects.all().order_by('-date')
        serializer = LogSerializer(logs, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class FileListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        folder_path = request.query_params.get('folder_path')
        if not folder_path:
            return Response(
                {'error': 'Folder path is required'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            check_folder_access(folder_path)
        except FileNotFoundError:
            return Response(
                {'error': 'Folder does not exist'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except PermissionDenied:
            return Response(
                {'error': 'Access denied to folder'},
                status=status.HTTP_403_FORBIDDEN,
            )

        try:
            files = [
                {
                    'ID': idx + 1,
                    'Название': file_name,
                    'Дата': os.path.getmtime(
                        os.path.join(folder_path, file_name)
                    ),
                    'Место': folder_path,
                }
                for idx, file_name in enumerate(os.listdir(folder_path))
                if os.path.isfile(os.path.join(folder_path, file_name))
            ]
            return Response(files, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


# DIRECTORY WORK
class FolderListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        folder_path = request.query_params.get('folder_path')

        if not folder_path:
            return Response(
                {'error': 'Folder path is required'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not os.path.exists(folder_path) or not os.path.isdir(folder_path):
            return Response(
                {'error': 'Invalid folder path'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            folders = [
                folder_name
                for folder_name in os.listdir(folder_path)
                if os.path.isdir(os.path.join(folder_path, folder_name))
                and folder_name.lower() != "secure"
            ]
            return Response({'folders': folders}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


# FILE WORK
class UploadArchiveView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        file = request.FILES.get('file')
        folder_path = request.data.get('folder_path')

        if not file or not folder_path:
            return Response(
                {'error': 'File and folder path are required'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not os.path.exists(folder_path) or not os.path.isdir(folder_path):
            return Response(
                {'error': 'Invalid folder path'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        temp_file_path = os.path.join(folder_path, f".tmp_{uuid.uuid4()}")
        try:
            with open(temp_file_path, 'wb+') as destination:
                for chunk in file.chunks():
                    destination.write(chunk)

            key = load_key()

            if not verify_encrypted_file(temp_file_path, key):
                os.remove(temp_file_path)
                return Response(
                    {'error': 'Invalid encryption detected'},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            final_file_path = os.path.join(folder_path, file.name)
            os.rename(temp_file_path, final_file_path)
            Log.objects.create(operation=f"Backup upload: {file.name}")
            return Response(
                {'message': 'File uploaded successfully'},
                status=status.HTTP_201_CREATED,
            )

        except Exception as e:
            if os.path.exists(temp_file_path):
                os.remove(temp_file_path)
            return Response(
                {'error': e}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class DeleteAllFilesView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request):
        folder_path = request.data.get('folder_path')

        if not folder_path:
            return Response(
                {'error': 'Folder path is required'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not os.path.exists(folder_path) or not os.path.isdir(folder_path):
            return Response(
                {'error': 'Invalid folder path'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            for file_name in os.listdir(folder_path):
                file_path = os.path.join(folder_path, file_name)
                if os.path.isfile(file_path):
                    os.remove(file_path)
            Log.objects.create(
                operation=f"All backups deleted from: {folder_path}"
            )
            return Response(
                {'message': 'All files deleted successfully'},
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response(
                {'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class DeleteFileView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request):
        folder_path = request.data.get('folder_path')
        file_name = request.data.get('file_name')

        if not folder_path or not file_name:
            return Response(
                {'error': 'Folder path and file name are required'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        file_path = os.path.join(folder_path, file_name)
        if not os.path.exists(file_path) or not os.path.isfile(file_path):
            return Response(
                {'error': 'File does not exist'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            os.remove(file_path)
            Log.objects.create(operation=f"Backup deleted: {file_name}")
            return Response(
                {'message': f'File {file_name} deleted successfully'},
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response(
                {'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class DownloadFileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        folder_path = request.query_params.get('folder_path')
        file_name = request.query_params.get('file_name')

        if not folder_path or not file_name:
            return Response(
                {'error': 'Folder path and file name are required'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        file_path = os.path.join(folder_path, file_name)
        if not os.path.exists(file_path) or not os.path.isfile(file_path):
            return Response(
                {'error': 'File does not exist'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            file_handle = open(file_path, 'rb')
            response = FileResponse(
                file_handle, as_attachment=True, filename=file_name
            )
            Log.objects.create(operation=f"Backup downloaded: {file_name}")
            return response
        except Exception as e:
            return Response(
                {'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class VerifyEncryptedFileView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        file = request.FILES.get('file')
        key = load_key()

        if not file or not key:
            return Response(
                {'error': 'File and key are required'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            temp_file_path = '/tmp/temp_encrypted_file'
            with open(temp_file_path, 'wb') as temp_file:
                for chunk in file.chunks():
                    temp_file.write(chunk)

            is_valid = verify_encrypted_file(temp_file_path, key)

            os.remove(temp_file_path)

            if is_valid:
                return Response(
                    {'message': 'File is valid'}, status=status.HTTP_200_OK
                )
            else:
                return Response(
                    {'message': 'File is invalid'}, status=status.HTTP_200_OK
                )

        except Exception as e:
            return Response(
                {'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


# SETTINGS WORK
import os
from django.conf import settings


class UpdateBackupSettingsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        schedule = BackupSettings.objects.first()
        serializer = BackupSettingsSerializer(schedule)
        return Response(serializer.data)

    def post(self, request):
        print(request.data)
        schedule = BackupSettings.objects.first()
        serializer = BackupSettingsSerializer(
            schedule, data=request.data.get('settings', {}), partial=True
        )
        backup_dir = os.path.join(
            settings.BASE_BACKUP_DIR['location'],
            request.data.get("backup_location", "").lstrip('/'),
        )

        try:
            if not os.path.exists(backup_dir):
                os.makedirs(backup_dir)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(
                serializer.errors, status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {"error": f"Failed to create directory: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class ManualBackupView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            admin_settings = BackupSettings.objects.first()
            if not admin_settings:
                return Response(
                    {"error": "Backup settings not found."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            backup_dir = os.path.join(
                settings.BASE_BACKUP_DIR['location'],
                admin_settings.backup_location.lstrip('/'),
            )
            run_manual_backup(backup_dir)
            return Response(
                {"message": "Backup executed successfully!"},
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
