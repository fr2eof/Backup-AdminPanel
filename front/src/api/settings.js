import axios from "axios";
import {CONSTANTS} from "@/constants.js";
import {getAuthHeader, refreshAccessToken} from "@/api/api.js";
import router from "@/router/index.js";

const API_BASE_URL = CONSTANTS.API_URL;

export const getFolders = async (folderPath) => {
    try {
        const response = await axios.get(`${API_BASE_URL}/folders/`, {
            headers: getAuthHeader(),
            params: {folder_path: folderPath},
        });
        return response.data;
    } catch (error) {
        if (error.response?.status === 401) {
            try {
                const newAccessToken = await refreshAccessToken();
                localStorage.setItem('access', newAccessToken);

                const retryResponse = await axios.get(`${API_BASE_URL}/folders/`, {
                    headers: getAuthHeader(),
                    params: {folder_path: folderPath},
                });
                return retryResponse.data;
            } catch (refreshError) {
                console.error('Ошибка при обновлении токена:', refreshError.message);
                router.push('/login');
                localStorage.clear();
                throw new Error('Не удалось обновить токен. Пожалуйста, войдите снова.');
            }
        }
        throw new Error("Ошибка загрузки папок");
    }
};

export const saveBackupSettings = async (settings) => {
    try {
        const response = await axios.post(`${API_BASE_URL}/backup-settings/`, {
            settings,
        }, {
            headers: getAuthHeader(),
        });
        return response.data;
    } catch (error) {
        if (error.response?.status === 401) {
            try {
                const newAccessToken = await refreshAccessToken();
                localStorage.setItem('access', newAccessToken);

                const retryResponse = await axios.post(`${API_BASE_URL}/backup-settings/`, {
                    settings,
                }, {
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
        throw new Error(error.response?.data?.error || "Ошибка сохранения настроек");
    }
};
export const getBackupSettings = async () => {
    try {
        const response = await axios.get(`${API_BASE_URL}/backup-settings/`, {
            headers: getAuthHeader(),
        });
        return response.data;
    } catch (error) {
        if (error.response?.status === 401) {
            try {
                const newAccessToken = await refreshAccessToken();
                localStorage.setItem('access', newAccessToken);

                const retryResponse = await axios.get(`${API_BASE_URL}/backup-settings/`, {
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
        throw new Error("Ошибка загрузки настроек резервного копирования");
    }
};

