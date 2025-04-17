import {reactive, provide, onMounted} from 'vue';

export const useTheme = () => {
    const state = reactive({
        isDarkMode: localStorage.getItem('theme') === 'dark',
    });

    onMounted(() => {
        document.documentElement.setAttribute(
            'data-theme',
            state.isDarkMode ? 'dark' : 'light'
        );
    });

    const toggleTheme = () => {
        state.isDarkMode = !state.isDarkMode;
        localStorage.setItem('theme', state.isDarkMode ? 'dark' : 'light');
        document.documentElement.setAttribute(
            'data-theme',
            state.isDarkMode ? 'dark' : 'light'
        );
    };

    provide('isDarkMode', state.isDarkMode);
    provide('toggleTheme', toggleTheme);

    return {state, toggleTheme};
};
