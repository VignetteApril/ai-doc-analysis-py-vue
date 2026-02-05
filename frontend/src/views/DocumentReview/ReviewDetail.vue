<template>
  <div class="h-full flex flex-col bg-[#f0f5ff] font-sans">
    <header class="h-16 bg-white/80 backdrop-blur-md border-b border-slate-200 px-8 flex items-center justify-between sticky top-0 z-50 shadow-sm">
      <div class="flex items-center gap-4">
        <button @click="$router.push('/review')" class="p-2 hover:bg-slate-100 rounded-full transition-colors text-slate-400">
          <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path d="M15 19l-7-7 7-7" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"/></svg>
        </button>
        <div class="h-6 w-[1px] bg-slate-200"></div>
        <h2 class="text-lg font-bold text-slate-800 tracking-tight">{{ documentName }}</h2>
      </div>
      <div class="flex items-center gap-3">
        <button class="px-5 py-2 border border-slate-200 text-[#1d70f5] rounded-xl text-sm font-medium hover:bg-blue-50 transition-all">取消</button>
        <button @click="handleSave" class="px-8 py-2 bg-[#1d70f5] text-white rounded-xl text-sm font-bold hover:bg-blue-700 shadow-lg shadow-blue-500/30 transition-all active:scale-95">保存文档</button>
      </div>
    </header>

    <div class="flex-1 flex overflow-hidden">
      <aside class="w-[400px] border-r border-slate-200 bg-white flex flex-col shadow-xl z-10">
        <div class="p-5 flex items-center justify-between border-b border-slate-50">
          <h3 class="font-bold text-slate-800 text-base">校对建议</h3>
          <button @click="showToast('正在重新分析...', 'info')" class="px-3 py-1 bg-[#1d70f5] text-white text-xs rounded-lg font-bold shadow-md shadow-blue-500/20 hover:scale-105 transition-transform">
            AI 重新分析
          </button>
        </div>

        <div class="flex-1 overflow-y-auto p-4 space-y-4 bg-slate-50/50">
          <div
            v-for="(sug, idx) in suggestions"
            :key="idx"
            class="suggestion-card bg-white rounded-2xl border border-slate-100 p-5 shadow-sm hover:shadow-md transition-all relative group cursor-pointer"
            :class="{'ring-2 ring-blue-500': activeId === idx}"
            @click="locateError(sug.original, idx)"
          >
            <div class="flex items-center justify-between mb-3">
              <span class="text-[10px] text-slate-400 font-mono bg-slate-50 px-2 py-0.5 rounded">#{{ idx + 1 }} {{ sug.type }}</span>
              <span :class="sug.source === 'AI分析' ? 'bg-blue-50 text-blue-500' : 'bg-orange-50 text-orange-500'" class="px-2 py-0.5 rounded text-[10px] font-bold">
                {{ sug.source }}
              </span>
            </div>
            <div class="space-y-1 mb-5">
              <p class="text-xs text-slate-400 line-through italic">原文：{{ sug.original }}</p>
              <p class="text-sm text-slate-700 font-medium">建议改为：<span class="text-[#1d70f5] font-bold text-base">{{ sug.content }}</span></p>
            </div>
            <div class="flex items-center justify-between border-t border-slate-50 pt-4">
              <div class="flex gap-2">
                <button @click.stop="handleIgnore(idx)" class="px-4 py-1.5 bg-slate-100 text-slate-500 text-xs rounded-lg hover:bg-slate-200 transition-colors font-medium">忽略</button>
                <button @click.stop="applyReplacement(idx)" class="px-4 py-1.5 bg-[#1d70f5] text-white text-xs rounded-lg hover:bg-blue-700 shadow-sm transition-colors font-bold">替换</button>
              </div>
              <button class="text-[#1d70f5] text-xs flex items-center gap-1 hover:bg-blue-50 px-2 py-1 rounded-md transition-colors font-medium">定位</button>
            </div>
          </div>
          <div v-if="suggestions.length === 0" class="flex flex-col items-center justify-center py-20 text-slate-400 opacity-60">
            <svg class="w-12 h-12 mb-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"/></svg>
            <p class="text-sm">暂无校对建议</p>
          </div>
        </div>

        <div class="p-4 border-t border-slate-100 bg-white grid grid-cols-2 gap-3 shrink-0">
          <button
            @click="handleIgnoreAll"
            :disabled="suggestions.length === 0"
            class="py-2.5 border border-slate-200 text-slate-500 rounded-xl text-xs font-bold hover:bg-slate-50 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            全部忽略
          </button>
          <button
            @click="applyAllReplacements"
            :disabled="suggestions.length === 0"
            class="py-2.5 bg-[#1d70f5] text-white rounded-xl text-xs font-bold hover:bg-blue-700 shadow-lg shadow-blue-500/20 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
          >
            全部替换
          </button>
        </div>
      </aside>

      <main class="flex-1 bg-[#f8faff] flex flex-col overflow-hidden">
        <Toolbar
          class="border-b border-slate-200 !bg-white px-4"
          :editor="editorRef"
          :defaultConfig="toolbarConfig"
          mode="default"
        />
        <div class="flex-1 overflow-y-auto p-10 flex justify-center">
          <div class="w-full max-w-4xl bg-white shadow-2xl min-h-full border border-slate-100 rounded-sm editor-paper">
            <Editor
              v-model="valueHtml"
              :defaultConfig="editorConfig"
              mode="default"
              class="h-full font-serif"
              @onCreated="handleCreated"
            />
          </div>
        </div>
      </main>
    </div>

    <Transition name="toast">
      <div v-if="toast.show" class="fixed top-24 left-1/2 -translate-x-1/2 z-[100] flex items-center gap-3 px-8 py-4 rounded-2xl shadow-2xl border backdrop-blur-md"
        :class="toast.type === 'success' ? 'bg-emerald-500/90 border-emerald-400 text-white' : (toast.type === 'info' ? 'bg-blue-500/90 border-blue-400 text-white' : 'bg-red-500/90 border-red-400 text-white')">
        <span class="font-bold text-sm">{{ toast.message }}</span>
      </div>
    </Transition>
  </div>
