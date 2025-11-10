<template>
  <el-dialog v-model="model" fullscreen>
    <photo-list :url-list="urlList" v-if="elements.length > 0" :elements="elements"/>
    <dialog-processed-media v-if="dataAnswer" :data-answer="dataAnswer" v-model="message"/>
    <span style="margin-top: 5px; display: flex; align-items: center; ">
      <el-icon style="margin-right: 2px">
        <InfoFilled />
      </el-icon>
      Для детализации нажмите на снимок
    </span>
    <template #footer>
      <div class="dialog-footer">
        <el-tooltip
            effect="dark"
            content="Можно обработать не более 10 снимков"
            placement="top-start"
            :disabled="disableButton"
        >
          <el-button :disabled="!disableButton" @click="sendMedias" class="button-send-media" type="primary" plain>Обработать</el-button>
        </el-tooltip>
        <el-text v-if="!disableButton" class="mx-1" size="small">Не более 10 снимков</el-text>
      </div>
    </template>
  </el-dialog>
</template>

<script setup>
import PhotoList from "./PhotoList.vue";
import {computed, ref} from "vue";
import {downloadMedias} from "@api/mediaDownload.js";
import {getLocation} from "@helpers/gps.js";
import {ElLoading} from 'element-plus';
import {InfoFilled} from "@element-plus/icons-vue";
import DialogProcessedMedia from "./DialogProcessedMedia.vue";

const props = defineProps(["elements"]);
const model = defineModel();
const urlList = computed(() => {
  return props.elements.map(elem => elem.url);
});
const dataAnswer = ref(null);
const message = ref(false);

const disableButton = computed(() => {
  return urlList.value.length <= 10;
});
async function sendMedias() {
  const urlParams = new URLSearchParams(window.location.search);
  const coords = await getLocation();
  let data = {
    images_base64: urlList.value,
    user_id: urlParams.get("user_id"),
    latitude: coords.status === true ? String(coords.data.latitude) : '',
    longitude: coords.status === true ? String(coords.data.longitude) : '',
    filenames: []
  }
  const loader = ElLoading.service({
    lock: true,
    text: 'Обработка нейросетью',
    background: 'primary',
  });
  try {
    dataAnswer.value = null;
    let response = await downloadMedias(data);
    dataAnswer.value = response.data;
    message.value = true;
  } catch (e) {
    console.error(e);
  } finally {
    loader.close();
  }
}
</script>

<style scoped>
.button-send-media {
  display: block;
  margin-left: auto;
  margin-top: 20px;
}

</style>