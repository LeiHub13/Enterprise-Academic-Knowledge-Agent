<script setup lang="ts">
import type { Source } from '../api/chat'

defineProps<{ sources: Source[] }>()
</script>

<template>
  <div v-if="sources && sources.length" class="sources">
    <div class="title">参考来源（{{ sources.length }}）</div>
    <div v-for="s in sources" :key="s.index" class="item">
      <div class="line">
        <el-tag size="small" type="primary" effect="plain">{{ s.index }}</el-tag>
        <span class="name">{{ s.source }}</span>
      </div>
      <p class="snippet">{{ s.snippet }}…</p>
    </div>
  </div>
</template>

<style scoped>
.sources {
  margin-top: 10px;
  border-top: 1px dashed #e4e3dd;
  padding-top: 8px;
}
.title {
  font-size: 12px;
  color: #6b7280;
  margin-bottom: 6px;
}
.item {
  margin-bottom: 6px;
}
.line {
  display: flex;
  align-items: center;
  gap: 6px;
}
.name {
  font-size: 12px;
  color: #1a1b1c;
  font-weight: 600;
}
.snippet {
  margin: 4px 0 0;
  font-size: 12px;
  color: #6b7280;
  line-height: 1.6;
  white-space: pre-wrap;
}
</style>
