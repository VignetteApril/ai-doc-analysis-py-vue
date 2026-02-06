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
        <button @click="handleDownload" class="px-5 py-2 border border-slate-200 text-[#1d70f5] rounded-xl text-sm font-medium hover:bg-blue-50 transition-all">下载成品</button>
        <button @click="handleSave" class="px-8 py-2 bg-[#1d70f5] text-white rounded-xl text-sm font-bold hover:bg-blue-700 shadow-lg shadow-blue-500/30 transition-all active:scale-95">
          保存草稿
        </button>
      </div>
    </header>

    <div class="flex-1 flex overflow-hidden">
      <aside class="w-[400px] border-r border-slate-200 bg-white flex flex-col shadow-xl z-10 relative">
        <div class="p-5 flex items-center justify-between border-b border-slate-50">
          <h3 class="font-bold text-slate-800 text-base">校对建议</h3>
          <button
            @click="handleStartAI"
            :disabled="analyzing || loading"
            class="px-4 py-1.5 bg-[#1d70f5] text-white text-xs rounded-lg font-bold shadow-md shadow-blue-500/20 hover:scale-105 transition-all disabled:opacity-50 disabled:scale-100"
          >
            <span v-if="analyzing" class="flex items-center gap-2">
              <div class="w-3 h-3 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
              分析中...
            </span>
            <span v-else>AI 深度分析</span>
          </button>
        </div>

        <div class="flex-1 overflow-y-auto p-4 space-y-4 bg-slate-50/50 relative">
          <div v-if="analyzing" class="absolute inset-0 z-20 bg-white/60 backdrop-blur-[2px] flex flex-col items-center justify-center p-10 text-center">
            <div class="w-12 h-12 border-4 border-[#1d70f5] border-t-transparent rounded-full animate-spin mb-4"></div>
            <p class="text-sm text-slate-600 font-bold">豆包 AI 正在扫描</p>
          </div>

          <div v-if="suggestions.length === 0 && !analyzing" class="flex flex-col items-center justify-center h-full opacity-40">
            <svg class="w-16 h-16 text-slate-300" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path d="M13 10V3L4 14h7v7l9-11h-7z" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"/></svg>
            <p class="text-sm font-medium mt-4">等待开启 AI 分析</p>
          </div>

          <div
            v-for="(sug, idx) in suggestions"
            :key="idx"
            class="suggestion-card bg-white rounded-2xl border border-slate-100 p-5 shadow-sm hover:shadow-md transition-all cursor-pointer"
            @click="locateError(sug.original)"
          >
            <div class="flex items-center justify-between mb-3">
              <span class="text-[10px] text-slate-400 font-mono bg-slate-50 px-2 py-0.5 rounded">#{{ idx + 1 }} {{ sug.type }}</span>
              <span class="bg-blue-50 text-blue-500 px-2 py-0.5 rounded text-[10px] font-bold">AI分析</span>
            </div>
            <div class="space-y-1 mb-5">
              <p class="text-xs text-slate-400 line-through italic">原文：{{ sug.original }}</p>
              <p class="text-sm text-slate-700 font-medium leading-relaxed">建议：<span class="text-[#1d70f5] font-bold text-base">{{ sug.content }}</span></p>
            </div>
            <div class="flex items-center gap-2 border-t border-slate-50 pt-4">
              <button @click.stop="handleIgnore(idx)" class="flex-1 py-1.5 bg-slate-100 text-slate-500 text-xs rounded-lg hover:bg-slate-200 font-medium">忽略</button>
              <button @click.stop="applyReplacement(idx)" class="flex-[2] py-1.5 bg-[#1d70f5] text-white text-xs rounded-lg hover:bg-blue-700 shadow-sm font-bold">确认修改</button>
            </div>
          </div>
        </div>
      </aside>

      <main class="flex-1 bg-slate-100/50 flex flex-col overflow-hidden">
        <Toolbar class="border-b border-slate-200 !bg-white px-4 shrink-0" :editor="editorRef" :defaultConfig="toolbarConfig" mode="default" />
        <div class="flex-1 overflow-y-auto p-10 flex justify-center">
          <div class="w-full max-w-4xl bg-white shadow-2xl min-h-[1100px] border border-slate-100 rounded-sm editor-paper relative">
            <Editor
              v-model="valueHtml"
              :defaultConfig="editorConfig"
              mode="default"
              style="height: 1100px; overflow-y: hidden;"
              @onCreated="handleCreated"
            />

            <div v-if="loading" class="absolute inset-0 z-50 bg-white flex flex-col items-center justify-center">
               <div class="w-10 h-10 border-4 border-[#1d70f5] border-t-transparent rounded-full animate-spin mb-4"></div>
               <p class="text-sm text-slate-400 tracking-widest font-bold">正在构建公文排版引擎...</p>
            </div>
          </div>
        </div>
      </main>
    </div>

    <Transition name="toast">
      <div v-if="toast.show" class="fixed top-24 left-1/2 -translate-x-1/2 z-[100] flex items-center gap-3 px-8 py-4 rounded-2xl shadow-2xl border backdrop-blur-md transition-all"
        :class="toast.type === 'success' ? 'bg-emerald-500/90 border-emerald-400 text-white' : 'bg-blue-500/90 border-blue-400 text-white'">
        <span class="font-bold text-sm">{{ toast.message }}</span>
      </div>
    </Transition>
  </div>
</template>

