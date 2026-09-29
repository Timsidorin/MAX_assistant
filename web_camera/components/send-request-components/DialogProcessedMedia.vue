<template>
  <el-dialog
    v-model="model"
    fullscreen
    :show-close="false"
    :close-on-click-modal="false"
    class="result-dialog"
  >
    <template #header>
      <header class="result-header">
        <button type="button" class="close-button" aria-label="Закрыть результат" @click="model = false">
          <el-icon><Close /></el-icon>
        </button>
        <div>
          <strong>Результат анализа</strong>
          <span>Нейросеть завершила проверку</span>
        </div>
        <div class="ready-mark"><el-icon><Check /></el-icon></div>
      </header>
    </template>

    <main class="result-content">
      <section :class="['result-hero', `result-hero--${riskLevel.tone}`]">
        <div class="risk-ring">
          <strong>{{ Math.round(summary.max_risk) }}%</strong>
          <span>риск</span>
        </div>
        <div class="risk-copy">
          <span>Оценка участка</span>
          <h1>{{ riskLevel.label }}</h1>
          <p>Обнаружено дефектов: {{ summary.total_potholes }}</p>
        </div>
      </section>

      <section :class="['address-card', { 'address-card--manual': needsManualAddress }]">
        <div class="address-icon"><el-icon><Location /></el-icon></div>
        <div class="address-content">
          <span>{{ needsManualAddress ? 'Укажите адрес вручную' : 'Определённый адрес' }}</span>
          <input
            v-if="needsManualAddress"
            v-model.trim="manualAddress"
            type="text"
            inputmode="text"
            autocomplete="street-address"
            placeholder="Город, улица, дом"
            aria-label="Адрес дорожного дефекта"
          >
          <strong v-else>{{ dataAnswer.address }}</strong>
          <small v-if="needsManualAddress">На iPhone геопозиция может быть недоступна внутри MAX</small>
        </div>
      </section>

      <section class="section-block">
        <div class="section-heading">
          <div>
            <span>Классификация</span>
            <h2>Уровни опасности</h2>
          </div>
          <small>{{ summary.total_potholes }} всего</small>
        </div>
        <div class="severity-grid">
          <div class="severity severity--critical"><strong>{{ summary.detections.CRITICAL }}</strong><span>Критических</span></div>
          <div class="severity severity--high"><strong>{{ summary.detections.HIGH }}</strong><span>Высоких</span></div>
          <div class="severity severity--medium"><strong>{{ summary.detections.MEDIUM }}</strong><span>Средних</span></div>
          <div class="severity severity--low"><strong>{{ summary.detections.LOW }}</strong><span>Низких</span></div>
        </div>
      </section>

      <section class="section-block">
        <div class="section-heading">
          <div>
            <span>Размеченные кадры</span>
            <h2>Что обнаружила модель</h2>
          </div>
          <small>{{ photos.length }} фото</small>
        </div>
        <div class="processed-grid">
          <article v-for="(element, index) in photos" :key="element.filename" class="processed-card">
            <el-image
              :src="element.image_url"
              :preview-src-list="urlList"
              :initial-index="index"
              fit="cover"
              preview-teleported
            />
            <div class="processed-meta">
              <span>Кадр {{ index + 1 }}</span>
              <strong>{{ element.total_potholes }} деф. · {{ Math.round(element.max_risk) }}%</strong>
            </div>
          </article>
        </div>
      </section>

      <section class="next-step">
        <div class="next-step__number">1</div>
        <div><strong>Мы уже подготовили данные</strong><span>Адрес, фотографии и оценка риска попадут в заявление автоматически.</span></div>
      </section>
    </main>

    <template #footer>
      <footer class="result-footer">
        <div class="footer-copy">
          <span>Следующий шаг</span>
          <strong>Проверить и отправить заявление</strong>
        </div>
        <button type="button" class="report-button" :disabled="isCreating" @click="handleSendReport">
          <span>{{ isCreating ? 'Создаём…' : 'Продолжить' }}</span>
          <el-icon v-if="!isCreating"><ArrowRight /></el-icon>
          <i v-else class="button-spinner"></i>
        </button>
      </footer>
    </template>
  </el-dialog>
</template>

<script setup>
import {computed, ref} from "vue";
import {ArrowRight, Check, Close, Location} from "@element-plus/icons-vue";
import {ElMessage} from "element-plus";
import {sendReport} from "@api/report.js";

