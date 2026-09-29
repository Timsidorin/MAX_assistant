<template>
  <el-dialog
    v-model="model"
    fullscreen
    :show-close="false"
    :close-on-click-modal="false"
    class="review-dialog"
  >
    <template #header>
      <header class="review-header">
        <button type="button" class="icon-button" aria-label="Вернуться к камере" @click="model = false">
          <el-icon><ArrowLeft /></el-icon>
        </button>
        <div>
          <strong>Проверьте снимки</strong>
          <span>{{ elements.length }} из 10 добавлено</span>
        </div>
        <div class="header-counter">{{ elements.length }}</div>
      </header>
    </template>

    <main class="review-content">
      <section class="review-intro">
        <div class="intro-icon"><el-icon><Camera /></el-icon></div>
        <div>
          <h1>Достаточно ли хорошо виден дефект?</h1>
          <p>Добавьте общий план и крупный ракурс — так нейросеть точнее оценит опасность.</p>
        </div>
      </section>

      <photo-list
        v-if="elements.length"
        :url-list="urlList"
        :elements="elements"
        @add-more="model = false"
      />

      <section class="quality-checks">
        <div><el-icon><Check /></el-icon><span>Яма находится в фокусе</span></div>
        <div><el-icon><Check /></el-icon><span>Виден масштаб повреждения</span></div>
        <div><el-icon><Location /></el-icon><span>Адрес определим автоматически</span></div>
      </section>
    </main>

    <template #footer>
      <footer class="review-footer">
        <button type="button" class="secondary-button" @click="model = false">Снять ещё</button>
        <button type="button" class="primary-button" :disabled="!canAnalyze || isProcessing" @click="sendMedias">
          <el-icon><MagicStick /></el-icon>
          <span>Найти дефекты</span>
        </button>
      </footer>
    </template>

    <div v-if="isProcessing" class="processing-overlay">
      <div class="processing-card">
        <div class="processing-orbit"><span></span></div>
        <strong>Анализируем дорогу</strong>
        <p>{{ processingMessage }}</p>
        <div class="processing-steps">
          <i :class="{ active: processingStep >= 0 }"></i>
          <i :class="{ active: processingStep >= 1 }"></i>
          <i :class="{ active: processingStep >= 2 }"></i>
        </div>
      </div>
    </div>
  </el-dialog>

  <dialog-processed-media v-if="dataAnswer" :data-answer="dataAnswer" v-model="resultVisible"/>
</template>

<script setup>
import PhotoList from "./PhotoList.vue";
import {computed, nextTick, ref} from "vue";
import {downloadMedias} from "@api/mediaDownload.js";
import {getLocation} from "@helpers/gps.js";
import {ElMessage} from 'element-plus';
import {ArrowLeft, Camera, Check, Location, MagicStick} from "@element-plus/icons-vue";
import DialogProcessedMedia from "./DialogProcessedMedia.vue";

const props = defineProps(["elements"]);
const model = defineModel();
const urlList = computed(() => props.elements.map(element => element.url));
const canAnalyze = computed(() => urlList.value.length > 0 && urlList.value.length <= 10);
const dataAnswer = ref(null);
const resultVisible = ref(false);
const isProcessing = ref(false);
const processingStep = ref(0);
const processingMessage = ref('Получаем координаты участка');
let progressTimer;

function startProgress() {
  const messages = [
    'Получаем координаты участка',
    'Нейросеть ищет повреждения',
    'Оцениваем уровень опасности',
  ];
  processingStep.value = 0;
  processingMessage.value = messages[0];
  progressTimer = setInterval(() => {
    if (processingStep.value < messages.length - 1) {
      processingStep.value += 1;
      processingMessage.value = messages[processingStep.value];
    }
  }, 1400);
}

function stopProgress() {
  clearInterval(progressTimer);
  isProcessing.value = false;
}

function getErrorText(error) {
  const detail = error.response?.data?.detail;
  if (typeof detail === 'string') {
    return detail;
  }
  if (Array.isArray(detail)) {
    return detail[0]?.msg || 'Проверьте отправленные данные';
  }
  return error.message || 'Не удалось обработать изображения';
}

async function sendMedias() {
  if (!canAnalyze.value) {
    return;
  }

  isProcessing.value = true;
  startProgress();

  try {
    const coords = await getLocation();
    if (!coords.status) {
      ElMessage.warning('Геопозиция недоступна — укажите адрес после анализа');
    }

    const urlParams = new URLSearchParams(window.location.search);
    const response = await downloadMedias({
      images_base64: urlList.value,
      user_id: urlParams.get("user_id"),
      latitude: coords.status ? String(coords.data.latitude) : '0',
      longitude: coords.status ? String(coords.data.longitude) : '0',
      filenames: [],
    });
    const successfulResults = response.data.results.filter(result => !result.error && result.image_url);

    if (successfulResults.length === 0) {
      throw new Error(response.data.results.find(result => result.error)?.error || 'Нейросеть не смогла обработать снимки');
    }

    dataAnswer.value = {
      ...response.data,
      results: successfulResults,
      locationUnavailable: !coords.status,
    };

    if (response.data.failed > 0) {
      ElMessage.warning(`Не удалось обработать снимков: ${response.data.failed}`);
    }

    model.value = false;
    await nextTick();
    resultVisible.value = true;
  } catch (error) {
    ElMessage.error(getErrorText(error));
    console.error(error);
  } finally {
    stopProgress();
  }
}
</script>

