<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { ElMessage, ElMessageBox, type UploadRequestOptions } from 'element-plus'
import { deleteDoc, listDocs, uploadDoc, type DocInfo } from '../api/docs'

const docs = ref<DocInfo[]>([])
const uploading = ref(false)
const progress = ref(0)

async function refresh() {
  docs.value = await listDocs()
}

onMounted(refresh)

async function customUpload(options: UploadRequestOptions) {
  uploading.value = true
  progress.value = 0
  try {
    const res = await uploadDoc(options.file as File, (p) => (progress.value = p))
    ElMessage.success(`《${res.filename}》已入库，生成 ${res.chunk_count} 个切片`)
    await refresh()
  } catch (e: unknown) {
    const detail =
      (e as { response?: { data?: { detail?: string } } })?.response?.data?.detail ??
      '上传失败'
    ElMessage.error(detail)
  } finally {
    uploading.value = false
    progress.value = 0
  }
}

async function remove(row: DocInfo) {
  await ElMessageBox.confirm(
    `确认删除《${row.filename}》？该文档的全部向量切片将一并移除。`,
    '删除确认',
    { type: 'warning' },
  )
  await deleteDoc(row.id)
  ElMessage.success('已删除')
  await refresh()
}
</script>

<template>
  <div class="page">
    <h2 class="title">知识库管理</h2>

    <el-upload
      drag
      :show-file-list="false"
      :http-request="customUpload"
      accept=".pdf,.txt,.md,.docx"
    >
      <el-icon class="el-icon--upload"><upload-filled /></el-icon>
      <div class="el-upload__text">拖拽文件到此处，或<em>点击上传</em></div>
      <template #tip>
        <div class="el-upload__tip">支持 PDF / TXT / Markdown / DOCX，上传后自动解析、切片并向量化入库</div>
      </template>
    </el-upload>

    <el-progress v-if="uploading" :percentage="progress" style="margin: 12px 0" />

    <el-table :data="docs" style="margin-top: 16px" empty-text="暂无文档，先上传一个吧">
      <el-table-column prop="filename" label="文件名" min-width="240" />
      <el-table-column prop="chunk_count" label="切片数" width="100" align="center" />
      <el-table-column prop="status" label="状态" width="100" align="center">
        <template #default="{ row }">
          <el-tag size="small" type="success">{{ row.status }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="created_at" label="入库时间（UTC）" width="220" />
      <el-table-column label="操作" width="100" align="center">
        <template #default="{ row }">
          <el-button size="small" type="danger" link @click="remove(row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>
  </div>
</template>

<style scoped>
.page {
  padding: 24px 8%;
  height: 100vh;
  overflow-y: auto;
  box-sizing: border-box;
}
.title {
  margin: 0 0 16px;
  font-size: 18px;
}
</style>
