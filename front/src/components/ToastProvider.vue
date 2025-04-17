<template>
  <slot></slot>
</template>

<script setup>
import { provide, reactive } from 'vue';

const toast = reactive({
  message: '',
  type: 'info',
  isVisible: false,
});

const showToast = (message, type = 'info', duration = 3000) => {
  toast.message = message;
  toast.type = type;
  toast.isVisible = true;

  setTimeout(() => {
    toast.message = '';
    toast.type = 'info';
    toast.isVisible = false;
  }, duration);
};

provide('toast', toast);
provide('showToast', showToast);
</script>
