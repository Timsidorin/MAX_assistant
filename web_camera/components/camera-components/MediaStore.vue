<template>
  <button type="button" class="media-store" :disabled="elements.length === 0">
    <img v-if="elements.length" :src="elements.at(-1).url" alt="Последний снимок">
    <el-icon v-else><Picture /></el-icon>
    <span v-if="elements.length" class="media-count">{{ elements.length }}</span>
    <small>{{ elements.length ? 'Снимки' : 'Галерея' }}</small>
  </button>
</template>

<script setup>
import {Picture} from "@element-plus/icons-vue";

defineProps({
  elements: {
    type: Array,
    default: () => [],
  },
});
</script>

<style scoped>
.media-store {
  position: relative;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 5px;
  width: 64px;
  padding: 0;
  border: 0;
  color: #ffffff;
  background: transparent;
  font: inherit;
  cursor: pointer;
}

.media-store img,
.media-store > .el-icon {
  width: 48px;
  height: 48px;
  border: 2px solid rgba(255, 255, 255, 0.75);
  border-radius: 16px;
  object-fit: cover;
  background: rgba(15, 23, 42, 0.52);
}

.media-store > .el-icon {
  display: grid;
  place-items: center;
  box-sizing: border-box;
  font-size: 21px;
}

.media-store small {
  font-size: 12px;
  font-weight: 600;
}

.media-store:disabled {
  opacity: 0.42;
  cursor: default;
}

.media-count {
  position: absolute;
  top: -6px;
  right: 0;
  display: grid;
  place-items: center;
  min-width: 20px;
  height: 20px;
  padding: 0 4px;
  border: 2px solid #111827;
  border-radius: 999px;
  color: #ffffff;
  background: #2563eb;
  box-sizing: border-box;
  font-size: 11px;
  font-weight: 800;
}
</style>
