from django.urls import path
from .views import (
    LoginView,
    RegisterView,
    LogoutView,
    ActivateAccountView,
    PasswordResetConfirmView,
    LogListView,
    FileListView,
    UploadArchiveView,
    DeleteAllFilesView,
    DeleteFileView,
    DownloadFileView,
    FolderListView,
    VerifyEncryptedFileView,
    PasswordResetRequestView,
)
from core.views import UpdateBackupSettingsView, ManualBackupView
from rest_framework_simplejwt.views import (
    TokenRefreshView,
)

urlpatterns = [
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('register/', RegisterView.as_view(), name='register'),
    path(
        'activate/<uidb64>/<token>/',
        ActivateAccountView.as_view(),
        name='activate',
    ),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path(
        'password-reset/',
        PasswordResetRequestView.as_view(),
        name='password-reset',
    ),
    path(
        'reset-password-confirm/<uidb64>/<token>/',
        PasswordResetConfirmView.as_view(),
        name='password-reset-confirm',
    ),
    path('logs/', LogListView.as_view(), name='log-list'),
    path('files/', FileListView.as_view(), name='file-list'),
    path('folders/', FolderListView.as_view(), name='folder-list'),
    path('files/upload/', UploadArchiveView.as_view(), name='upload_archive'),
    path(
        'files/delete_all/',
        DeleteAllFilesView.as_view(),
        name='delete_all_files',
    ),
    path('files/delete/', DeleteFileView.as_view(), name='delete_file'),
    path('files/download/', DownloadFileView.as_view(), name='download_file'),
    path(
        'files/verify/', VerifyEncryptedFileView.as_view(), name='verify_file'
    ),
    path(
        'backup-settings/',
        UpdateBackupSettingsView.as_view(),
        name='backup_settings',
    ),
    path('manual-backup/', ManualBackupView.as_view(), name='execute_backup'),
]
