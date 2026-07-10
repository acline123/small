<template>
  <div class="exercise-page">
    <h2>智能习题</h2>

    <!-- 知识水平卡片 -->
    <el-card shadow="never" class="level-card" v-loading="assessing">
      <template v-if="level.level">
        <div class="level-header">
          <el-tag :type="levelTagType" size="large">{{ level.level }}</el-tag>
          <span class="level-suggestion">{{ level.suggestion }}</span>
        </div>
        <el-row :gutter="20" style="margin-top: 16px">
          <el-col :span="8">
            <h4>已学知识点</h4>
            <el-tag v-for="t in level.topics" :key="t" size="small" style="margin: 2px">{{ t }}</el-tag>
            <span v-if="!level.topics?.length" class="empty-hint">暂无</span>
          </el-col>
          <el-col :span="8">
            <h4>擅长领域</h4>
            <el-tag v-for="s in level.strengths" :key="s" type="success" size="small" style="margin: 2px">{{ s }}</el-tag>
            <span v-if="!level.strengths?.length" class="empty-hint">暂无</span>
          </el-col>
          <el-col :span="8">
            <h4>薄弱领域</h4>
            <el-tag v-for="w in level.weaknesses" :key="w" type="danger" size="small" style="margin: 2px">{{ w }}</el-tag>
            <span v-if="!level.weaknesses?.length" class="empty-hint">暂无</span>
          </el-col>
        </el-row>
      </template>
      <template v-else>
        <el-empty description="暂无评估数据，请先生成习题">
          <el-button type="primary" @click="doAssess">评估知识水平</el-button>
        </el-empty>
      </template>
    </el-card>

    <!-- 习题设置 -->
    <el-card shadow="never" class="settings-card">
      <el-form inline>
        <el-form-item label="题型">
          <el-checkbox-group v-model="selectedTypes">
            <el-checkbox value="choice">选择题</el-checkbox>
            <el-checkbox value="true_false">判断题</el-checkbox>
            <el-checkbox value="fill_blank">填空题</el-checkbox>
          </el-checkbox-group>
        </el-form-item>
        <el-form-item label="题量">
          <el-input-number v-model="questionCount" :min="1" :max="20" size="small" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="doGenerate" :loading="generating" :disabled="!selectedTypes.length">
            生成习题
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 答题区 -->
    <el-card shadow="never" class="question-card" v-if="exercises.length && !showSummary">
      <!-- 进度 -->
      <div class="progress-bar">
        <span>第 {{ currentIndex + 1 }} / {{ exercises.length }} 题</span>
        <span class="right-count">已对：{{ correctCount }} 题</span>
      </div>

      <!-- 当前题目 -->
      <template v-if="currentQuestion">
        <div class="question-header">
          <el-tag size="small">{{ typeLabel(currentQuestion.question_type) }}</el-tag>
          <span class="topic" v-if="currentQuestion.topic">知识点：{{ currentQuestion.topic }}</span>
        </div>

        <div class="question-text">{{ currentQuestion.question }}</div>

        <!-- 选择题 -->
        <el-radio-group v-if="currentQuestion.question_type === 'choice'" v-model="userAnswer" class="options-group">
          <el-radio v-for="(opt, i) in currentQuestion.options" :key="i" :value="opt.charAt(0)" class="option-item">
            {{ opt }}
          </el-radio>
        </el-radio-group>

        <!-- 判断题 -->
        <el-radio-group v-if="currentQuestion.question_type === 'true_false'" v-model="userAnswer" class="options-group">
          <el-radio value="对" class="option-item">对</el-radio>
          <el-radio value="错" class="option-item">错</el-radio>
        </el-radio-group>

        <!-- 填空题 -->
        <el-input v-if="currentQuestion.question_type === 'fill_blank'" v-model="userAnswer"
          placeholder="请输入答案" style="max-width: 400px" />

        <!-- 提交按钮 -->
        <div style="margin-top: 20px" v-if="!answered">
          <el-button type="primary" @click="submitCurrent" :disabled="!userAnswer.trim()">
            提交答案
          </el-button>
        </div>

        <!-- 批改结果 -->
        <div v-if="answered" class="result-box" :class="{ correct: lastCorrect, wrong: !lastCorrect }">
          <div class="result-icon">{{ lastCorrect ? '✓ 正确！' : '✗ 错误' }}</div>
          <div v-if="!lastCorrect" class="correct-answer">正确答案：{{ lastCorrectAnswer }}</div>
          <div class="explanation" v-if="lastExplanation">
            <strong>解析：</strong>{{ lastExplanation }}
          </div>
          <el-button type="primary" @click="nextQuestion" style="margin-top: 12px">
            {{ currentIndex + 1 < exercises.length ? '下一题' : '查看结果' }}
          </el-button>
        </div>
      </template>
    </el-card>

    <!-- 结果汇总 -->
    <el-card shadow="never" class="summary-card" v-if="showSummary">
      <h3>🎉 答题完成！</h3>
      <el-row :gutter="20" class="summary-stats">
        <el-col :span="8">
          <el-statistic title="总分" :value="correctCount + ' / ' + exercises.length" />
        </el-col>
        <el-col :span="8">
          <el-statistic title="正确率" :value="accuracy + '%'" />
        </el-col>
        <el-col :span="8">
          <el-statistic title="水平评估" :value="level.level || '未知'" />
        </el-col>
      </el-row>

      <!-- 错题回顾 -->
      <div v-if="wrongQuestions.length" class="wrong-review">
        <h4>错题回顾</h4>
        <div v-for="wq in wrongQuestions" :key="wq.id" class="wrong-item">
          <el-tag size="small">{{ typeLabel(wq.question_type) }}</el-tag>
          <div class="wrong-question">{{ wq.question }}</div>
          <div class="wrong-answer">你的答案：<span class="wrong">{{ wq.userAnswer }}</span> | 正确答案：<span class="correct-text">{{ wq.correctAnswer }}</span></div>
          <div class="wrong-explanation" v-if="wq.explanation">{{ wq.explanation }}</div>
        </div>
      </div>

      <div style="margin-top: 20px">
        <el-button type="primary" @click="resetExercise">再来一组</el-button>
        <el-button @click="doAssess">重新评估水平</el-button>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { assessLevel, generateExercise, submitAnswer } from '../api/exercise'
