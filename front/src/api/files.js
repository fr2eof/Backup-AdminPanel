import axios from 'axios';
import {getAuthHeader, refreshAccessToken} from './api.js';
import {CONSTANTS} from "@/constants.js";
import router from "@/router/index.js";

const API_URL = CONSTANTS.API_URL + '/files';

export const fetchFiles = async (folderPath) => {
    if (!folderPath) {
        throw new Error('Путь к папке обязателен');
    }
    try {
        const response = await axios.get(`${API_URL}/`, {
            params: {folder_path: "backup/" + folderPath},
            headers: getAuthHeader(),
        });
        return response.data;
    } catch (error) {
        if (error.response?.status === 401) {
            try {
                const newAccessToken = await refreshAccessToken();
                localStorage.setItem('access', newAccessToken);

                const retryResponse = await axios.get(`${API_URL}/`, {
                    params: {folder_path: "backup/" + folderPath},
                    headers: getAuthHeader(),
                });
                return retryResponse.data;
            } catch (refreshError) {
                console.error('Ошибка при обновлении токена:', refreshError.message);
                router.push('/login');
                localStorage.clear();
                throw new Error('Не удалось обновить токен. Пожалуйста, войдите снова.');
            }
        }
        throw new Error(error.response?.data?.error || 'Ошибка при загрузке файлов');
    }
};

export const downloadFile = async (folderPath, fileName) => {
    if (!folderPath || !fileName) {
        throw new Error('Путь к папке и имя файла обязательны');
    }
    try {
        const response = await axios.get(`${API_URL}/download/`, {
            params: {folder_path: folderPath, file_name: fileName},
            responseType: 'blob',
            headers: getAuthHeader(),
        });
        const blob = new Blob([response.data]);
        const link = document.createElement('a');
        link.href = URL.createObjectURL(blob);
        link.download = fileName;
        link.click();
    } catch (error) {
        if (error.response?.status === 401) {
            try {
                const newAccessToken = await refreshAccessToken();
                localStorage.setItem('access', newAccessToken);

                const retryResponse = await axios.get(`${API_URL}/download/`, {
                    params: {folder_path: folderPath, file_name: fileName},
                    responseType: 'blob',
                    headers: getAuthHeader(),
                });
                const blob = new Blob([retryResponse.data]);
                const link = document.createElement('a');
                link.href = URL.createObjectURL(blob);
                link.download = fileName;
                link.click();
            } catch (refreshError) {
                console.error('Ошибка при обновлении токена:', refreshError.message);
                router.push('/login');
                localStorage.clear();
                throw new Error('Не удалось обновить токен. Пожалуйста, войдите снова.');
            }
        }
        throw new Error(error.response?.data?.error || 'Ошибка при скачивании файла');
    }
};

export const deleteFile = async (folderPath, fileName) => {
    if (!folderPath || !fileName) {
        throw new Error('Путь к папке и имя файла обязательны');
    }
    try {
        await axios.delete(`${API_URL}/delete/`, {
            data: {folder_path: folderPath, file_name: fileName},
            headers: getAuthHeader(),
        });
    } catch (error) {
        if (error.response?.status === 401) {
            try {
                const newAccessToken = await refreshAccessToken();
                localStorage.setItem('access', newAccessToken);

                await axios.delete(`${API_URL}/delete/`, {
                    data: {folder_path: folderPath, file_name: fileName},
                    headers: getAuthHeader(),
                });
            } catch (refreshError) {
                console.error('Ошибка при обновлении токена:', refreshError.message);
                router.push('/login');
                localStorage.clear();
                throw new Error('Не удалось обновить токен. Пожалуйста, войдите снова.');
            }
        }
        throw new Error(error.response?.data?.error || 'Ошибка при удалении файла');
    }
};

export const deleteAllFiles = async (folderPath) => {
    if (!folderPath) {
        throw new Error('Путь к папке обязателен');
    }
    try {
        await axios.delete(`${API_URL}/delete_all/`, {
            data: {folder_path: "backup/" + folderPath},
            headers: getAuthHeader(),
        });
    } catch (error) {
        if (error.response?.status === 401) {
            try {
                const newAccessToken = await refreshAccessToken();
                localStorage.setItem('access', newAccessToken);

                await axios.delete(`${API_URL}/delete_all/`, {
                    data: {folder_path: "backup/" + folderPath},
                    headers: getAuthHeader(),
                });
            } catch (refreshError) {
                console.error('Ошибка при обновлении токена:', refreshError.message);
                router.push('/login');
                localStorage.clear();
                throw new Error('Не удалось обновить токен. Пожалуйста, войдите снова.');
            }
        }
        throw new Error(error.response?.data?.error || 'Ошибка при удалении всех файлов');
    }
};

export const uploadFile = async (folderPath, file) => {
    if (!folderPath || !file) {
        throw new Error('Путь к папке и файл обязательны');
    }
    try {
        const formData = new FormData();

        formData.append('folder_path', "backup/" + folderPath);
        formData.append('file', file);
        const response = await axios.post(`${API_URL}/upload/`, formData, {
            headers: getAuthHeader(),
            'Content-Type': 'multipart/form-data'

        });
        return response.data;
    } catch (error) {
        if (error.response?.status === 401) {
            try {
                const formData = new FormData();

                formData.append('folder_path', "backup/" + folderPath);
                formData.append('file', file);
                const retryResponse = await axios.post(`${API_URL}/upload/`, formData, {
                    headers: getAuthHeader(),
                    'Content-Type': 'multipart/form-data'

                });

                return retryResponse.data;
            } catch (refreshError) {
                console.error('Ошибка при обновлении токена:', refreshError.message);
                router.push('/login');
                localStorage.clear();
                throw new Error('Не удалось обновить токен. Пожалуйста, войдите снова.');
            }
        }
        throw new Error(error.response?.data?.error || 'Ошибка при загрузке файла');
    }
};

export const verifyFileMet = async (file) => {
    if (!file) {
        throw new Error('Файл обязателен для проверки');
    }
    try {
        const formData = new FormData();
        formData.append('file', file);

        const response = await axios.post(`${API_URL}/verify/`, formData, {
            headers: getAuthHeader(),
            'Content-Type': 'multipart/form-data',
        });
        return response.data.message;
    } catch (error) {
        if (error.response?.status === 401) {
            try {
                const newAccessToken = await refreshAccessToken();
                localStorage.setItem('access', newAccessToken);

                const formData = new FormData();
                formData.append('file', file);
                const retryResponse = await axios.post(`${API_URL}/verify/`, formData, {
                    headers: getAuthHeader(),
                    'Content-Type': 'multipart/form-data',
                });

                return retryResponse.data.message;
            } catch (refreshError) {
                console.error('Ошибка при обновлении токена:', refreshError.message);
                router.push('/login');
                localStorage.clear();
                throw new Error('Не удалось обновить токен. Пожалуйста, войдите снова.');
            }
        }
        throw new Error(error.response?.data?.error || 'Ошибка при проверке файла');
    }
};
