<template>
  <el-scrollbar always height="500px">
    <div style="display: flex; flex-direction: row; gap: 10px; flex-wrap: wrap">
      <el-image
          class="element"
          v-for="(element, index) in elements"
          :preview-src-list="urlList"
          :src="element.url"
          style="border-radius: 6px; height: 100px; width: 100px"
          :initial-index="index"
      >
        <template #toolbar="{ prev, next, actions }">
          <el-icon @click="prev">
            <Back/>
          </el-icon>
          <el-icon @click="next">
            <Right/>
          </el-icon>
          <el-icon @click="actions('zoomOut')">
            <ZoomOut/>
          </el-icon>
          <el-icon @click="actions('zoomIn', { enableTransition: false, zoomRate: 2 })">
            <ZoomIn/>
          </el-icon>
          <el-icon @click="deleteElement(element.id)">
            <Delete/>
          </el-icon>
        </template>
      </el-image>
    </div>
  </el-scrollbar>
</template>

<script setup>
import {Back, Right, ZoomIn, ZoomOut, Delete} from '@element-plus/icons-vue';
import {inject} from "vue";

const props = defineProps({
  elements: Array,
  urlList: Array,
});
const deleteElement = inject("deleteElement");

</script>

<style scoped>

</style>