const model = defineModel();
const props = defineProps({
  dataAnswer: Object,
});
const isCreating = ref(false);
const manualAddress = ref(props.dataAnswer.address || '');
const needsManualAddress = computed(() => props.dataAnswer.locationUnavailable || !props.dataAnswer.address);
const photos = computed(() => props.dataAnswer.results.filter(element => !element.error && element.image_url));
const urlList = computed(() => photos.value.map(element => element.image_url));
const summary = computed(() => {
  const result = {
    average_risk: 0,
    max_risk: 0,
    total_potholes: 0,
    detections: {CRITICAL: 0, HIGH: 0, MEDIUM: 0, LOW: 0},
  };

  photos.value.forEach(element => {
    result.average_risk += element.average_risk;
    result.max_risk = Math.max(result.max_risk, element.max_risk);
    result.total_potholes += element.total_potholes;
    result.detections.CRITICAL += element.detections.CRITICAL;
    result.detections.HIGH += element.detections.HIGH;
    result.detections.MEDIUM += element.detections.MEDIUM;
    result.detections.LOW += element.detections.LOW;
  });
  result.average_risk = photos.value.length ? result.average_risk / photos.value.length : 0;
  return result;
});
const riskLevel = computed(() => {
  if (summary.value.max_risk > 70) return {label: 'Критическая опасность', tone: 'critical'};
  if (summary.value.max_risk > 50) return {label: 'Высокая опасность', tone: 'high'};
  if (summary.value.max_risk > 30) return {label: 'Средняя опасность', tone: 'medium'};
  return {label: 'Низкая опасность', tone: 'low'};
});

function getErrorText(error) {
  const detail = error.response?.data?.detail;
  if (typeof detail === 'string') return detail;
  if (Array.isArray(detail)) return detail[0]?.msg || 'Проверьте данные заявления';
  return 'Не удалось сформировать заявление';
}

async function handleSendReport() {
  if (needsManualAddress.value && manualAddress.value.length < 5) {
    ElMessage.warning('Укажите город, улицу и дом');
    return;
  }

  isCreating.value = true;
  try {
    const response = await sendReport({
      user_id: props.dataAnswer.user_id,
      latitude: props.dataAnswer.latitude,
      longitude: props.dataAnswer.longitude,
      address: needsManualAddress.value ? manualAddress.value : props.dataAnswer.address,
      image_urls: urlList.value,
      ...summary.value,
    });
    window.location.href = `https://max.ru/t468_hakaton_max_bot?startapp=${response.data.uuid}`;
  } catch (error) {
    ElMessage.error(getErrorText(error));
    console.error(error);
  } finally {
    isCreating.value = false;
  }
}
</script>

<style scoped>
.result-header {
  display: grid;
  grid-template-columns: 44px 1fr 44px;
  align-items: center;
  gap: 12px;
}

.result-header > div:nth-child(2) {
  display: flex;
  flex-direction: column;
  gap: 3px;
}

.result-header strong {
  color: #111827;
  font-size: 17px;
}

.result-header span {
  color: #6b7280;
  font-size: 12px;
}

.close-button,
.ready-mark {
  display: grid;
  place-items: center;
  width: 42px;
  height: 42px;
  border: 0;
  border-radius: 14px;
  font-size: 18px;
}

.close-button {
  color: #374151;
  background: #f3f4f6;
  cursor: pointer;
}

.ready-mark {
  color: #15803d;
  background: #dcfce7;
}

.result-content {
  display: flex;
  flex-direction: column;
  gap: 16px;
  max-width: 720px;
  margin: 0 auto;
  padding-bottom: 122px;
}

.result-hero {
  display: grid;
  grid-template-columns: 104px 1fr;
  align-items: center;
  gap: 18px;
  padding: 20px;
  border-radius: 24px;
}

