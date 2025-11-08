<template>
  <el-badge v-if="elements.length > 0" :value="elements.length" class="item">
    <el-button class="share-button" :icon="ArrowRight" type="primary" />
  </el-badge>
</template>

<script setup>
import {ArrowRight} from "@element-plus/icons-vue";

const props = defineProps(['elements']);
</script>
