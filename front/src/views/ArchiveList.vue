<template>
  <div class="archives-wrapper">
    <h1>Управление файлами</h1>

    <div class="controls">
      <select v-model="selectedFolder" @change="loadFilesMethod">
        <option disabled value="">Выберите папку</option>
        <option v-for="folder in folders" :key="folder" :value="folder">{{ folder }}</option>
      </select>

      <input type="file" @change="onFileChange"/>

      <button @click="uploadFileMethod" :disabled="!selectedFile">Загрузить файл</button>

      <button @click="confirmDeleteAll">Удалить все</button>
    </div>

    <div class="verification-section">
      <h2>Проверка файла</h2>
      <input type="file" @change="onVerifyFileChange"/>
      <button @click="verifyFileMethod" :disabled="!verifyFile">
        Проверить файл
      </button>
    </div>

    <div class="search-bar">
      <input
          v-model="searchQuery"
          placeholder="Поиск файлов"
          class="search-input"
      />
      <div class="backup-controls">
        <button @click="executeBackup">Запустить ручной бэкап</button>
      </div>

    </div>


    <table class="archives-table">
      <thead>
      <tr>
        <th>ID</th>
        <th>Название</th>
        <th>Дата</th>
        <th>Время</th>
        <th>Место</th>
        <th>Действия</th>
      </tr>
      </thead>
      <tbody>
      <tr v-for="file in paginatedFiles" :key="file.ID">
        <td>{{ file.ID }}</td>
        <td>{{ file.Название }}</td>
        <td>{{ formatDate(file.Дата) }}</td>
        <td>{{ formatTime(file.Дата) }}</td>
        <td>{{ formatPath(file.Место) }}</td>
        <td>
          <button @click="downloadFileMethod(file.Место, file.Название)">
            Скачать
          </button>
          <button @click="deleteFileMethod(file.Место, file.Название)">
            Удалить
          </button>
        </td>
      </tr>
      </tbody>
    </table>

    <div class="pagination">
      <button :disabled="currentPage === 1" @click="changePage(currentPage - 1)">
        Предыдущая
      </button>
      <span>{{ currentPage }} / {{ totalPages }}</span>
      <button :disabled="currentPage === totalPages" @click="changePage(currentPage + 1)">
        Следующая
      </button>
    </div>

    <Toast/>
  </div>
</template>

<script setup>
import {ref, computed, provide, onMounted} from "vue";
import Toast from "@/components/Toast.vue";
import {
  fetchFiles,
  deleteFile,
  deleteAllFiles,
  downloadFile,
  uploadFile,
  verifyFileMet
} from "@/api/files";
import {executeManualBackup} from "@/api/manual.js";
import {getFolders} from "@/api/settings.js";
import {CONSTANTS} from "@/constants.js";

const files = ref([]);
const searchQuery = ref("");
const currentPage = ref(CONSTANTS.DEFAULT_CURRENT_PAGE);
const itemsPerPage = ref(CONSTANTS.DEFAULT_PAGE_SIZE);
const selectedFolder = ref("");
const folders = ref([]);
const selectedFile = ref(null);
const verifyFile = ref(null);

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
    console.error(error);
    showToast("Ошибка загрузки папок с сервера", "error");
  }
};

const loadFilesMethod = async () => {
  if (!selectedFolder.value) return;
  const folderPath = selectedFolder.value;
  try {
    const data = await fetchFiles(folderPath);

    let sortedFiles = data.sort((a, b) => {
      const dateA = new Date(a.Дата * 1000);
      const dateB = new Date(b.Дата * 1000);

      if (dateA > dateB) return -1;
      if (dateA < dateB) return 1;

      return 0;
    });

    sortedFiles = sortedFiles.map((file, index) => {
      file.ID = sortedFiles.length - index;
      return file;
    });

    files.value = sortedFiles;
  } catch (error) {
    console.error(error);
    showToast('Ошибка загрузки файлов', 'error');
  }
};

const onFileChange = (event) => {
  selectedFile.value = event.target.files[0];
};
const onVerifyFileChange = (event) => {
  verifyFile.value = event.target.files[0];
};

const executeBackup = async () => {
  try {
    const message = await executeManualBackup();
    showToast(message, "success");
  } catch (error) {
    console.error(error);
    showToast(error.message, "error");
  }
  await loadFilesMethod();
};


