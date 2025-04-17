<template>
  <div class="logs-wrapper">
    <h1 class="logs-title">Логи операций</h1>
    <div class="filters">
      <input
          v-model="filter.date"
          type="date"
          class="filter-input"
      />
      <input
          v-model="filter.operation"
          placeholder="Операция"
          class="filter-input"
      />
      <input
          v-model="filter.file"
          placeholder="Файл"
          class="filter-input"
      />
    </div>
    <div v-if="isLoading" class="loading">Загрузка...</div>
    <table v-else class="logs-table">
      <thead>
      <tr>
        <th>ID</th>
        <th>Дата</th>
        <th>Время</th>
        <th>Операция</th>
        <th>Файл</th>
      </tr>
      </thead>
      <tbody>
      <tr v-for="log in paginatedLogs" :key="log.id">
        <td>{{ log.id }}</td>
        <td>{{ log.date }}</td>
        <td>{{ log.time }}</td>
        <td>{{ log.operation }}</td>
        <td>{{ log.file }}</td>
      </tr>
      </tbody>
    </table>
    <p v-if="!isLoading && filteredLogs.length === 0" class="no-logs">
      Нет данных для отображения.
    </p>

    <!-- Пагинация -->
    <div class="pagination" v-if="filteredLogs.length > itemsPerPage">
      <button @click="changePage(currentPage - 1)" :disabled="currentPage === 1">Предыдущая</button>
      <span>{{ currentPage }} / {{ totalPages }}</span>
      <button @click="changePage(currentPage + 1)" :disabled="currentPage === totalPages">Следующая</button>
    </div>

    <Toast />
  </div>
</template>

<script setup>
import {ref, computed, provide} from 'vue';
import {fetchLogs} from '@/api/logs';
import Toast from "@/components/Toast.vue";
import {CONSTANTS} from "@/constants.js";

const logs = ref([]);
const filter = ref({
  operation: '',
  file: '',
  date: '',
});
const isLoading = ref(false);
const currentPage = ref(1);
const itemsPerPage = ref(10);

const toast = ref({
  message: '',
  type: 'info',
  isVisible: false,
});

const showToast = (message, type = 'info', duration = CONSTANTS.DEFAULT_TOAST_DURATION) => {
  toast.value.message = message;
  toast.value.type = type;
  toast.value.isVisible = true;

  setTimeout(() => {
    toast.value.message = '';
    toast.value.type = 'info';
    toast.value.isVisible = false;
  }, duration);
};

const parseLogs = (apiLogs) => {
  return apiLogs.map((log) => {
    const [operation, file] = log.operation.split(': ').map(str => str.trim());
    const [date, time] = log.date.split('T');
    return {
      id: log.id,
      date,
      time: time.slice(0, 8),
      operation,
      file: file || '—',
    };
  });
};

const filteredLogs = computed(() => {
  return logs.value.filter(log => {
    return (
        log.operation.toLowerCase().includes(filter.value.operation.toLowerCase()) &&
        log.file.toLowerCase().includes(filter.value.file.toLowerCase()) &&
        (!filter.value.date || log.date === filter.value.date)
    );
  });
});

const paginatedLogs = computed(() => {
  const startIndex = (currentPage.value - 1) * itemsPerPage.value;
  const endIndex = startIndex + itemsPerPage.value;
  return filteredLogs.value.slice(startIndex, endIndex);
});

const totalPages = computed(() => {
  return Math.ceil(filteredLogs.value.length / itemsPerPage.value);
});

const changePage = (newPage) => {
  if (newPage >= 1 && newPage <= totalPages.value) {
    currentPage.value = newPage;
  }
};

const getLogs = async () => {
  isLoading.value = true;
  try {
    const apiLogs = await fetchLogs();
    logs.value = parseLogs(apiLogs);
  } catch (error) {
    console.error(error);
    showToast(error.message || 'Ошибка загрузки логов.', 'error');
  } finally {
    isLoading.value = false;
  }
};

provide('toast', toast);
provide('showToast', showToast);

getLogs();
</script>

<style scoped>
.logs-wrapper {
  min-height: 100vh;
  padding: 2rem;
  background-color: var(--background-color);
  color: var(--text-color);
}

.logs-title {
  font-size: 2rem;
  margin-bottom: 1.5rem;
  text-align: center;
  color: var(--primary-color);
}

.filters {
  display: flex;
  gap: 1rem;
  margin-bottom: 1.5rem;
  justify-content: center;
}

.filter-input {
  padding: 0.8rem;
  border: 1px solid var(--textfield-border);
  border-radius: 4px;
  background-color: var(--textfield-background);
  color: var(--textfield-text);
  font-size: 1rem;
  outline: none;
  transition: border-color 0.3s;
  width: 200px;
}

.filter-input:focus {
  border-color: var(--textfield-focus-border);
}

.loading {
  text-align: center;
  font-size: 1.2rem;
  color: var(--primary-color);
}

.no-logs {
  text-align: center;
  font-size: 1.2rem;
  color: var(--text-color);
  margin-top: 1.5rem;
}

.logs-table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 1.5rem;
}

.logs-table th,
.logs-table td {
  border: 1px solid var(--border-color);
  padding: 0.8rem;
  text-align: left;
}

.logs-table th {
  background-color: var(--navbar-background);
  color: var(--navbar-text);
}

.logs-table tr:nth-child(even) {
  background-color: var(--clicker-background-color);
}

.logs-table tr:hover {
  background-color: var(--hover-color);
  color: var(--text-color);
}

.logs-table td {
  color: var(--text-color);
}

.pagination {
  display: flex;
  justify-content: center;
  margin-top: 1.5rem;
}

.pagination button {
  padding: 0.5rem 1rem;
  border: 1px solid var(--border-color);
  background-color: var(--button-background);
  cursor: pointer;
  margin: 0 0.5rem;
  border-radius: 4px;
}

.pagination button:disabled {
  cursor: not-allowed;
  opacity: 0.5;
}
</style>
