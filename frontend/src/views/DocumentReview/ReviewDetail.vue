<template>
  <div class="h-full flex flex-col bg-white font-sans overflow-hidden">
    <!-- 顶部栏 -->
    <header class="h-14 bg-white border-b border-slate-100 px-6 flex items-center justify-between z-50 shrink-0">
      <div class="flex items-center gap-4">
        <button @click="$router.push('/review')" class="p-1.5 hover:bg-slate-100 rounded-md text-slate-500 transition-colors">
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path d="M10 19l-7-7m0 0l7-7m-7 7h18" stroke-width="2" stroke-linecap="round"/>
          </svg>
        </button>
        <div class="flex items-center gap-2">
          <span class="text-xl">📄</span>
          <h2 class="text-sm font-medium text-slate-800">{{ documentName }}</h2>
          <div v-if="analyzing" class="flex items-center gap-2 px-3 py-1 bg-purple-50 text-purple-600 rounded-full text-xs font-bold animate-pulse">
            <div class="w-2 h-2 bg-purple-500 rounded-full"></div>
            AI 正在深度校阅...
          </div>
        </div>
      </div>

      <div class="flex gap-2">
        <button @click="handleStartAI" :disabled="analyzing"
          class="flex items-center gap-2 px-5 py-1.5 bg-black text-white text-xs font-medium rounded-full hover:bg-slate-800 transition-all disabled:opacity-50 shadow-md">
          <span v-if="analyzing">✨ 分析中...</span>
          <span v-else>✨ AI 深度校阅</span>
        </button>
        <button @click="handleSave" class="px-4 py-1.5 text-slate-600 text-xs font-medium hover:bg-slate-100 rounded-full transition-colors">保存</button>
        <button @click="handleDownload" class="px-4 py-1.5 text-slate-600 text-xs font-medium hover:bg-slate-100 rounded-full transition-colors">导出</button>
      </div>
    </header>

    <!-- 编辑器主体 -->
    <main class="flex-1 overflow-y-auto relative bg-[#f9f9fb] flex justify-center cursor-text" @click.self="editor?.commands.focus()">
      <div class="w-full max-w-3xl my-12 bg-white shadow-sm border border-slate-200 min-h-[1000px] px-16 py-12 relative rounded-lg">
        <editor-content :editor="editor" class="editor-content-wrapper" />

        <!-- BubbleMenu（AI 建议气泡） -->
        <bubble-menu
          v-if="editor"
          :editor="editor"
          :tippy-options="{ duration: 120, placement: 'bottom-start', maxWidth: 420, zIndex: 999 }"
          :should-show="shouldShowBubble"
          class="ai-bubble-menu"
        >
          <div class="bg-white rounded-2xl shadow-2xl border border-slate-200 overflow-hidden w-[380px]">
            <!-- 头部 -->
            <div class="flex items-center justify-between px-4 py-3 border-b bg-slate-50">
              <span class="text-xs font-bold text-slate-500 uppercase tracking-widest flex items-center gap-1.5">
                🤖 AI 校阅建议
              </span>
              <div class="flex items-center gap-3 text-xs text-slate-400">
                <button @click="navigateIssue(-1)" :disabled="currentIssueIndex <= 0" class="hover:text-slate-600 disabled:opacity-50">←</button>
                <span>{{ currentIssueIndex + 1 }} / {{ suggestions.length }}</span>
                <button @click="navigateIssue(1)" :disabled="currentIssueIndex >= suggestions.length - 1" class="hover:text-slate-600 disabled:opacity-50">→</button>
              </div>
            </div>

            <!-- 内容 -->
            <div class="p-5 bg-slate-50">
              <div class="text-xs text-slate-400 mb-1">原文片段</div>
              <div class="text-sm text-slate-600 line-through bg-white p-3 rounded-lg border border-rose-100 mb-4">
                {{ currentIssue?.original || '' }}
              </div>

              <div class="text-xs text-slate-400 mb-1 flex justify-between">
                <span>建议修改为</span>
              </div>
              <div class="text-sm font-medium text-emerald-700 bg-emerald-50 p-3 rounded-lg border border-emerald-100">
                {{ currentIssue?.content || '（建议删除此内容）' }}
              </div>

              <div v-if="currentIssue?.message" class="mt-4 text-xs text-slate-500 italic">
                “{{ currentIssue.message }}”
              </div>
            </div>

            <!-- 操作按钮 -->
            <div class="p-3 grid grid-cols-2 gap-2 border-t">
              <button @click="rejectSuggestion"
                class="py-3 rounded-xl text-sm font-medium text-slate-600 hover:bg-slate-100 flex items-center justify-center gap-2">
                <span>忽略</span>
              </button>
              <button @click="acceptSuggestion"
                class="py-3 rounded-xl text-sm font-medium bg-black text-white hover:bg-slate-800 flex items-center justify-center gap-2">
                采纳建议
              </button>
            </div>
          </div>
        </bubble-menu>
      </div>

      <!-- 底部进度 -->
      <div v-if="analyzing" class="fixed bottom-8 left-1/2 -translate-x-1/2 bg-slate-900/95 text-white px-6 py-3 rounded-2xl shadow-2xl flex items-center gap-4 z-50">
        <div class="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin"></div>
        <span class="text-sm">{{ currentStatusMsg }}...</span>
        <span class="text-xs text-slate-400">{{ progressPercent }}%</span>
      </div>
    </main>

    <!-- Toast -->
    <transition name="toast">
      <div v-if="toast.show" class="fixed top-6 left-1/2 -translate-x-1/2 z-[200] px-5 py-2.5 rounded-2xl shadow-xl bg-white border text-sm flex items-center gap-2">
        <span :class="toast.type === 'success' ? 'text-emerald-500' : 'text-rose-500'">●</span>
        {{ toast.message }}
      </div>
    </transition>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, onBeforeUnmount, nextTick } from 'vue'
