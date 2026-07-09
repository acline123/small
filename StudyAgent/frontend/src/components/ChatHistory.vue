<template>
  <div class="history-panel">
    <div class="panel-header">
      <span>历史会话</span>
      <el-button type="primary" size="small" @click="$emit('new-chat')">新对话</el-button>
    </div>
    <div
      v-for="s in sortedSessions"
      :key="s.session_id"
      :class="['session-item', { active: s.session_id === activeId }]"
    >
      <div class="session-row" @click="$emit('select', s.session_id)">
        <div class="session-info">
          <div class="title">
            <el-icon v-if="s.pinned" class="pin-icon"><StarFilled /></el-icon>
            {{ s.title }}
          </div>
          <div class="time">{{ s.updated_at }}</div>
        </div>
      </div>
      <div class="menu-wrapper">
        <el-dropdown trigger="click" @command="(cmd) => handleCommand(cmd, s)">
          <el-button class="menu-btn" size="small" circle>
            <el-icon><MoreFilled /></el-icon>
          </el-button>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item command="pin">
                <el-icon><StarFilled /></el-icon>
                {{ s.pinned ? "取消置顶" : "置顶" }}
              </el-dropdown-item>
              <el-dropdown-item command="rename">
                <el-icon><Edit /></el-icon>
                重命名
              </el-dropdown-item>
              <el-dropdown-item command="delete" divided>
                <el-icon><Delete /></el-icon>
                删除
              </el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </div>
    </div>
    <el-empty v-if="!sessions.length" description="暂无会话" />
  </div>
</template>

<script setup>
import { computed } from "vue"
import { ElMessage, ElMessageBox } from "element-plus"
import { MoreFilled, StarFilled, Edit, Delete } from "@element-plus/icons-vue"
import { deleteSession, togglePin, renameSession } from "../api/chat"

const props = defineProps({
  sessions: { type: Array, default: () => [] },
  activeId: { type: String, default: "" },
})

const emit = defineEmits(["select", "new-chat", "refresh"])

const sortedSessions = computed(() => {
  return [...props.sessions].sort((a, b) => {
    if (a.pinned !== b.pinned) return a.pinned ? -1 : 1
    return 0
  })
})

const handleCommand = async (cmd, session) => {
  if (cmd === "delete") {
    try {
      await ElMessageBox.confirm("确定要删除这个会话吗？", "删除确认", {
        confirmButtonText: "删除",
        cancelButtonText: "取消",
        type: "warning",
      })
      await deleteSession(session.session_id)
      ElMessage.success("会话已删除")
      emit("refresh")
    } catch {
      // 用户取消或请求失败都不处理
    }
    return
  }

  if (cmd === "pin") {
    try {
      await togglePin(session.session_id)
      ElMessage.success(session.pinned ? "已取消置顶" : "已置顶")
      emit("refresh")
    } catch {
      // 请求失败时拦截器已处理
    }
    return
  }

  if (cmd === "rename") {
    try {
      const { value } = await ElMessageBox.prompt("输入新的会话名称", "重命名", {
        confirmButtonText: "确定",
        cancelButtonText: "取消",
        inputValue: session.title,
        inputPlaceholder: "输入新名称",
      })
      if (value && value.trim()) {
        await renameSession(session.session_id, value.trim())
        ElMessage.success("重命名成功")
        emit("refresh")
      }
    } catch {
      // 用户取消
    }
    return
  }
}
</script>

<style scoped>
.history-panel {
  width: 260px;
  border-right: 1px solid #e4e7ed;
  padding: 12px;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 4px;
}
.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
  font-weight: bold;
}
.session-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 8px 8px 8px 12px;
  border-radius: 6px;
  cursor: pointer;
  border: 1px solid transparent;
  transition: background 0.15s;
}
.session-item:hover {
  background: #f0f2f5;
}
.session-item.active {
  background: #ecf5ff;
  border-color: #409eff;
}
.session-row {
  flex: 1;
  min-width: 0;
}
.session-info {
  min-width: 0;
}
.title {
  font-size: 14px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  display: flex;
  align-items: center;
  gap: 4px;
}
.pin-icon {
  color: #e6a23c;
  font-size: 12px;
  flex-shrink: 0;
}
.time {
  font-size: 12px;
  color: #909399;
  margin-top: 2px;
}
.menu-wrapper {
  flex-shrink: 0;
  margin-left: 4px;
}
.menu-btn {
  border: none;
  background: transparent;
  font-size: 14px;
  width: 28px;
  height: 28px;
  opacity: 0.6;
}
.session-item:hover .menu-btn {
  opacity: 1;
}
</style>
