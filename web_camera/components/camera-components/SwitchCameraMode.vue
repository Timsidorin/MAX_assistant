<template>
  <el-segmented v-model="value" :options="options" size="large"/>
</template>

<script setup>

const value = defineModel();

let options = [
  {
    value: 'photo',
    label: 'Фото'
  },
  // {
  //   value: 'video',
  //   label: 'Видео'
  // }
]
</script>

<style scoped>
.el-segmented {
  --el-border-radius-base: 16px;
  width: 50%;
}
</style>