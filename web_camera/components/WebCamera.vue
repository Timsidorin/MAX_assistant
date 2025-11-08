<template>
  <camera-preview ref="camera"/>
  <div class="container-switch-camera-mode">
    <photo-button @take-photo="takePhoto" :camera-mode="cameraMode" class="camera-button"/>
    <switch-camera-mode v-model="cameraMode" class="switch-camera-mode"/>
    <media-store :elements="mediaStore" class="media-store"/>
  </div>
</template>

<script setup>
import SwitchCameraMode from "./camera-components/SwitchCameraMode.vue";
import PhotoButton from "./camera-components/PhotoButton.vue";
import CameraPreview from "./camera-components/CameraPreview.vue";
import MediaStore from "./camera-components/MediaStore.vue";
import {ref} from "vue";

const cameraMode = ref('photo');
const camera = ref(null);
const mediaStore = ref([]);

function takePhoto() {
  const newPhoto = camera.value.capturePhoto();
  mediaStore.value.push(newPhoto);
}
</script>

<style scoped>
.container-switch-camera-mode {
  position: absolute;
  bottom: 5%;
  left: 0;
  right: 0;
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.switch-camera-mode {
  margin-left: auto;
  margin-right: auto;
}

.camera-button {
  margin-left: auto;
  margin-right: auto;
  margin-bottom: 5%;
}

.media-store {
  margin-left: auto;
  margin-right: 10%;
}
</style>