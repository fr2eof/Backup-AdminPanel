<template>
  <span class="clock">{{ time }}</span>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue';

const time = ref(new Date().toLocaleTimeString('ru-RU', { hour: '2-digit', minute: '2-digit', second: '2-digit' }));

const updateTime = () => {
  time.value = new Date().toLocaleTimeString('ru-RU', { hour: '2-digit', minute: '2-digit', second: '2-digit' });
};

onMounted(() => {
  const timerID = setInterval(updateTime, 1000);

  onUnmounted(() => {
    clearInterval(timerID);
  });
});
</script>

<style scoped>
.clock {
  font-size: 1rem;
  color: var(--clock-text);
  background: var(--clock-background);
  padding: 5px 10px;
  border-radius: 5px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
}
</style>
