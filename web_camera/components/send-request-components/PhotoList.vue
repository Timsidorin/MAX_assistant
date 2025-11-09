<template>
  <div class="elements">
    <el-image
        class="element"
        v-for="(element, index) in elements"
        :preview-src-list="urlList"
        :src="element.url"
        style="border-radius: 6px"
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
</template>

<script setup>
import {Back, Right, ZoomIn, ZoomOut, Delete} from '@element-plus/icons-vue';
import {computed, inject} from "vue";

const props = defineProps({
  elements: Array,
  urlList: Array,
});
const deleteElement = inject("deleteElement");

</script>

<style scoped>
.elements {
  display: flex;
  gap: 1rem;
  flex-wrap: wrap;
}

.element {
  flex-basis: 100px;
}
</style>