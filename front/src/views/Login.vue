<template>
  <div class="auth-page">
    <div class="auth-content">
      <h2>Вход</h2>
      <form @submit.prevent="handleSubmit" class="auth-form">
        <input
            type="text"
            placeholder="Логин"
            required
            v-model="username"
            pattern="^[a-zA-Z0-9]{4,20}$"
            title="Логин должен содержать только буквы и цифры и быть длиной от 4 до 20 символов"
        />
        <input
            type="password"
            placeholder="Пароль"
            required
            v-model="password"
            pattern="^(?=.*[A-Za-z])(?=.*\d).{8,}$"
            title="Пароль должен содержать минимум 8 символов, включая хотя бы одну букву и одну цифру"
        />
        <button type="submit">
          {{ "Войти" }}
        </button>
      </form>
      <p>
        Нет акккаунта?
        <RouterLink to="/signup">Зарегистрироваться</RouterLink>
      </p>
      <p>
        Забыли пароль?
        <RouterLink to="/reset-password-request">Восстановить</RouterLink>
      </p>
    </div>
    <Toast/>
  </div>
</template>

<script setup>
import {provide, ref} from 'vue';
import Toast from "@/components/Toast.vue";
import {useRouter} from 'vue-router';
import {login} from '@/api/auth';
import {CONSTANTS} from "@/constants.js";

const username = ref('');
const password = ref('');
const router = useRouter();

const toast = ref({
  message: "",
  type: "info",
  isVisible: false,
});

const showToast = (message, type = "info", duration = CONSTANTS.DEFAULT_TOAST_DURATION) => {
  toast.value.message = message;
  toast.value.type = type;
  toast.value.isVisible = true;

  setTimeout(() => {
    toast.value.message = "";
    toast.value.type = "info";
    toast.value.isVisible = false;
  }, duration);
};


const handleSubmit = async () => {
  const userData = {
    username: username.value,
    password: password.value,
  };

  try {
    const response = await login(userData);
    const {access, refresh} = response;

    localStorage.setItem('access', access);
    localStorage.setItem('refresh', refresh);

    await router.push('/archives');

    showToast('Вход выполнен успешно!', 'success');
  } catch (error) {
    console.log(error);
    showToast('Ошибка при входе', 'error');
  }
};

provide("toast", toast);
provide("showToast", showToast);
</script>

<style scoped>
.auth-page {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background-color: var(--background-color);
}

.auth-content {
  max-width: 400px;
  width: 100%;
  padding: 20px;
  background-color: var(--modal-background);
  border-radius: 10px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  text-align: center;
}

.auth-form {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.form-group {
  width: 100%;
  display: flex;
  justify-content: center;
}

.auth-form input {
  width: 100%;
  padding: 10px;
  border: 1px solid var(--border-color);
  border-radius: 5px;
  font-size: 16px;
  background-color: var(--textfield-background);
  color: var(--textfield-text);
  box-sizing: border-box;
}

.auth-form input:focus {
  border-color: var(--textfield-focus-border);
  outline: none;
}

.auth-form button {
  width: 100%;
  padding: 10px;
  background-color: var(--primary-color);
  color: white;
  border: none;
  border-radius: 5px;
  font-size: 16px;
  cursor: pointer;
  transition: background-color 0.3s ease;
}

.auth-form button:hover {
  background-color: var(--hover-color);
}

.auth-form button:disabled {
  background-color: var(--border-color);
  cursor: not-allowed;
}

.auth-link {
  margin-top: 15px;
  font-size: 14px;
  color: var(--text-color);
}

.auth-link a {
  color: var(--primary-color);
  text-decoration: none;
}

.auth-link a:hover {
  text-decoration: underline;
}
</style>