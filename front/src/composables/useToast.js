import { inject } from 'vue';

export const useToast = () => {
    const toast = inject('toast');

    const showToast = (message, type, duration = 3000) => {
        if (toast) {
            toast.message = message;
            toast.type = type;
            toast.isVisible = true;

            setTimeout(() => {
                toast.isVisible = false;
            }, duration);
        }
    };

    return { showToast };
};