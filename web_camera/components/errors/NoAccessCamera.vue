<template>
  <div class="camera-error">
    <div class="camera-error__icon">!</div>
    <h1>Нет доступа к камере</h1>
    <p>{{ message }}</p>
    <button type="button" @click="$emit('retry')">Попробовать снова</button>
  </div>
</template>

<script setup>
defineProps({
  message: {
    type: String,
    default: 'Разрешите доступ к камере в настройках браузера и повторите попытку.'
  }
});

defineEmits(['retry']);
</script>

<style scoped>
.camera-error {
  position: absolute;
  inset: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 28px;
  color: white;
  text-align: center;
  background: #111827;
}

.camera-error__icon {
  display: grid;
  place-items: center;
  width: 56px;
  height: 56px;
  margin-bottom: 8px;
  border: 2px solid #f87171;
  border-radius: 50%;
  color: #f87171;
  font-size: 32px;
  font-weight: 700;
}

.camera-error h1 {
  margin: 8px 0;
  font-size: 22px;
}

.camera-error p {
  max-width: 360px;
  margin: 0 0 20px;
  color: #cbd5e1;
  line-height: 1.5;
}

.camera-error button {
  padding: 12px 20px;
  border: 0;
  border-radius: 12px;
  color: white;
  background: #2563eb;
  font: inherit;
  font-weight: 600;
  cursor: pointer;
}
</style>