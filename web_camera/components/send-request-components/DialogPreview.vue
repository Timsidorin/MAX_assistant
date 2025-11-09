<template>
  <el-dialog v-model="model" fullscreen>
    <photo-list :url-list="urlList" v-if="elements.length > 0" :elements="elements"/>
    <el-button @click="sendMedias" class="button-send-media" type="primary" plain>Отправить</el-button>
    <dialog-processed-media v-if="dataAnswer" :data-answer="dataAnswer" v-model="message"/>
  </el-dialog>
</template>

<script setup>
import PhotoList from "./PhotoList.vue";
import {computed, onMounted, ref} from "vue";
import {downloadMedias} from "@api/MediaDownload.js";
import {getLocation} from "@helpers/gps.js";
import {ElLoading} from 'element-plus'
import DialogProcessedMedia from "./DialogProcessedMedia.vue";

const props = defineProps(["elements"]);
const model = defineModel();
const urlList = computed(() => {
  return props.elements.map(elem => elem.url);
});
const dataAnswer = ref(null);
const message = ref(false);
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
    dataAnswer.value = await downloadMedias(data);
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
  position: sticky;
  left: 100%;
  z-index: 99;
  margin-top: 20px;
}

</style>