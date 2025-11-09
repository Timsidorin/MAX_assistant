<template>
  <el-dialog
      v-model="model"
      title="Успешная обработка"
      style="width: 100%; max-width: 400px"
  >
    <p>Адрес: <b>{{dataAnswer.address ?? 'Не определен'}}</b></p>
    <el-scrollbar height="400px">
      <div style="display: flex; flex-direction: row; gap: 10px; flex-wrap: wrap">
        <el-image
          class="element"
          v-for="(element, index) in photos"
          :preview-src-list="urlList"
          :src="element.image_url"
          style="border-radius: 6px; height: 100px; width: 100px"
          :initial-index="index"
      />
      </div>
    </el-scrollbar>
    <template #footer>
      <div class="dialog-footer">
        <el-button type="primary" @click="sendTicket">
          Отправить
        </el-button>
      </div>
    </template>
  </el-dialog>
</template>

<script setup>
import {computed, ref} from "vue";

const model = defineModel();

const props = defineProps({
  dataAnswer: Object,
});
const photos = ref(props.dataAnswer.results);

const urlList = computed(() => {
  return photos.value.map(elem => elem.image_url)
});

function sendTicket() {
  window.location.href = 'https://max.ru/t86_hakaton_bot?startapp';
}
</script>
