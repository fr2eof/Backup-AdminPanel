import {createRouter, createWebHistory} from 'vue-router';
import LoginView from '@/views/Login.vue';
import SignupView from '@/views/Signup.vue';
import ArchivesView from '@/views/ArchiveList.vue';
import SettingsView from '@/views/Settings.vue';
import LogsView from '@/views/Logs.vue';
import ResetRequestView from '@/views/ResetPasswordRequest.vue';

const routes = [
    {
        path: '/',
        redirect: '/login',
    },
    {
        path: '/login',
        component: LoginView,
    },
    {
        path: '/signup',
        component: SignupView,
    },
    {
        path: '/reset-password-request',
        component: ResetRequestView,
    },
    {
        path: '/archives',
        component: ArchivesView,
    },
    {
        path: '/settings',
        component: SettingsView,
    },
    {
        path: '/logs',
        component: LogsView,
    },
    {
        path: '/:catchAll(.*)',
        redirect: '/login',
    },
];

const router = createRouter({
    history: createWebHistory(import.meta.env.BASE_URL),
    routes,
});

export default router;