import { useRoute } from 'vue-router'
import { useEditor, EditorContent } from '@tiptap/vue-3'
import { BubbleMenu } from '@tiptap/vue-3/menus'
import StarterKit from '@tiptap/starter-kit'
import { TextStyle } from '@tiptap/extension-text-style'
import { Color } from '@tiptap/extension-color'
import { Mark, mergeAttributes } from '@tiptap/core'

import {
  getDocumentDetail,
  saveDocumentContent,
  downloadDocumentFile,
  analyzeDocumentAI
} from '@/api/review'

// ==================== 自定义 Mark ====================
const AiCorrection = Mark.create({
  name: 'aiCorrection',
  keepOnSplit: false,
  addAttributes() {
    return { 'data-ai-id': { default: null } }
  },
  parseHTML() {
    return [{ tag: 'span.ai-correction-mark' }]
  },
  renderHTML({ HTMLAttributes }) {
    return ['span', mergeAttributes({ class: 'ai-correction-mark' }, HTMLAttributes), 0]
  },
})

// ==================== 响应式数据 ====================
const route = useRoute()
const documentName = ref('加载中...')
const suggestions = ref([])
const analyzing = ref(false)
const currentStatusMsg = ref('')
const progressPercent = ref(0)

const toast = reactive({ show: false, message: '', type: 'success' })

const currentIssueId = ref(null)
const currentIssue = computed(() => suggestions.value.find(s => s.id === currentIssueId.value))
const currentIssueIndex = computed(() => suggestions.value.findIndex(s => s.id === currentIssueId.value))