import { getSessions } from '../api/chat'

// 知识水平
const assessing = ref(false)
const level = ref({})

// 习题设置
const selectedTypes = ref(['choice', 'true_false', 'fill_blank'])
const questionCount = ref(5)

// 习题状态
const generating = ref(false)
const exercises = ref([])
const currentIndex = ref(0)
const userAnswer = ref('')
const answered = ref(false)
const lastCorrect = ref(false)
const lastCorrectAnswer = ref('')
const lastExplanation = ref('')
const correctCount = ref(0)
const wrongQuestions = ref([])
const showSummary = ref(false)

// 当前题目
const currentQuestion = computed(() => exercises.value[currentIndex.value] || null)

// 正确率
const accuracy = computed(() => {
  if (!exercises.value.length) return 0
  return Math.round((correctCount.value / exercises.value.length) * 100)
})

// 水平标签颜色
const levelTagType = computed(() => {
  const map = { '初级': 'warning', '中级': '', '高级': 'success' }
  return map[level.value.level] || 'info'
})

// 题型名称
function typeLabel(type) {
  const map = { choice: '选择题', true_false: '判断题', fill_blank: '填空题' }
  return map[type] || type
}

// 获取 session_id
function getSessionId() {
  return localStorage.getItem('session_id') || ''
}

// 评估知识水平
async function doAssess() {
  const sid = getSessionId()
  if (!sid) {
    ElMessage.warning('请先在智能问答中进行对话')
    return
  }
  assessing.value = true
  try {
    const res = await assessLevel(sid)
    level.value = res.data || {}
  } catch {
    // error handled by interceptor
  } finally {
    assessing.value = false
  }
}

// 生成习题
async function doGenerate() {
  const sid = getSessionId()
  if (!sid) {
    ElMessage.warning('请先在智能问答中进行对话')
    return
  }
  generating.value = true
  showSummary.value = false
  exercises.value = []
  currentIndex.value = 0
  userAnswer.value = ''
  answered.value = false
  correctCount.value = 0
  wrongQuestions.value = []

  try {
    const res = await generateExercise(sid, selectedTypes.value, questionCount.value)
    exercises.value = res.data?.exercises || []
    if (res.data?.level) level.value = res.data.level
    if (!exercises.value.length) {
      ElMessage.warning('未能生成习题，请重试')
    }
  } catch {
    // error handled by interceptor
  } finally {
    generating.value = false
  }
}

