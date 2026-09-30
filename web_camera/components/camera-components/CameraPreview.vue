<template>
  <div class="camera-preview">
    <video v-show="cameraAccess" ref="videoElement" autoplay muted playsinline></video>
    <div v-if="isLoading" class="camera-loading">
      <div class="camera-loading__spinner"></div>
      <strong>Запускаем камеру</strong>
      <span>Разрешите доступ, если браузер запросит его</span>
    </div>
    <NoAccessCamera
      v-else-if="!cameraAccess"
      :message="errorMessage"
      @retry="renderCamera"
    />
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, nextTick } from 'vue';
import NoAccessCamera from "../errors/NoAccessCamera.vue";

const emit = defineEmits(['access-change']);
const videoElement = ref(null);
const mediaStream = ref(null);
const cameraAccess = ref(false);
const isLoading = ref(true);
const errorMessage = ref('');

const getErrorMessage = (error) => {
  if (!window.isSecureContext) {
    return 'Камера работает только при защищённом HTTPS-соединении.';
  }
  if (error?.name === 'NotAllowedError') {
    return 'Доступ к камере запрещён. Разрешите его в настройках браузера и попробуйте снова.';
  }
  if (error?.name === 'NotFoundError') {
    return 'На устройстве не найдена доступная камера.';
  }
  if (error?.name === 'NotReadableError') {
    return 'Камера занята другим приложением. Закройте его и попробуйте снова.';
  }
  return 'Не удалось запустить камеру. Проверьте разрешения браузера.';
};

const renderCamera = async () => {
  isLoading.value = true;
  errorMessage.value = '';
  cameraAccess.value = false;

  try {
    if (mediaStream.value) {
      stopCamera();
    }

    if (!navigator.mediaDevices?.getUserMedia) {
      throw new Error('getUserMedia is unavailable');
    }

    const stream = await navigator.mediaDevices.getUserMedia({
      video: {
        facingMode: { ideal: 'environment' },
        width: { ideal: 1920 },
        height: { ideal: 1080 }
      },
      audio: false
    });

    mediaStream.value = stream;
    cameraAccess.value = true;
    emit('access-change', true);
    await nextTick();

    if (videoElement.value) {
      videoElement.value.srcObject = stream;
      await videoElement.value.play();
    }
  } catch (error) {
    console.error('getUserMedia error:', error);
    stopCamera();
    cameraAccess.value = false;
    emit('access-change', false);
    errorMessage.value = getErrorMessage(error);
  } finally {
    isLoading.value = false;
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

const capturePhoto = () => {
  if (!videoElement.value || !mediaStream.value) {
    throw new Error('Камера не активна');
  }
  const video = videoElement.value;
  const canvas = document.createElement('canvas');
  const context = canvas.getContext('2d');

  canvas.width = video.videoWidth;
  canvas.height = video.videoHeight;
  context.drawImage(video, 0, 0, canvas.width, canvas.height);
  return canvas.toDataURL();
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
.camera-preview {
  position: fixed;
  inset: 0;
  background: #111827;
  overflow: hidden;
}

video {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.camera-loading {
  position: absolute;
  inset: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 10px;
  padding: 24px;
  color: white;
  text-align: center;
}

.camera-loading span {
  color: #cbd5e1;
  font-size: 14px;
}

.camera-loading__spinner {
  width: 36px;
  height: 36px;
  border: 3px solid rgba(255, 255, 255, 0.25);
  border-top-color: white;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}
</style>