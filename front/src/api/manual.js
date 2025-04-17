import axios from 'axios';
import {getAuthHeader, refreshAccessToken} from "@/api/api.js";
import router from "@/router/index.js";

const API_URL = 'http://127.0.0.1:8000/api';

export const executeManualBackup = async () => {
    try {
        const response = await axios.post(`${API_URL}/manual-backup/`, {}, {
            headers: getAuthHeader(),
        });
        return response.data.message;
    } catch (error) {
        if (error.response?.status === 401) {
            try {
                const newAccessToken = await refreshAccessToken();
                localStorage.setItem('access', newAccessToken);
                const retryResponse = await axios.post(`${API_URL}/manual-backup/`, {}, {
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
        throw new Error(error.response?.data?.error || 'Ошибка выполнения ручного бэкапа');
    }
};
