import axios from 'axios';
import {CONSTANTS} from "@/constants.js";

const API_URL = CONSTANTS.API_URL;

export const getAuthHeader = () => {
    const accessToken = localStorage.getItem('access');
    return {
        Authorization: `Bearer ${accessToken}`,
    };
};

export const refreshAccessToken = async () => {
    try {
        const refreshToken = localStorage.getItem('refresh');

        if (!refreshToken) {
            throw new Error('Нет refresh токена');
        }

        const response = await axios.post(`${API_URL}/token/refresh/`, {
            refresh: refreshToken,
        });

        const newAccessToken = response.data.access;
        localStorage.setItem('access', newAccessToken);

        return newAccessToken;
    } catch (error) {
        throw new Error(error.response?.data?.detail || 'Ошибка при обновлении токена');
    }
};