import { createStore } from 'vuex';

export default createStore({
    state: {
        username: null,
        role: null,
        accessToken: null,
        refreshToken: null,
        isLoggedIn: false,
    },
    mutations: {
        loginSuccess(state, payload) {
            state.username = payload.username;
            state.accessToken = payload.accessToken;
            state.refreshToken = payload.refreshToken;
            state.isLoggedIn = true;
            localStorage.setItem('auth', JSON.stringify(payload));
        },
        logout(state) {
            state.username = null;
            state.accessToken = null;
            state.refreshToken = null;
            state.isLoggedIn = false;
            localStorage.removeItem('auth');
        },
        restoreAuth(state) {
            const authData = localStorage.getItem('auth');
            if (authData) {
                const payload = JSON.parse(authData);
                state.username = payload.username;
                state.accessToken = payload.accessToken;
                state.refreshToken = payload.refreshToken;
                state.isLoggedIn = true;
            }
        },
    },
    actions: {
        loginSuccess({ commit }, payload) {
            commit('loginSuccess', payload);
        },
        logout({ commit }) {
            commit('logout');
        },
        restoreAuth({ commit }) {
            commit('restoreAuth');
        },
    },
    getters: {
        isLoggedIn: (state) => state.isLoggedIn,
        username: (state) => state.username,
    },
});