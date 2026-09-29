<template>
  <button
    type="button"
    class="shutter"
    :disabled="disabled"
    aria-label="Сделать снимок"
    @click="$emit('take-photo')"
  >
    <span></span>
  </button>
</template>

<script setup>
defineProps({
  disabled: Boolean,
});

defineEmits(['take-photo']);
</script>

<style scoped>
.shutter {
  position: relative;
  display: grid;
  place-items: center;
  width: 78px;
  height: 78px;
  margin: 0 auto;
  padding: 0;
  border: 3px solid rgba(255, 255, 255, 0.92);
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.16);
  cursor: pointer;
  transition: transform 120ms ease, opacity 120ms ease;
  -webkit-tap-highlight-color: transparent;
}

.shutter span {
  width: 62px;
  height: 62px;
  border-radius: 50%;
  background: #ffffff;
  transition: transform 120ms ease;
}

.shutter:active:not(:disabled) {
  transform: scale(0.94);
}

.shutter:active:not(:disabled) span {
  transform: scale(0.88);
}

.shutter:disabled {
  opacity: 0.42;
  cursor: default;
}
</style>
