import axios from 'axios';
import {CONSTANTS} from "@/constants.js";
import {getAuthHeader, refreshAccessToken} from "@/api/api.js";
import router from "@/router/index.js";

const API_URL = CONSTANTS.API_URL + '/logs';

export const fetchLogs = async () => {
    try {
        const response = await axios.get(`${API_URL}/`, {
            headers: getAuthHeader(),
        });
        return response.data;
    } catch (error) {
        if (error.response?.status === 401) {
            try {
                const newAccessToken = await refreshAccessToken();
                localStorage.setItem('access', newAccessToken);
                const retryResponse = await axios.get(`${API_URL}/`, {
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
        throw new Error('Не удалось загрузить логи. Пожалуйста, попробуйте позже.');
    }
};