const downloadFileMethod = async (folderPath, fileName) => {
  try {
    await downloadFile(folderPath, fileName);
    showToast("Файл успешно скачан", "success");
  } catch (error) {
    console.error(error);
    showToast("Ошибка при скачивании файла", "error");
  }
};
const deleteFileMethod = async (folderPath, fileName) => {
  try {
    await deleteFile(folderPath, fileName);
    showToast("Файл успешно удален", "success");
    await loadFilesMethod();
  } catch (error) {
    console.error(error);
    showToast("Ошибка при удалении файла", "error");
  }
};
const uploadFileMethod = async () => {
  if (!selectedFile.value || !selectedFolder.value) {
    showToast("Выберите файл и папку для загрузки", "error");
    return;
  }
  try {
    await uploadFile(selectedFolder.value, selectedFile.value);
    showToast("Файл успешно загружен", "success");
    selectedFile.value = null;
    await loadFilesMethod();
  } catch (error) {
    console.error(error);
    showToast("Ошибка при загрузке файла", "error");
  }
};
const confirmDeleteAll = () => {
  if (!selectedFolder.value) {
    showToast("Выберите папку для удаления файлов", "error");
    return;
  }
  if (confirm("Вы уверены, что хотите удалить все файлы?")) {
    deleteAllFilesMethod();
  }
};
const deleteAllFilesMethod = async () => {
  try {
    await deleteAllFiles(selectedFolder.value);
    showToast("Все файлы удалены", "success");
    await loadFilesMethod();
  } catch (error) {
    console.error(error);
    showToast("Ошибка при удалении файлов", "error");
  }
};
const verifyFileMethod = async () => {
  if (!verifyFile.value) {
    showToast("Выберите файл для проверки", "error");
    return;
  }

  try {
    const message = await verifyFileMet(verifyFile.value);
    showToast(message, "warning");
  } catch (error) {
    console.error(error);
    showToast(error.message, "error");
  }
};

const filteredFiles = computed(() =>
    files.value.filter((file) =>
        file.Название.toLowerCase().includes(searchQuery.value.toLowerCase())
    )
);

const paginatedFiles = computed(() => {
  const startIndex = (currentPage.value - 1) * itemsPerPage.value;
  const endIndex = startIndex + itemsPerPage.value;
  return filteredFiles.value.slice(startIndex, endIndex);
});

const totalPages = computed(() =>
    Math.ceil(filteredFiles.value.length / itemsPerPage.value)
);

const changePage = (newPage) => {
  if (newPage >= 1 && newPage <= totalPages.value) {
    currentPage.value = newPage;
  }
};

const formatDate = (dateString) =>
    new Date(dateString * 1000).toLocaleDateString("ru-RU");

const formatTime = (dateString) =>
    new Date(dateString * 1000).toLocaleTimeString("ru-RU", {hour12: false});

const formatPath = (path) => path.replace(/^backup\//, "");

onMounted(() => {
  loadFolders();
  loadFilesMethod();
});

provide("toast", toast);
provide("showToast", showToast);
</script>

<style scoped>
.archives-wrapper {
  min-height: 100vh;
  max-width: 900px;
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

.controls {
  display: flex;
  gap: 1rem;
  justify-content: center;
  flex-wrap: wrap;
}

select, input[type="file"], button {
  padding: 0.8rem;
  font-size: 1rem;
  border-radius: 4px;
  border: 1px solid var(--border-color);
}

select {
  width: 180px;
}

input[type="file"] {
  width: auto;
  background-color: var(--textfield-background);
  color: var(--textfield-text);
}

button {
  cursor: pointer;
  background-color: var(--button-background);
  color: var(--button-text);
  transition: background-color 0.3s ease;
  padding: 0.8rem 1.2rem;
}

button:hover {
  background-color: var(--hover-color);
}

.search-bar {
  margin-bottom: 1.5rem;
  display: flex;
  justify-content: center;
}

.search-input {
  width: 300px;
  margin-right: 1rem;
  padding: 0.8rem;
  border: 1px solid var(--textfield-border);
  border-radius: 4px;
  background-color: var(--textfield-background);
  color: var(--textfield-text);
  font-size: 1rem;
  outline: none;
  transition: border-color 0.3s;
}

.search-input:focus {
  border-color: var(--textfield-focus-border);
}

.archives-table {
  width: 100%;
  border-collapse: collapse;
}

.archives-table th,
.archives-table td {
  border: 1px solid var(--border-color);
  padding: 0.8rem;
  text-align: left;
}

.archives-table th {
  background-color: var(--navbar-background);
  color: var(--navbar-text);
}

.archives-table tr:nth-child(even) {
  background-color: var(--clicker-background-color);
}

.archives-table tr:hover {
  background-color: var(--hover-color);
}

.archives-table td {
  color: var(--text-color);
}

.pagination {
  display: flex;
  justify-content: center;
  margin-top: 1rem;
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

.verification-section {
  padding: 1rem;
  background-color: var(--modal-background);
  border-radius: 8px;
  text-align: center;
}

.verification-section button {
  margin-left: 1rem;
}
</style>
