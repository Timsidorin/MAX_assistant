<template>
  <el-dialog
      v-model="model"
      title="Успешная обработка"
      style="width: 100%; max-width: 400px"
  >
    <el-image
        class="element"
        v-for="(element, index) in photos"
        :preview-src-list="urlList"
        :src="element.image_url"
        style="border-radius: 6px"
        :initial-index="index"
    />
    <template #footer>
      <div class="dialog-footer">
        <el-button type="primary" @click="model = false">
          Отправить
        </el-button>
      </div>
    </template>
  </el-dialog>
</template>

<script setup>
import {computed, nextTick, onMounted, ref} from "vue";

const model = defineModel();

const props = defineProps({
  dataAnswer: Object,
});
const photos = ref(props.dataAnswer.results);

const urlList = computed(() => {
  return photos.value.map(elem => elem.image_url)
});
</script>