.result-hero--critical { color: #991b1b; background: #fef2f2; }
.result-hero--high { color: #c2410c; background: #fff7ed; }
.result-hero--medium { color: #a16207; background: #fefce8; }
.result-hero--low { color: #166534; background: #f0fdf4; }

.risk-ring {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  width: 96px;
  height: 96px;
  border: 8px solid currentColor;
  border-radius: 50%;
  box-sizing: border-box;
}

.risk-ring strong { font-size: 22px; line-height: 1; }
.risk-ring span { margin-top: 3px; font-size: 11px; opacity: 0.75; }
.risk-copy > span { font-size: 12px; opacity: 0.72; }
.risk-copy h1 { margin: 4px 0 6px; font-size: 20px; line-height: 1.2; }
.risk-copy p { margin: 0; font-size: 13px; }

.address-card {
  display: flex;
  align-items: center;
  gap: 13px;
  padding: 15px;
  border: 1px solid #e5e7eb;
  border-radius: 18px;
}

.address-icon {
  display: grid;
  flex: 0 0 auto;
  place-items: center;
  width: 42px;
  height: 42px;
  border-radius: 14px;
  color: #1d4ed8;
  background: #eff6ff;
  font-size: 19px;
}

.address-content { display: flex; min-width: 0; flex: 1; flex-direction: column; gap: 5px; }
.address-card span { color: #6b7280; font-size: 11px; }
.address-card strong { color: #1f2937; font-size: 13px; line-height: 1.35; }
.address-card input {
  width: 100%;
  padding: 11px 12px;
  border: 1px solid #d1d5db;
  border-radius: 12px;
  outline: none;
  color: #111827;
  background: #ffffff;
  font-size: 16px;
}
.address-card input:focus { border-color: #2563eb; }
.address-card small { color: #6b7280; font-size: 10px; line-height: 1.35; }
.address-card--manual { align-items: flex-start; border-color: #bfdbfe; background: #f8fbff; }

.section-block {
  padding: 18px;
  border: 1px solid #e5e7eb;
  border-radius: 22px;
}

.section-heading {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  margin-bottom: 14px;
}

.section-heading > div { display: flex; flex-direction: column; gap: 2px; }
.section-heading span { color: #6b7280; font-size: 11px; }
.section-heading h2 { margin: 0; color: #111827; font-size: 17px; }
.section-heading small { color: #6b7280; font-size: 12px; }

.severity-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 9px;
}

.severity {
  display: flex;
  flex-direction: column;
  gap: 2px;
  padding: 13px;
  border-radius: 14px;
}

.severity strong { font-size: 20px; }
.severity span { font-size: 11px; }
.severity--critical { color: #991b1b; background: #fef2f2; }
.severity--high { color: #c2410c; background: #fff7ed; }
.severity--medium { color: #a16207; background: #fefce8; }
.severity--low { color: #166534; background: #f0fdf4; }

.processed-grid {
  display: grid;
  gap: 10px;
}

.processed-card {
  overflow: hidden;
  border-radius: 16px;
  background: #111827;
}

.processed-card .el-image {
  display: block;
  width: 100%;
  height: 210px;
}

.processed-meta {
  display: flex;
  justify-content: space-between;
  padding: 11px 13px;
  color: #e5e7eb;
  font-size: 12px;
}

.processed-meta strong { color: #ffffff; }

.next-step {
  display: flex;
  gap: 12px;
  padding: 16px;
  border-radius: 18px;
  background: #f3f4f6;
}

.next-step__number {
  display: grid;
  flex: 0 0 auto;
  place-items: center;
  width: 32px;
  height: 32px;
  border-radius: 11px;
  color: #ffffff;
  background: #2563eb;
  font-size: 13px;
  font-weight: 800;
}

.next-step > div:last-child { display: flex; flex-direction: column; gap: 4px; }
.next-step strong { color: #111827; font-size: 13px; }
.next-step span { color: #6b7280; font-size: 12px; line-height: 1.4; }

.result-footer {
  display: grid;
  grid-template-columns: 1fr auto;
  align-items: center;
  gap: 12px;
  max-width: 720px;
  margin: 0 auto;
}

.footer-copy { display: flex; min-width: 0; flex-direction: column; gap: 2px; text-align: left; }
.footer-copy span { color: #6b7280; font-size: 10px; }
.footer-copy strong { overflow: hidden; color: #111827; font-size: 12px; text-overflow: ellipsis; white-space: nowrap; }

.report-button {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  min-width: 132px;
  min-height: 50px;
  padding: 0 18px;
  border: 0;
  border-radius: 16px;
  color: #ffffff;
  background: #2563eb;
  font: inherit;
  font-size: 14px;
  font-weight: 700;
  cursor: pointer;
}

.report-button:disabled { opacity: 0.7; cursor: default; }
.button-spinner { width: 15px; height: 15px; border: 2px solid rgba(255,255,255,.4); border-top-color: #fff; border-radius: 50%; animation: spin .7s linear infinite; }
@keyframes spin { to { transform: rotate(360deg); } }

:deep(.result-dialog) { background: #ffffff; }
:deep(.result-dialog .el-dialog__header) {
  position: sticky;
  top: 0;
  z-index: 5;
  margin: 0;
  padding: max(14px, env(safe-area-inset-top)) 16px 12px;
  border-bottom: 1px solid #eef0f3;
  background: rgba(255, 255, 255, 0.94);
  backdrop-filter: blur(14px);
}
:deep(.result-dialog .el-dialog__body) { padding: 16px; }
:deep(.result-dialog .el-dialog__footer) {
  position: fixed;
  right: 0;
  bottom: 0;
  left: 0;
  z-index: 6;
  padding: 11px 16px max(13px, env(safe-area-inset-bottom));
  border-top: 1px solid #eef0f3;
  background: rgba(255, 255, 255, 0.96);
  backdrop-filter: blur(14px);
}
</style>
