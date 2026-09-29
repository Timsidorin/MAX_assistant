<template>
  <div class="photo-grid">
    <article v-for="(element, index) in elements" :key="element.id" class="photo-card">
      <el-image
        class="photo-card__image"
        :preview-src-list="urlList"
        :src="element.url"
        :initial-index="index"
        fit="cover"
        preview-teleported
      />
      <span class="photo-card__number">{{ index + 1 }}</span>
      <button
        type="button"
        class="photo-card__delete"
        :aria-label="`Удалить снимок ${index + 1}`"
        @click.stop="deleteElement(element.id)"
      >
        <el-icon><Delete /></el-icon>
      </button>
    </article>
    <button v-if="elements.length < 10" type="button" class="photo-add" @click="$emit('add-more')">
      <el-icon><Plus /></el-icon>
      <span>Добавить ракурс</span>
    </button>
  </div>
</template>

<script setup>
import {Delete, Plus} from '@element-plus/icons-vue';
import {inject} from "vue";

defineProps({
  elements: Array,
  urlList: Array,
});

defineEmits(['add-more']);

const deleteElement = inject("deleteElement");
</script>

<style scoped>
.photo-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 12px;
}

.photo-card,
.photo-add {
  position: relative;
  min-height: 150px;
  overflow: hidden;
  border-radius: 18px;
  background: #e5e7eb;
}

.photo-card__image {
  width: 100%;
  height: 100%;
  min-height: 150px;
  display: block;
}

.photo-card__number {
  position: absolute;
  bottom: 10px;
  left: 10px;
  display: grid;
  place-items: center;
  width: 27px;
  height: 27px;
  border-radius: 9px;
  color: #ffffff;
  background: rgba(15, 23, 42, 0.72);
  backdrop-filter: blur(8px);
  font-size: 12px;
  font-weight: 700;
}

.photo-card__delete {
  position: absolute;
  top: 10px;
  right: 10px;
  display: grid;
  place-items: center;
  width: 34px;
  height: 34px;
  padding: 0;
  border: 0;
  border-radius: 11px;
  color: #ffffff;
  background: rgba(15, 23, 42, 0.72);
  backdrop-filter: blur(8px);
  cursor: pointer;
}

.photo-add {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 8px;
  border: 1px dashed #9ca3af;
  color: #4b5563;
  background: #f9fafb;
  font: inherit;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
}

.photo-add .el-icon {
  font-size: 24px;
}

@media (min-width: 540px) {
  .photo-grid {
    grid-template-columns: repeat(3, minmax(0, 1fr));
  }
}
</style>
