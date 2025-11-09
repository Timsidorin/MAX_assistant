<template>
  <el-dialog v-model="model" fullscreen>
    <photo-list :url-list="urlList" v-if="elements.length > 0" :elements="elements"/>
    <dialog-processed-media v-if="dataAnswer" :data-answer="dataAnswer" v-model="message"/>
    <template #footer>
      <div class="dialog-footer">
        <el-button @click="sendMedias" class="button-send-media" type="primary" plain>Обработать</el-button>
      </div>
    </template>
  </el-dialog>
</template>

<script setup>
import PhotoList from "./PhotoList.vue";
import {computed, ref} from "vue";
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
  display: block;
  margin-left: auto;
  margin-top: 50px
}

</style>