// ==================== Tiptap 编辑器 ====================
const editor = useEditor({
  content: '',
  extensions: [
    StarterKit,
    TextStyle,
    Color,
    AiCorrection
  ],
  editorProps: {
    attributes: {
      class: 'prose prose-lg max-w-none focus:outline-none font-serif leading-relaxed text-slate-800'
    },
    handleClick(view, pos) {
      const node = view.state.doc.nodeAt(pos)
      if (!node) return
      const mark = node.marks.find(m => m.type.name === 'aiCorrection')
      if (mark && mark.attrs['data-ai-id']) {
        currentIssueId.value = mark.attrs['data-ai-id']
      }
    }
  },
  onSelectionUpdate({ editor: e }) {
    const { from } = e.state.selection
    const node = e.state.doc.nodeAt(from)
    if (node) {
      const mark = node.marks.find(m => m.type.name === 'aiCorrection')
      if (mark && mark.attrs['data-ai-id']) {
        currentIssueId.value = mark.attrs['data-ai-id']
      }
    }
  },
  onUpdate() {
    if (suggestions.value.length > 0 && !currentIssueId.value) {
      nextTick(() => {
        currentIssueId.value = suggestions.value[0].id
        const el = document.querySelector(`span[data-ai-id="${suggestions.value[0].id}"]`)
        if (el) el.scrollIntoView({ behavior: 'smooth', block: 'center' })
      })
    }
  }
})

// BubbleMenu 显示条件
const shouldShowBubble = ({ editor: e }) => {
  return e.isActive('aiCorrection')
}

// ==================== 操作方法 ====================
const acceptSuggestion = () => {
  const sug = currentIssue.value
  if (!sug || !editor.value) return

  editor.value.chain().focus().command(({ tr, dispatch }) => {
    let found = false
    editor.value.state.doc.descendants((node, pos) => {
      if (found) return false
      const mark = node.marks.find(m => m.type.name === 'aiCorrection' && m.attrs['data-ai-id'] === sug.id)
      if (mark) {
        const from = pos
        const to = pos + node.nodeSize
        tr.deleteRange(from, to)
        if (sug.content) {
          tr.insertText(sug.content, from)
          tr.addMark(from, from + sug.content.length, editor.value.state.schema.marks.textStyle.create({ color: '#1e40af' }))
        }
        found = true
      }
    })
    if (dispatch && found) dispatch(tr)
    return found
  }).run()

  suggestions.value = suggestions.value.filter(s => s.id !== sug.id)
  showToast('✅ 已采纳建议', 'success')
}

const rejectSuggestion = () => {
  const sug = currentIssue.value
  if (!sug || !editor.value) return

  editor.value.chain().focus().command(({ tr, dispatch }) => {
    editor.value.state.doc.descendants((node, pos) => {
      const mark = node.marks.find(m => m.type.name === 'aiCorrection' && m.attrs['data-ai-id'] === sug.id)
      if (mark) tr.removeMark(pos, pos + node.nodeSize, mark)
    })
    if (dispatch) dispatch(tr)
    return true
  }).run()

  suggestions.value = suggestions.value.filter(s => s.id !== sug.id)
  showToast('已忽略', 'success')
}

const navigateIssue = (step) => {
  let idx = currentIssueIndex.value + step
  if (idx < 0) idx = 0
  if (idx >= suggestions.value.length) idx = suggestions.value.length - 1
  if (suggestions.value.length === 0) return

  const targetId = suggestions.value[idx].id
  currentIssueId.value = targetId

  nextTick(() => {
    const el = document.querySelector(`span[data-ai-id="${targetId}"]`)
    if (el) el.scrollIntoView({ behavior: 'smooth', block: 'center' })
  })
}

