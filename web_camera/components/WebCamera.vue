<template>
  <main class="scanner-shell">
    <camera-preview ref="camera" @access-change="cameraReady = $event"/>
    <div class="scanner-shade"></div>

    <header class="scanner-header">
      <div class="brand-mark">Я</div>
      <div class="brand-copy">
        <strong>Ямоборец</strong>
        <span><i :class="['status-dot', { active: cameraReady }]"></i>{{ cameraReady ? 'Камера готова' : 'Подключение камеры' }}</span>
      </div>
      <div class="photo-limit">{{ mediaStore.length }}/10</div>
    </header>

    <section v-if="cameraReady" class="capture-guide" aria-hidden="true">
      <div class="guide-corner guide-corner--top-left"></div>
      <div class="guide-corner guide-corner--top-right"></div>
      <div class="guide-corner guide-corner--bottom-left"></div>
      <div class="guide-corner guide-corner--bottom-right"></div>
      <span>Расположите дефект внутри рамки</span>
    </section>

    <div v-if="showCaptureFeedback" class="capture-feedback">Снимок добавлен</div>

    <footer v-if="cameraReady" class="scanner-controls">
      <p class="capture-hint">Снимите общий план и крупный ракурс</p>
      <div class="control-row">
        <media-store
          :elements="mediaStore"
          aria-label="Открыть выбранные снимки"
          @click="openPreview"
        />
        <photo-button
          :disabled="mediaStore.length >= 10"
          @take-photo="takePhoto"
        />
        <button
          type="button"
          class="analyze-button"
          :disabled="mediaStore.length === 0"
          aria-label="Перейти к анализу"
          @click="openPreview"
        >
          <el-icon><ArrowRight /></el-icon>
          <span>Анализ</span>
        </button>
      </div>
    </footer>

    <dialog-preview :elements="mediaStore" v-model="dialogVisible"/>
  </main>
</template>

<script setup>
import {ref, provide} from "vue";
import {ArrowRight} from "@element-plus/icons-vue";
import {ElMessage} from "element-plus";
import DialogPreview from "./send-request-components/DialogPreview.vue";
import PhotoButton from "./camera-components/PhotoButton.vue";
import CameraPreview from "./camera-components/CameraPreview.vue";
import MediaStore from "./camera-components/MediaStore.vue";

const dialogVisible = ref(false);
const camera = ref(null);
const cameraReady = ref(false);
const mediaStore = ref([]);
const showCaptureFeedback = ref(false);
let feedbackTimer;

function takePhoto() {
  if (!cameraReady.value || mediaStore.value.length >= 10) {
    return;
  }

  try {
    const newPhoto = camera.value.capturePhoto();
    mediaStore.value.push({
      id: crypto.randomUUID?.() ?? `${Date.now()}-${mediaStore.value.length}`,
      url: newPhoto,
    });
    showCaptureFeedback.value = true;
    clearTimeout(feedbackTimer);
    feedbackTimer = setTimeout(() => {
      showCaptureFeedback.value = false;
    }, 1100);
  } catch (error) {
    ElMessage.error('Камера ещё не готова. Попробуйте ещё раз.');
    console.error(error);
  }
}

function openPreview() {
  if (mediaStore.value.length > 0) {
    dialogVisible.value = true;
  }
}

function deleteElement(id) {
  mediaStore.value = mediaStore.value.filter(element => element.id !== id);
}

provide('deleteElement', deleteElement);
</script>

<style scoped>
.scanner-shell {
  position: fixed;
  inset: 0;
  overflow: hidden;
  color: #ffffff;
  background: #0b1220;
}

.scanner-shade {
  position: fixed;
  inset: 0;
  z-index: 2;
  pointer-events: none;
  background: linear-gradient(180deg, rgba(3, 7, 18, 0.72) 0%, transparent 30%, transparent 55%, rgba(3, 7, 18, 0.88) 100%);
}

.scanner-header {
  position: fixed;
  top: 0;
  right: 0;
  left: 0;
  z-index: 12;
  display: flex;
  align-items: center;
  gap: 11px;
  padding: max(18px, env(safe-area-inset-top)) 18px 14px;
}

