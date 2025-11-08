<template>
  <el-button @click="eventClick" :color="mode.color" circle/>
</template>

<script setup>

import {computed} from "vue";

const emit = defineEmits(["take-photo", "take-video"]);
const props = defineProps(['cameraMode']);

const mode = computed(() => {
  let photoMode = {
    color: 'white',
    action: 'take-photo'
  };
  let videoMode = {
    color: '#ff3c3c',
    action: 'take-video'
  };
  return props.cameraMode === 'photo' ? photoMode : videoMode;
});

function eventClick() {
  emit(mode.value.action);
}
</script>

<style scoped>
.el-button {
  width: 70px;
  height: 70px;
  border: 2px solid #ccc;
}
</style>