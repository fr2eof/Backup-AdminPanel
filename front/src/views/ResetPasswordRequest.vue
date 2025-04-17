<template>
  <div class="reset-password-wrapper">
    <h1>Восстановление пароля</h1>
    <form @submit.prevent="sendResetEmail" class="reset-password-form">
      <div class="form-group">
        <label for="email">Введите ваш email:</label>
        <input v-model="email" type="email" id="email" required class="reset-input"/>
      </div>
      <button type="submit" class="reset-button">Отправить письмо для восстановления</button>
    </form>
    <button @click="goBack" class="back-button">Назад</button>
  </div>
  <Toast/>

</template>

<script setup>
import {provide, ref} from 'vue';
import Toast from "@/components/Toast.vue";
import {CONSTANTS} from "@/constants.js";
import {requestPasswordReset} from "@/api/auth.js";
import router from "@/router/index.js";

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

const email = ref('');

const sendResetEmail = async () => {
  try {
    const response = await requestPasswordReset(email.value);
    showToast('Письмо для восстановления пароля отправлено!', 'success');
    await router.push('/login');

  } catch (error) {
    console.log(error);
    showToast('Произошла ошибка при отправке письма.', 'error');
  }
};
const goBack = () => {
  router.go(-1);
};

provide('toast', toast);
provide('showToast', showToast);
</script>

<style scoped>
.reset-password-wrapper {
  padding: 2rem;
  background-color: var(--background-color);
  color: var(--text-color);
  max-width: 500px;
  margin: auto;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

h1 {
  font-size: 1.8rem;
  margin-bottom: 1.5rem;
  text-align: center;
  color: var(--primary-color);
}

.reset-password-form {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.form-group {
  margin-bottom: 1rem;
}

label {
  font-size: 1.2rem;
  color: var(--text-color);
}

.reset-input {
  padding: 0.8rem;
  border: 1px solid var(--textfield-border);
  border-radius: 4px;
  background-color: var(--textfield-background);
  color: var(--textfield-text);
  font-size: 1rem;
  outline: none;
}

.reset-input:focus {
  border-color: var(--textfield-focus-border);
}

.reset-button {
  padding: 0.8rem;
  border: none;
  background-color: var(--primary-color);
  color: white;
  font-weight: bold;
  font-size: 1.2rem;
  cursor: pointer;
  border-radius: 4px;
}

.reset-button:hover {
  background-color: var(--hover-color);
}

.back-button {
  margin-top: 1rem;
  padding: 0.8rem;
  border: none;
  background-color: var(--primary-color);
  color: white;
  font-weight: bold;
  font-size: 1rem;
  cursor: pointer;
  border-radius: 4px;
  width: 20%;
}

.back-button:hover {
  background-color: var(--textfield-focus-border);
}
</style>