// ==================== AI 校阅（超级鲁棒版：强制从任何地方提取字符串） ====================
const handleStartAI = async () => {
  analyzing.value = true
  suggestions.value = []
  currentIssueId.value = null
  progressPercent.value = 0
  currentStatusMsg.value = "正在启动 AI 校阅..."

  try {
    const rawHtml = editor.value.getHTML()
    const res = await analyzeDocumentAI(route.params.id, rawHtml)

    console.log('Axios 完整响应:', res)

    // 强制把响应转成字符串（兼容所有情况）
    let text = ''
    if (res.data) {
      text = String(res.data)
    } else if (res) {
      text = String(res)
    }

    console.log('强制转字符串后的响应:', text.substring(0, 500) + '...') // 只打印前500字符

    if (!text || text.trim() === '') {
      throw new Error('响应内容为空')
    }

    // 最宽松的提取：所有 "data: " 后面的内容，直到下一个 "data:" 或结尾
    const dataMatches = text.match(/data:\s*([\s\S]*?)(?=data:|$)/g) || []
    console.log('提取到的原始 data 块数量:', dataMatches.length)
    console.log('提取到的 data 块示例:', dataMatches)

    let completePayload = null

    for (let block of dataMatches) {
      let jsonStr = block.replace(/^data:\s*/, '').trim()
      let payload
      try {
        payload = JSON.parse(jsonStr)
      } catch (e) {
        console.warn('解析失败，尝试清理块:', jsonStr.substring(0, 200))
        // 额外清理：去除可能的换行或多余字符
        jsonStr = jsonStr.replace(/[\r\n]+/g, ' ')
        try {
          payload = JSON.parse(jsonStr)
        } catch (e2) {
          continue
        }
      }

      if (payload.step === 'complete') {
        completePayload = payload
      } else if (payload.step) {
        currentStatusMsg.value = payload.desc || payload.step
        progressPercent.value = Math.min(progressPercent.value + 20, 95)
      }
    }

    if (completePayload && completePayload.results) {
      const { final_issues, final_html } = completePayload.results
      if (final_html) {
        editor.value.commands.setContent(final_html, false)
        suggestions.value = final_issues || []
        progressPercent.value = 100
        showToast(`校阅完成，发现 ${final_issues?.length || 0} 处问题`, 'success')

        nextTick(() => {
          if (suggestions.value.length > 0) {
            navigateIssue(0)
          }
        })
      } else {
        throw new Error('final_html 为空')
      }
    } else {
      throw new Error('未找到 complete 结果，可能解析失败')
    }
  } catch (err) {
    console.error('AI 校阅最终失败:', err)
    showToast('校阅失败：' + (err.message || '未知错误'), 'error')
  } finally {
    analyzing.value = false
  }
}

// ==================== 其他方法 ====================
const fetchBasicDetail = async () => {
  try {
    const res = await getDocumentDetail(route.params.id)
    documentName.value = res.name || '未命名文档'
    editor.value?.commands.setContent(res.content_html || res.content || '')
  } catch (e) {
    showToast('文档加载失败', 'error')
  }
}

const handleSave = async () => {
  let html = editor.value.getHTML()
  html = html.replace(/<span[^>]*class="ai-correction-mark"[^>]*>([\s\S]*?)<\/span>/g, '$1')
  await saveDocumentContent(route.params.id, html)
  showToast('保存成功', 'success')
}

const handleDownload = async () => {
  const blob = await downloadDocumentFile(route.params.id)
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `${documentName.value}_校核版.docx`
  a.click()
  URL.revokeObjectURL(url)
}

const showToast = (msg, type = 'success') => {
  toast.message = msg
  toast.type = type
  toast.show = true
  setTimeout(() => { toast.show = false }, 3000)
}

// ==================== 生命周期 ====================
onMounted(() => {
  fetchBasicDetail()
})

onBeforeUnmount(() => {
  editor.value?.destroy()
})
</script>

<style scoped>
:deep(.ai-correction-mark) {
  background-color: #fefce8;
  border-bottom: 2px dashed #eab308;
  padding: 1px 2px;
  cursor: pointer;
  border-radius: 2px;
  transition: all 0.2s;
}

:deep(.ai-correction-mark:hover) {
  background-color: #fde047;
  border-bottom-style: solid;
}

.ai-bubble-menu {
  z-index: 9999;
}

.toast-enter-active { animation: toastIn 0.3s ease; }
@keyframes toastIn {
  from { opacity: 0; transform: translate(-50%, -10px); }
  to { opacity: 1; transform: translate(-50%, 0); }
}
</style>