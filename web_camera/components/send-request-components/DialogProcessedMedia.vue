<template>
  <el-dialog
      v-model="model"
      title="Успешная обработка"
      style="width: 100%; max-width: 400px"
  >
    <p>Ближайший адрес: <b>{{ dataAnswer.address ?? 'Не определен' }}</b></p>
    <el-scrollbar max-height="400px">
      <div style="display: flex; flex-direction: row; gap: 10px; flex-wrap: wrap">
        <el-image
            class="element"
            v-for="(element, index) in photos"
            :preview-src-list="urlList"
            :src="element.image_url"
            style="border-radius: 6px; height: 100px; width: 100px"
            :initial-index="index"
        >
          <template #toolbar="{ prev, next, actions }">
            <el-icon @click="prev">
              <Back/>
            </el-icon>
            <el-icon @click="next">
              <Right/>
            </el-icon>
            <el-icon @click="actions('zoomOut')">
              <ZoomOut/>
            </el-icon>
            <el-icon @click="actions('zoomIn', { enableTransition: false, zoomRate: 2 })">
              <ZoomIn/>
            </el-icon>
            <el-icon @click="openStatistic(element.detections)">
              <Histogram/>
            </el-icon>
          </template>
        </el-image>
      </div>
    </el-scrollbar>
    <span style="margin-top: 5px; display: flex; align-items: center; ">
      <el-icon style="margin-right: 2px">
        <InfoFilled/>
      </el-icon>
      Для детализации нажмите на снимок
    </span>
    <template #footer>
      <div class="dialog-footer">
        <el-button type="primary" @click="handleSendReport">
          Начать формирование заявления
        </el-button>
      </div>
    </template>
  </el-dialog>
</template>

<script setup>
import {computed, ref, h} from "vue";
import {Back, Histogram, InfoFilled, Right, ZoomIn, ZoomOut} from "@element-plus/icons-vue";
import {ElMessageBox, ElLoading} from "element-plus";
import {sendReport} from "@api/report.js";

const model = defineModel();

const props = defineProps({
  dataAnswer: Object,
});
const photos = ref(props.dataAnswer.results);

const urlList = computed(() => {
  return photos.value.map(elem => elem.image_url)
});

function openStatistic(stat) {
  ElMessageBox({
    confirmButtonText: 'Ок',
    title: 'Результат анализа',
    message: h('div', {style: {display: 'flex', flexDirection: 'row', gap: '20px'}}, [
      h('div', {style: {display: 'flex', flexDirection: 'column'}}, [
        h('span', {innerHTML: `Всего ям: ${stat.CRITICAL + stat.HIGH + stat.LOW + stat.MEDIUM}`})
      ]),
      h('div', {style: {display: 'flex', flexDirection: 'column'}}, [
        h('span', {innerHTML: 'По уровню опасности'}),
        h('span', {innerHTML: `Критический: ${stat.CRITICAL}`, style: {color: '#f56c6c'}}),
        h('span', {innerHTML: `Высокий: ${stat.HIGH}`, style: {color: '#ff8989'}}),
        h('span', {innerHTML: `Средний: ${stat.LOW}`, style: {color: '#e6a23c'}}),
        h('span', {innerHTML: `Низкий: ${stat.MEDIUM}`, style: {color: '#67c23a'}}),
      ]),
    ]),
  })
}

async function handleSendReport() {
  let total_potholes = {
    average_risk: 0,
    max_risk: 0,
    detections: {
      CRITICAL: 0,
      HIGH: 0,
      MEDIUM: 0,
      LOW: 0,
      total_potholes: 0
    }
  };
  props.dataAnswer.results.forEach((element) => {
    total_potholes.average_risk = element.average_risk > total_potholes.average_risk
        ? element.average_risk : total_potholes.average_risk;
    total_potholes.max_risk = element.max_risk > total_potholes.max_risk
        ? element.max_risk : total_potholes.max_risk;
    total_potholes.detections.CRITICAL += element.detections.CRITICAL;
    total_potholes.detections.HIGH += element.detections.HIGH;
    total_potholes.detections.MEDIUM += element.detections.MEDIUM;
    total_potholes.detections.LOW += element.detections.LOW;
    total_potholes.total_potholes = element.total_potholes;
  });
  let data = {
    user_id: props.dataAnswer.user_id,
    latitude: props.dataAnswer.latitude,
    longitude: props.dataAnswer.longitude,
    address: props.dataAnswer.address,
    image_urls: urlList.value,
    ...total_potholes,
  }
  const loading = ElLoading.service({
    lock: true,
    text: 'Открываю мини-приложение',
    background: 'primary',
  });
  try {
    let response = await sendReport(data);
    window.location.href = `https://max.ru/t86_hakaton_bot?startapp&draftUUID=${response.data.uuid}`;
  } catch (e) {
    console.error(e);
  } finally {
    loading.close();
  }
}
</script>