</template>

<script setup>
import '@wangeditor/editor/dist/css/style.css'
import { onBeforeUnmount, ref, shallowRef, reactive, onMounted } from 'vue'
import { Editor, Toolbar } from '@wangeditor/editor-for-vue'
import { useRoute } from 'vue-router'

const route = useRoute()
const documentName = ref('数字化转型方案.docx')
const activeId = ref(null)

// --- 编辑器核心状态 ---
const editorRef = shallowRef()
const valueHtml = ref('')
const toolbarConfig = { excludeKeys: ['fullScreen', 'group-image', 'group-video', 'insertTable', 'codeBlock'] }
const editorConfig = { placeholder: '正文加载中...', scroll: false }

// 模拟 AI 建议数据 [cite: 2026-02-05]
const suggestions = ref([
  { type: '语法错误', content: '行动', original: '心动', source: 'AI分析' },
  { type: '标点连用', content: '删除“，”', original: '，，', source: 'AI分析' },
  { type: '重复用词', content: '删除“增长”', original: '增长增长', source: 'AI分析' },
  { type: '推荐替换', content: '稳中向好', original: '回稳', source: '词库' }
])

// --- 逻辑方法 ---

const handleCreated = (editor) => {
  editorRef.value = editor
  // 模拟初始化数据
  valueHtml.value = `<p style="text-align: center;"><span style="font-size: 22px;"><strong>关于印发2024年数字化转型方案的通知</strong></span></p>
  <p>各部委：党的十八大以来，我们不断提供<strong>心动</strong>指南。我们要关注新增长<strong>增长增长</strong>点。消费<strong>，，</strong>餐饮热度上升。我国经济<strong>回稳</strong>之势确立。</p>`
}

// 替换单条逻辑 [cite: 2026-02-05]
const applyReplacement = (id) => {
  const s = suggestions.value[id]
  const editor = editorRef.value
  if (!editor) return

  const html = editor.getHtml()
  const newHtml = html.replace(new RegExp(s.original, 'g'), `<span style="color: #1d70f5; font-weight: bold;">${s.content}</span>`)
  editor.setHtml(newHtml)

  suggestions.value.splice(id, 1)
  showToast('内容已成功替换并同步更新')
}

// ✅ 核心功能：全部替换逻辑
const applyAllReplacements = () => {
  const editor = editorRef.value
  if (!editor || suggestions.value.length === 0) return

  let currentHtml = editor.getHtml()
  suggestions.value.forEach(s => {
    currentHtml = currentHtml.replace(new RegExp(s.original, 'g'), `<span style="color: #1d70f5; font-weight: bold;">${s.content}</span>`)
  })

  editor.setHtml(currentHtml)
  suggestions.value = [] // 清空建议列表
  showToast('已完成全部内容的智能替换', 'success')
}

// ✅ 核心功能：全部忽略逻辑
const handleIgnoreAll = () => {
  suggestions.value = []
  showToast('已忽略所有修改建议', 'info')
}

const handleIgnore = (id) => {
  suggestions.value.splice(id, 1)
  showToast('已忽略建议', 'info')
}

const locateError = (text, id) => {
  activeId.value = id
  const editor = editorRef.value
  if (editor) {
    // wangEditor 提供的选择文本功能
    editor.select(text)
    showToast(`正在定位：${text}`, 'info')
  }
}

// Toast 系统
const toast = reactive({ show: false, message: '', type: 'success' })
const showToast = (msg, type = 'success') => {
  toast.message = msg; toast.type = type; toast.show = true
  setTimeout(() => toast.show = false, 3000)
}

const handleSave = () => {
  showToast('文档已安全保存至云端', 'success')
}

onBeforeUnmount(() => {
  const editor = editorRef.value
  if (editor) editor.destroy()
})
</script>

<style scoped>
/* 定制编辑器样式 */
:deep(.w-e-text-container) { background-color: transparent !important; border: none !important; }
.font-serif :deep(.w-e-text-container [contenteditable]) {
  font-family: "FangSong", "仿宋", serif;
  line-height: 2.2 !important;
  padding: 40px 60px !important;
}

.suggestion-card { transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1); }
.suggestion-card:hover { transform: translateY(-3px); }

/* Toast 动画 (保持不变) */
.toast-enter-active { animation: toast-in 0.4s ease-out; }
.toast-leave-active { transition: opacity 0.3s; }
.toast-leave-to { opacity: 0; }
@keyframes toast-in {
  from { opacity: 0; transform: translate(-50%, 20px); }
  to { opacity: 1; transform: translate(-50%, 0); }
}
</style>