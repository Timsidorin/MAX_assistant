<template>
  <el-segmented v-model="value" :options="options" size="large" />
</template>

<script setup>
import { ref } from 'vue'

const value = ref('Фото')

const options = ['Фото', 'Видео']
</script>

<style scoped>
.el-segmented {
  --el-border-radius-base: 16px;
  width: 50%;
}
</style>