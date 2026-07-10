<template>
  <div>
    <el-upload
      drag
      :auto-upload="false"
      :show-file-list="false"
      accept=".pdf,.docx,.txt,.pptx"
      :on-change="handleChange"
      :disabled="uploadState.status === 'uploading'"
    >
      <el-icon class="upload-icon"><UploadFilled /></el-icon>
      <div class="el-upload__text">拖拽文件到此处，或 <em>点击上传</em></div>
      <template #tip>
        <div class="el-upload__tip">支持 PDF、DOCX、TXT、PPTX 格式</div>
      </template>
    </el-upload>

    <div v-if="uploadState.status !== 'idle'" class="upload-progress-area">
      <div class="progress-item">
        <div class="progress-info">
          <span class="file-name">{{ uploadState.fileName }}</span>
          <span class="file-status" :class="uploadState.status">
            {{ statusText }}
          </span>
        </div>
        <el-progress
          :percentage="uploadState.percent"
          :status="progressStatus"
          :stroke-width="8"
          style="margin-top: 6px"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed } from "vue"
import { ElMessage } from "element-plus"
import { uploadDocumentWithProgress } from "../api/document"

const emit = defineEmits(["uploaded"])

const uploadState = reactive({
  status: "idle",
  fileName: "",
  percent: 0,
})

const statusText = computed(() => {
  const map = { idle: "", uploading: "上传中...", success: "上传完成", error: "上传失败" }
  return map[uploadState.status]
})

const progressStatus = computed(() => {
  if (uploadState.status === "success") return "success"
  if (uploadState.status === "error") return "exception"
  return ""
})

const handleChange = async (uploadFile) => {
  const file = uploadFile?.raw
  if (!file || uploadState.status === "uploading") return

  uploadState.status = "uploading"
  uploadState.fileName = file.name
  uploadState.percent = 0

  try {
    await uploadDocumentWithProgress(file, (pct) => {
      uploadState.percent = pct
    })
    uploadState.percent = 100
    uploadState.status = "success"
    ElMessage.success("「" + file.name + "」上传成功，知识库已更新")
    emit("uploaded")
  } catch (e) {
    uploadState.status = "error"
    const msg = e.response?.data?.message || e.message || "上传失败"
    ElMessage.error(msg)
  }
}
</script>

<style scoped>
.upload-icon {
  font-size: 48px;
  color: #409eff;
}
.upload-progress-area {
  margin-top: 16px;
  padding: 12px 16px;
  background: #f8f9fb;
  border-radius: 8px;
  border: 1px solid #e8eaed;
}
.progress-item {
  margin-bottom: 0;
}
.progress-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 13px;
}
.file-name {
  color: #303133;
  max-width: 70%;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.file-status {
  font-size: 12px;
}
.file-status.uploading {
  color: #409eff;
}
.file-status.success {
  color: #67c23a;
}
.file-status.error {
  color: #f56c6c;
}
</style>