<script setup>
import '@wangeditor/editor/dist/css/style.css'
import { onBeforeUnmount, ref, shallowRef, reactive, onMounted, nextTick } from 'vue'
import { Editor, Toolbar } from '@wangeditor/editor-for-vue'
import { useRoute } from 'vue-router'
import { getDocumentDetail, saveDocumentContent, downloadDocumentFile, analyzeDocumentAI } from '@/api/review'

const route = useRoute()
const editorRef = shallowRef()
const valueHtml = ref('') // 保持为空，等实例好了再注入
const documentName = ref('加载中...')
const suggestions = ref([])
const analyzing = ref(false)
const loading = ref(true)

// 用于缓存后端传回的 HTML
let remoteContent = ''

const toolbarConfig = { excludeKeys: ['fullScreen', 'group-video', 'insertTable', 'codeBlock'] }
const editorConfig = {
  placeholder: '正文加载中...',
  autoFocus: false, // 禁止自动聚焦，防止路径计算冲突
  scroll: false
}

/**
 * 核心逻辑：获取详情 [cite: 2026-02-05]
 */
const fetchBasicDetail = async () => {
  loading.value = true
  try {
    const res = await getDocumentDetail(route.params.id)
    documentName.value = res.name
    remoteContent = res.content || '<p>文件内容为空</p>'

    // 如果这时候 Editor 实例已经创建成功，直接注入
    if (editorRef.value) {
      injectContent()
    }
  } catch (error) {
    showToast('获取内容失败', 'error')
    loading.value = false
  }
}

/**
 * 核心逻辑：手动注入 HTML 以规避 Slate 路径错误 [cite: 2026-02-05]
 */
const injectContent = () => {
  if (!editorRef.value || !remoteContent) return

  // 绕过 v-model 直接操作实例
  editorRef.value.setHtml(remoteContent)

  // 给 UI 渲染一点缓冲时间
  nextTick(() => {
    loading.value = false
    showToast('公文解析成功', 'success')
  })
}

/**
 * 编辑器创建回调
 */
const handleCreated = (editor) => {
  editorRef.value = editor
  // 如果 API 响应快于编辑器创建，在此处执行注入
  if (remoteContent) {
    injectContent()
  }
}

/**
 * 触发 AI 分析
 */
const handleStartAI = async () => {
  if (analyzing.value) return
  analyzing.value = true
  suggestions.value = []
  try {
    // 步骤 A: 同步当前内容
    const html = editorRef.value.getHtml()
    await saveDocumentContent(route.params.id, html)
    // 步骤 B: 调用 AI
    const res = await analyzeDocumentAI(route.params.id)
    suggestions.value = res.suggestions
    showToast(`AI 分析完成`, 'success')
  } catch (error) {
    showToast('AI 分析异常', 'error')
  } finally {
    analyzing.value = false
  }
}

/**
 * 保存草稿
 */
const handleSave = async () => {
  if (!editorRef.value) return
  try {
    await saveDocumentContent(route.params.id, editorRef.value.getHtml())
    showToast('已保存至云端', 'success')
  } catch (error) { showToast('保存失败', 'error') }
}

/**
 * 下载文档
 */
const handleDownload = async () => {
  showToast('正在生成文档...', 'info')
  try {
    const blob = await downloadDocumentFile(route.params.id)
    const url = window.URL.createObjectURL(new Blob([blob]))
    const a = document.createElement('a')
    a.href = url; a.download = `校核版_${documentName.value}.docx`
    a.click(); window.URL.revokeObjectURL(url)
  } catch (e) { showToast('导出失败', 'error') }
}

/**
 * 替换建议
 */
const applyReplacement = (idx) => {
  const s = suggestions.value[idx]
  const editor = editorRef.value
  if (!editor) return
  const html = editor.getHtml()
  const newHtml = html.replace(new RegExp(s.original, 'g'), `<span style="color: #1d70f5; background-color: #eef6ff; font-weight: bold;">${s.content}</span>`)
  editor.setHtml(newHtml)
  suggestions.value.splice(idx, 1)
}

const handleIgnore = (idx) => { suggestions.value.splice(idx, 1) }

// Toast 系统
const toast = reactive({ show: false, message: '', type: 'success' })
const showToast = (msg, type = 'success') => {
  toast.message = msg; toast.type = type; toast.show = true
  setTimeout(() => toast.show = false, 3000)
}

// 生命周期挂载
onMounted(() => {
  fetchBasicDetail()
})

onBeforeUnmount(() => {
  const editor = editorRef.value
  if (editor == null) return
  editor.destroy()
})
</script>

<style scoped>
/* 深度选择器强制覆盖 wangEditor 内部表格样式 [cite: 2026-02-05] */
:deep(.w-e-text-container table) {
  border-collapse: collapse;
  width: 100% !important;
  margin: 10px 0;
}
:deep(.w-e-text-container td), :deep(.w-e-text-container th) {
  border: 1px solid #d1d5db !important;
  padding: 12px !important;
  min-width: 40px;
}

/* 强制高度解决报错 */
:deep(.w-e-text-container) {
  min-height: 1100px !important;
  background-color: transparent !important;
  border: none !important;
}

.font-serif :deep(.w-e-text-container [contenteditable]) {
  font-family: "FangSong", "仿宋", serif;
  line-height: 1.8;
  padding: 60px 90px !important;
}

.editor-paper {
  background-color: white;
  transition: box-shadow 0.3s ease;
}

.suggestion-card { transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1); }
.suggestion-card:hover { transform: translateY(-4px); box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1); }

.toast-enter-active { animation: toast-in 0.4s ease-out; }
@keyframes toast-in {
  from { opacity: 0; transform: translate(-50%, 20px); }
  to { opacity: 1; transform: translate(-50%, 0); }
}
</style>