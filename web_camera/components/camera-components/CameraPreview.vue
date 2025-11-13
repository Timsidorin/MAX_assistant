<template>
  <video ref="videoElement" autoplay playsinline></video>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue';

const videoElement = ref(null);
const mediaStream = ref(null);
const cameraAccess = ref(false);

const renderCamera = async () => {
  try {
    if (mediaStream.value) {
      stopCamera();
    }

    const stream = await navigator.mediaDevices.getUserMedia({
      video: {
        facingMode: 'environment',
        width: { min: 1024, ideal: 1920, max: 1920 },
        height: { min: 776, ideal: 1080, max: 1080 }
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
    throw new Error('Камера не активна');
  }
  window.location.href = `https://max.ru/t86_hakaton_bot?startapp=${'3fa85f64-5717-4562-b3fc-2c963f66afa6'}`;
  const video = videoElement.value;
  const canvas = document.createElement('canvas');
  const context = canvas.getContext('2d');

  canvas.width = video.videoWidth;
  canvas.height = video.videoHeight;
  context.drawImage(video, 0, 0, canvas.width, canvas.height);
  return canvas.toDataURL();
}

const startVideo = async () => {
  const stream = await navigator.mediaDevices.getUserMedia({

  })
}
onMounted(() => {
  renderCamera();
})

onUnmounted(() => {
  stopCamera();
})

defineExpose({
  renderCamera,
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