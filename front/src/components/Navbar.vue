<template>
  <nav class="navbar">
    <div class="navbar-logo">
      <Clock/>
    </div>

    <ul class="navbar-links" v-if="isAuthenticated">
      <li>
        <button @click="toggleTheme">{{ themeIcon }}</button>
      </li>
      <li>
        <router-link to="/archives">Управление</router-link>
      </li>
      <li>
        <router-link to="/settings">Настройки</router-link>
      </li>
      <li>
        <router-link to="/logs">Логи</router-link>
      </li>
      <li>
        <button @click="logoutMethod">Выйти</button>
      </li>
    </ul>
  </nav>
</template>

<script setup>
import {useTheme} from '../context/ThemeContext';
import Clock from './Clock.vue';
import {logout} from '@/api/auth';
import router from "@/router/index.js";
import {onMounted, ref, watch} from "vue";
import {useRoute} from "vue-router";

const isAuthenticated = ref(false);
const route = useRoute();

const {state: {isDarkMode}, toggleTheme} = useTheme();
const themeIcon = ref(isDarkMode ? '🌞' : '🌙');

const checkAuthentication = () => {
  const accessToken = localStorage.getItem('access');
  const refreshToken = localStorage.getItem('refresh');
  isAuthenticated.value = !!accessToken && !!refreshToken;
};

watch(
    () => route.path,
    () => {
      checkAuthentication();
    }
);

watch(
    () => isDarkMode,
    (newValue) => {
      themeIcon.value = newValue ? '🌞' : '🌙';
    }
);

onMounted(() => {
  checkAuthentication();
});

const logoutMethod = async () => {
  try {
    const refreshToken = localStorage.getItem('refresh');
    if (refreshToken) {
      await logout(refreshToken);
    }
    localStorage.clear();
    isAuthenticated.value = false;
    await router.push('/login');
  } catch (error) {
    console.error('Ошибка при выходе:', error);
  }
};
</script>

<style scoped>
.navbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 2rem;
  background-color: var(--navbar-background);
  color: var(--navbar-text);
}

.navbar-logo a {
  color: var(--navbar-text);
  text-decoration: none;
  font-size: 1.5rem;
  font-weight: bold;
}

.navbar-links {
  list-style: none;
  display: flex;
  gap: 1rem;
  align-items: center;
}

.navbar-links li a {
  color: var(--navbar-text);
  text-decoration: none;
  font-size: 1rem;
  transition: color 0.3s ease;
}

.navbar-links li a:hover {
  color: var(--secondary-color);
}

.navbar-links li button {
  background: none;
  border: none;
  color: var(--navbar-text);
  font-size: 1rem;
  cursor: pointer;
  transition: color 0.3s ease;
}

.navbar-links li button:hover {
  color: var(--secondary-color);
}

.navbar-links li span {
  font-size: 1rem;
  color: var(--navbar-text);
}

.navbar-links button {
  width: 100%;
  padding: 2px;
  background-color: var(--primary-color);
  color: white;
  border: none;
  border-radius: 5px;
  font-size: 10px;
  cursor: pointer;
  transition: background-color 0.3s ease;
}

.navbar-links button:hover {
  background-color: var(--hover-color);
}

.navbar-links button:disabled {
  background-color: var(--border-color);
  cursor: not-allowed;
}
</style>