// 提交当前题答案
async function submitCurrent() {
  if (!userAnswer.value.trim()) return
  const ex = currentQuestion.value
  if (!ex) return

  const sid = getSessionId()
  try {
    const res = await submitAnswer(sid, [{ exercise_id: ex.id, user_answer: userAnswer.value.trim() }])
    const result = res.data?.results?.[0] || {}
    lastCorrect.value = result.is_correct
    lastCorrectAnswer.value = result.correct_answer || ''
    lastExplanation.value = result.explanation || ''
    answered.value = true

    if (result.is_correct) {
      correctCount.value++
    } else {
      wrongQuestions.value.push({
        id: ex.id,
        question_type: ex.question_type,
        question: ex.question,
        userAnswer: userAnswer.value.trim(),
        correctAnswer: result.correct_answer,
        explanation: result.explanation,
      })
    }
  } catch {
    // error handled by interceptor
  }
}

// 下一题
function nextQuestion() {
  if (currentIndex.value + 1 < exercises.value.length) {
    currentIndex.value++
    userAnswer.value = ''
    answered.value = false
  } else {
    showSummary.value = true
  }
}

// 重置
function resetExercise() {
  showSummary.value = false
  exercises.value = []
  currentIndex.value = 0
  userAnswer.value = ''
  answered.value = false
  correctCount.value = 0
  wrongQuestions.value = []
}
</script>

<style scoped>
.exercise-page {
  padding: 0;
}
.exercise-page h2 {
  margin-bottom: 16px;
}
.level-card,
.settings-card,
.question-card,
.summary-card {
  margin-bottom: 16px;
}
.level-header {
  display: flex;
  align-items: center;
  gap: 12px;
}
.level-suggestion {
  color: #606266;
  font-size: 14px;
}
.empty-hint {
  color: #c0c4cc;
  font-size: 13px;
}
h4 {
  margin: 0 0 6px 0;
  font-size: 14px;
  color: #303133;
}
.progress-bar {
  display: flex;
  justify-content: space-between;
  margin-bottom: 16px;
  font-size: 14px;
  color: #909399;
}
.right-count {
  color: #67c23a;
}
.question-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
}
.topic {
  font-size: 13px;
  color: #909399;
}
.question-text {
  font-size: 16px;
  line-height: 1.8;
  margin-bottom: 20px;
}
.options-group {
  display: flex;
  flex-direction: column;
  gap: 10px;
}
.option-item {
  padding: 10px 14px;
  border: 1px solid #e4e7ed;
  border-radius: 6px;
  transition: border-color 0.2s;
}
.option-item:hover {
  border-color: #409eff;
}
.result-box {
  margin-top: 16px;
  padding: 16px;
  border-radius: 8px;
}
.result-box.correct {
  background: #f0f9eb;
  border: 1px solid #e1f3d8;
}
.result-box.wrong {
  background: #fef0f0;
  border: 1px solid #fde2e2;
}
.result-icon {
  font-size: 18px;
  font-weight: bold;
  margin-bottom: 8px;
}
.result-box.correct .result-icon {
  color: #67c23a;
}
.result-box.wrong .result-icon {
  color: #f56c6c;
}
.correct-answer {
  color: #67c23a;
  font-weight: bold;
  margin-bottom: 8px;
}
.explanation {
  color: #606266;
  line-height: 1.6;
}
.summary-stats {
  margin: 24px 0;
}
.wrong-review {
  margin-top: 24px;
  padding-top: 16px;
  border-top: 1px solid #e4e7ed;
}
.wrong-review h4 {
  margin-bottom: 12px;
  color: #f56c6c;
}
.wrong-item {
  padding: 12px;
  margin-bottom: 10px;
  background: #fef0f0;
  border-radius: 6px;
}
.wrong-question {
  margin: 8px 0;
  font-weight: 500;
}
.wrong-answer {
  font-size: 13px;
  color: #606266;
}
.wrong-answer .wrong {
  color: #f56c6c;
  text-decoration: line-through;
}
.wrong-answer .correct-text {
  color: #67c23a;
  font-weight: bold;
}
.wrong-explanation {
  margin-top: 6px;
  font-size: 13px;
  color: #909399;
}
</style>