<style scoped>
.review-header {
  display: grid;
  grid-template-columns: 44px 1fr 44px;
  align-items: center;
  gap: 12px;
}

.review-header > div:nth-child(2) {
  display: flex;
  flex-direction: column;
  gap: 3px;
}

.review-header strong {
  color: #111827;
  font-size: 17px;
}

.review-header span {
  color: #6b7280;
  font-size: 12px;
}

.icon-button,
.header-counter {
  display: grid;
  place-items: center;
  width: 42px;
  height: 42px;
  border: 0;
  border-radius: 14px;
  color: #111827;
  background: #f3f4f6;
  font-size: 19px;
}

.icon-button {
  cursor: pointer;
}

.header-counter {
  color: #1d4ed8;
  background: #eff6ff;
  font-size: 13px;
  font-weight: 800;
}

.review-content {
  display: flex;
  flex-direction: column;
  gap: 20px;
  max-width: 720px;
  margin: 0 auto;
  padding: 2px 0 112px;
}

.review-intro {
  display: flex;
  gap: 14px;
  padding: 16px;
  border-radius: 20px;
  background: #eff6ff;
}

.intro-icon {
  display: grid;
  flex: 0 0 auto;
  place-items: center;
  width: 42px;
  height: 42px;
  border-radius: 14px;
  color: #1d4ed8;
  background: #dbeafe;
  font-size: 20px;
}

.review-intro h1 {
  margin: 0 0 5px;
  color: #111827;
  font-size: 16px;
  line-height: 1.3;
}

.review-intro p {
  margin: 0;
  color: #4b5563;
  font-size: 13px;
  line-height: 1.45;
}

.quality-checks {
  display: grid;
  gap: 11px;
  padding: 2px 4px;
}

.quality-checks div {
  display: flex;
  align-items: center;
  gap: 10px;
  color: #4b5563;
  font-size: 13px;
}

.quality-checks .el-icon {
  color: #16a34a;
  font-size: 17px;
}

.review-footer {
  display: grid;
  grid-template-columns: minmax(110px, 0.7fr) minmax(180px, 1.3fr);
  gap: 10px;
  max-width: 720px;
  margin: 0 auto;
}

.secondary-button,
.primary-button {
  min-height: 52px;
  border: 0;
  border-radius: 16px;
  font: inherit;
  font-size: 14px;
  font-weight: 700;
  cursor: pointer;
}

.secondary-button {
  color: #374151;
  background: #f3f4f6;
}

.primary-button {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  color: #ffffff;
  background: #2563eb;
}

.primary-button:disabled {
  opacity: 0.45;
  cursor: default;
}

.processing-overlay {
  position: fixed;
  inset: 0;
  z-index: 3000;
  display: grid;
  place-items: center;
  padding: 24px;
  background: rgba(3, 7, 18, 0.72);
  backdrop-filter: blur(10px);
}

.processing-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  width: min(100%, 320px);
  padding: 30px 22px 24px;
  border-radius: 24px;
  background: #ffffff;
  text-align: center;
}

.processing-orbit {
  display: grid;
  place-items: center;
  width: 68px;
  height: 68px;
  margin-bottom: 18px;
  border: 2px solid #dbeafe;
  border-top-color: #2563eb;
  border-radius: 50%;
  animation: spin 0.9s linear infinite;
}

.processing-orbit span {
  width: 34px;
  height: 34px;
  border-radius: 12px;
  background: #dbeafe;
}

.processing-card strong {
  color: #111827;
  font-size: 18px;
}

.processing-card p {
  min-height: 20px;
  margin: 8px 0 18px;
  color: #6b7280;
  font-size: 13px;
}

.processing-steps {
  display: flex;
  gap: 6px;
}

.processing-steps i {
  width: 28px;
  height: 4px;
  border-radius: 999px;
  background: #e5e7eb;
  transition: background 200ms ease;
}

.processing-steps i.active {
  background: #2563eb;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

:deep(.review-dialog) {
  background: #ffffff;
}

:deep(.review-dialog .el-dialog__header) {
  position: sticky;
  top: 0;
  z-index: 5;
  margin: 0;
  padding: max(14px, env(safe-area-inset-top)) 16px 12px;
  border-bottom: 1px solid #eef0f3;
  background: rgba(255, 255, 255, 0.94);
  backdrop-filter: blur(14px);
}

:deep(.review-dialog .el-dialog__body) {
  padding: 16px;
}

:deep(.review-dialog .el-dialog__footer) {
  position: fixed;
  right: 0;
  bottom: 0;
  left: 0;
  z-index: 6;
  padding: 12px 16px max(14px, env(safe-area-inset-bottom));
  border-top: 1px solid #eef0f3;
  background: rgba(255, 255, 255, 0.96);
  backdrop-filter: blur(14px);
}
</style>
