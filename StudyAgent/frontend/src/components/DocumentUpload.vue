<template>
  <el-upload
    drag
    :auto-upload="false"
    :show-file-list="false"
    accept=".pdf,.docx,.txt,.pptx"
    :on-change="handleChange"
  >
    <el-icon class="upload-icon"><UploadFilled /></el-icon>
    <div class="el-upload__text">拖拽文件到此处，或 <em>点击上传</em></div>
    <template #tip>
      <div class="el-upload__tip">支持 PDF、DOCX、TXT、PPTX 格式</div>
    </template>
  </el-upload>
</template>

<script setup>
import { ElMessage } from 'element-plus'
import { uploadDocument } from '../api/document'

const emit = defineEmits(['uploaded'])

const handleChange = async (file) => {
  try {
    await uploadDocument(file.raw)
    ElMessage.success('上传成功，知识库已更新')
    emit('uploaded')
  } catch (e) {
    /* 错误已在拦截器处理 */
  }
}
</script>

<style scoped>
.upload-icon {
  font-size: 48px;
  color: #409eff;
}
</style>
