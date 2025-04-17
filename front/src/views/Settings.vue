<template>
  <html>
  <div class="settings-wrapper">
    <h1>Настройки архивирования</h1>

    <div class="settings-group">
      <h2>Расписание</h2>
      <select v-model="schedule" class="settings-select">
        <option value="daily">Ежедневно</option>
        <option value="weekly">Еженедельно</option>
        <option value="monthly">Ежемесячно</option>
        <option value="yearly">Ежегодно</option>
      </select>
    </div>

    <div class="settings-group">
      <h2>Выбор папки</h2>
      <select v-model="selectedFolder" class="settings-select">
        <option v-for="folder in folders" :key="folder" :value="folder">{{ folder }}</option>
        <option value="new">Новая папка</option>
      </select>
    </div>

    <div v-if="selectedFolder === 'new'" class="settings-group">
      <h2>Название новой папки</h2>
      <input
          v-model="newFolderName"
          type="text"
          placeholder="Введите название новой папки"
          class="settings-input"
          @input="validateNewFolderName"
      />
      <p v-if="newFolderError" class="error-text">{{ newFolderError }}</p>
    </div>

    <div class="settings-group">
      <h2>Объемный порог (GB)</h2>
      <input
          v-model="threshold"
          type="number"
          step="0.01"
          min="0.03"
          @input="validateThreshold"
          placeholder="Объемный порог (GB)"
          class="settings-input"
      />
    </div>

    <button class="settings-button" @click="saveSettings">Сохранить</button>

    <Toast/>
  </div>
  </html>
</template>

<script setup>
import {onMounted, provide, ref} from "vue";
import Toast from "@/components/Toast.vue";
import {getBackupSettings, getFolders, saveBackupSettings} from "@/api/settings.js";
import {CONSTANTS} from "@/constants.js";

const schedule = ref("daily");
const threshold = ref(0.03);
const selectedFolder = ref("");
const newFolderName = ref("");
const folders = ref([]);
const newFolderError = ref("");

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

const loadFolders = async () => {
  try {
    const response = await getFolders(CONSTANTS.FILES_FOLDER);
    folders.value = response.folders;
  } catch (error) {
    showToast("Ошибка загрузки папок с сервера", "error");
    console.error(error);
  }
};

const validateNewFolderName = () => {
  const name = newFolderName.value;
  if (!name || name.length < 3) {
    newFolderError.value = "Имя папки должно содержать минимум 3 символа.";
  } else if (/[^a-zA-Z0-9_-]/.test(name)) {
    newFolderError.value = "Имя папки может содержать только буквы, цифры, дефис и подчеркивание.";
  } else {
    newFolderError.value = "";
  }
};

const validateThreshold = () => {
  if (threshold.value < 0.03) {
    threshold.value = 0.03;
  }
};

const loadSettings = async () => {
  try {
    const settings = await getBackupSettings();
    schedule.value = settings.interval;
    threshold.value = settings.max_size_gb;
    selectedFolder.value = settings.backup_location.split("/").pop();
  } catch (error) {
    console.error(error);
    showToast("Ошибка загрузки настроек", "error");
  }
};

const saveSettings = async () => {
  if (selectedFolder.value === "new") {
    validateNewFolderName();
    if (newFolderError.value) {
      showToast("Пожалуйста, исправьте ошибки в имени папки", "error");
      return;
    }
  }

  const backupLocation = selectedFolder.value === "new" ? newFolderName.value : selectedFolder.value;

  const settings = {
    interval: schedule.value,
    max_size_gb: threshold.value,
    backup_location: `/${backupLocation}`,
  };

  try {
    await saveBackupSettings(settings);
    showToast("Настройки успешно сохранены!", "success");
  } catch (error) {
    console.error(error);
    showToast(error.message, "error");
  }
};

onMounted(() => {
  loadFolders();
  loadSettings();
});

provide("toast", toast);
provide("showToast", showToast);


</script>

<style scoped>
html, body {
  min-height: 100vh;
}

.settings-wrapper {
  max-width: 600px;
  margin: 2rem auto;
  padding: 1.5rem;
  background-color: var(--modal-background);
  color: var(--modal-text);
  border-radius: 8px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

h1 {
  font-size: 1.8rem;
  margin-bottom: 1.5rem;
  text-align: center;
  color: var(--primary-color);
}

.settings-group {
  margin-bottom: 1.5rem;
}

.settings-group h2 {
  font-size: 1.2rem;
  margin-bottom: 0.5rem;
  color: var(--text-color);
}

.settings-input,
.settings-select {
  width: 100%;
  padding: 0.8rem;
  border: 1px solid var(--textfield-border);
  border-radius: 4px;
  background-color: var(--textfield-background);
  color: var(--textfield-text);
  font-size: 1rem;
  outline: none;
  transition: border-color 0.3s;
  box-sizing: border-box;
}

.settings-input:focus,
.settings-select:focus {
  border-color: var(--textfield-focus-border);
}

.error-text {
  color: red;
  font-size: 0.9rem;
  margin-top: 0.3rem;
}

.settings-button {
  width: 100%;
  padding: 0.8rem;
  font-size: 1rem;
  font-weight: bold;
  color: white;
  background-color: var(--primary-color);
  border: none;
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.3s;
}

.settings-button:hover {
  background-color: var(--hover-color);
}
</style>
