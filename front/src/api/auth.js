import axios from 'axios';
import {CONSTANTS} from "@/constants.js";
import {getAuthHeader, refreshAccessToken} from "@/api/api.js";
import router from "@/router/index.js";

const API_URL = CONSTANTS.API_URL;

export const login = async (userData) => {
    try {
        const response = await axios.post(`${API_URL}/login/`, userData);
        return response.data;
    } catch (error) {
        throw new Error(error.response?.data?.error || 'Ошибка авторизации');
    }
};

export const register = async (userData) => {
    try {
        const response = await axios.post(`${API_URL}/register/`, userData);
        return response.data;
    } catch (error) {
        throw new Error(error.response?.data?.error || 'Ошибка регистрации');
    }
};

export const logout = async (refreshToken) => {
    try {
        const response = await axios.post(`${API_URL}/logout/`, {
            refresh_token: refreshToken,
        }, {
            headers: getAuthHeader(),
        });
        return response.data;
    } catch (error) {
        if (error.response?.status === 401) {
            try {
                const newAccessToken = await refreshAccessToken();
                localStorage.setItem('access', newAccessToken);
                const retryResponse = await axios.post(`${API_URL}/logout/`, {
                    refresh_token: refreshToken,
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
        throw new Error(error.response?.data?.error || 'Ошибка выхода из аккаунта');
    }
};

export const requestPasswordReset = async (email) => {
    try {
        const response = await axios.post(`${API_URL}/password-reset/`, {email});
        return response.data;
    } catch (error) {
        throw new Error(error.response?.data?.error || 'Ошибка при запросе сброса пароля');
    }
};
