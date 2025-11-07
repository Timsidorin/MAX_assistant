<template>
  <camera-preview/>
  <div class="container-switch-camera-mode">
    <photo-button class="camera-button"/>
    <switch-camera-mode class="switch-camera-mode"/>
  </div>
</template>

<script setup>
import SwitchCameraMode from "./camera-components/SwitchCameraMode.vue";
import PhotoButton from "./camera-components/PhotoButton.vue";
import CameraPreview from "./camera-components/CameraPreview.vue";
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
</style>