.brand-mark {
  display: grid;
  place-items: center;
  width: 42px;
  height: 42px;
  border-radius: 14px;
  color: #111827;
  background: #ffffff;
  font-size: 20px;
  font-weight: 800;
}

.brand-copy {
  display: flex;
  flex: 1;
  flex-direction: column;
  gap: 3px;
}

.brand-copy strong {
  font-size: 16px;
  letter-spacing: -0.01em;
}

.brand-copy span {
  display: flex;
  align-items: center;
  gap: 6px;
  color: #d1d5db;
  font-size: 12px;
}

.status-dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: #f59e0b;
}

.status-dot.active {
  background: #22c55e;
}

.photo-limit {
  min-width: 42px;
  padding: 8px 10px;
  border: 1px solid rgba(255, 255, 255, 0.18);
  border-radius: 12px;
  text-align: center;
  background: rgba(15, 23, 42, 0.52);
  backdrop-filter: blur(12px);
  font-size: 13px;
  font-weight: 700;
}

.capture-guide {
  position: fixed;
  top: 25%;
  right: 11%;
  bottom: 31%;
  left: 11%;
  z-index: 5;
  pointer-events: none;
}

.capture-guide > span {
  position: absolute;
  bottom: -38px;
  left: 50%;
  padding: 8px 12px;
  border-radius: 999px;
  color: #f3f4f6;
  background: rgba(15, 23, 42, 0.64);
  backdrop-filter: blur(10px);
  font-size: 12px;
  white-space: nowrap;
  transform: translateX(-50%);
}

.guide-corner {
  position: absolute;
  width: 34px;
  height: 34px;
  border-color: rgba(255, 255, 255, 0.92);
  border-style: solid;
}

.guide-corner--top-left {
  top: 0;
  left: 0;
  border-width: 2px 0 0 2px;
  border-radius: 14px 0 0;
}

.guide-corner--top-right {
  top: 0;
  right: 0;
  border-width: 2px 2px 0 0;
  border-radius: 0 14px 0 0;
}

.guide-corner--bottom-left {
  bottom: 0;
  left: 0;
  border-width: 0 0 2px 2px;
  border-radius: 0 0 0 14px;
}

.guide-corner--bottom-right {
  right: 0;
  bottom: 0;
  border-width: 0 2px 2px 0;
  border-radius: 0 0 14px;
}

.capture-feedback {
  position: fixed;
  top: 18%;
  left: 50%;
  z-index: 20;
  padding: 10px 16px;
  border-radius: 999px;
  color: #052e16;
  background: #dcfce7;
  font-size: 13px;
  font-weight: 700;
  transform: translateX(-50%);
  animation: feedback 1.1s ease both;
}

.scanner-controls {
  position: fixed;
  right: 0;
  bottom: 0;
  left: 0;
  z-index: 12;
  padding: 12px 18px max(22px, env(safe-area-inset-bottom));
}

.capture-hint {
  margin: 0 0 14px;
  color: #d1d5db;
  text-align: center;
  font-size: 13px;
}

.control-row {
  display: grid;
  grid-template-columns: 76px 1fr 76px;
  align-items: center;
  min-height: 82px;
}

.analyze-button {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 5px;
  padding: 0;
  border: 0;
  color: #ffffff;
  background: transparent;
  font: inherit;
  font-size: 12px;
  font-weight: 600;
  cursor: pointer;
}

.analyze-button .el-icon {
  display: grid;
  place-items: center;
  width: 48px;
  height: 48px;
  border-radius: 16px;
  color: #111827;
  background: #ffffff;
  font-size: 21px;
}

.analyze-button:disabled {
  opacity: 0.36;
  cursor: default;
}

@keyframes feedback {
  0% { opacity: 0; transform: translate(-50%, 8px); }
  20%, 75% { opacity: 1; transform: translate(-50%, 0); }
  100% { opacity: 0; transform: translate(-50%, -6px); }
}
</style>
