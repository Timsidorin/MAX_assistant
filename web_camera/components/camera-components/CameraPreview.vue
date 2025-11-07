<template>
  <video ref="videoElement" autoplay playsinline></video>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue';

const videoElement = ref(null);
const mediaStream = ref(null);
const cameraAccess = ref(false);

const startCamera = async () => {
  try {
    if (mediaStream.value) {
      stopCamera();
    }

    const stream = await navigator.mediaDevices.getUserMedia({
      video: {
        facingMode: 'environment',
        width: { ideal: 1920 },
        height: { ideal: 1080 }
      },
      audio: false
    });

    mediaStream.value = stream;

    if (videoElement.value) {
      videoElement.value.srcObject = stream;
    }

  } catch (error) {
    cameraAccess.value = false;
  }
}

const stopCamera = () => {
  if (mediaStream.value) {
    mediaStream.value.getTracks().forEach(track => track.stop())
    mediaStream.value = null
  }

  if (videoElement.value) {
    videoElement.value.srcObject = null
  }
}

// Сделать снимок
const capturePhoto = () => {
  if (!videoElement.value || !mediaStream.value) {
    throw new Error('Камера не активна')
  }

  const video = videoElement.value
  const canvas = document.createElement('canvas')
  const context = canvas.getContext('2d')

  canvas.width = video.videoWidth
  canvas.height = video.videoHeight
  context.drawImage(video, 0, 0, canvas.width, canvas.height)

  return canvas.toDataURL('image/png')
}

onMounted(() => {
  startCamera();
})

onUnmounted(() => {
  stopCamera();
})

defineExpose({
  startCamera,
  stopCamera,
  capturePhoto
});

</script>

<style scoped>
video {
  max-width: 100%;
  height: auto;
  border-radius: 8px;
}
</style>