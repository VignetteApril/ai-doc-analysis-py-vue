<template>
  <div class="h-full flex flex-col bg-[#F9F9FB] font-sans overflow-hidden">
    <header class="sticky top-0 h-14 bg-white border-b border-slate-200 px-6 flex items-center justify-between z-[1000] shrink-0">
      <div class="flex items-center gap-4">
        <button @click="$router.push('/review')" class="p-2 hover:bg-slate-100 rounded-lg text-slate-500 transition-colors">
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path d="M10 19l-7-7m0 0l7-7m-7 7h18" stroke-width="2" stroke-linecap="round"/>
          </svg>
        </button>
        <div class="flex items-center gap-3">
          <div class="w-8 h-8 bg-blue-50 text-blue-600 rounded-lg flex items-center justify-center text-sm font-bold">
            DOC
          </div>
          <h2 class="text-sm font-semibold text-slate-800">{{ documentName }}</h2>
        </div>
      </div>

      <div class="flex gap-3">
        <button @click="handleStartAI" :disabled="analyzing"
          class="flex items-center gap-2 px-4 py-2 bg-black text-white text-xs font-semibold rounded-lg hover:bg-slate-800 transition-all disabled:opacity-50 shadow-sm active:scale-95">
          <span v-if="analyzing" class="flex items-center gap-2">
             <span class="w-2 h-2 bg-green-400 rounded-full animate-pulse"></span>
             <span>分析中...</span>
          </span>
          <span v-else>✨ AI 深度校阅</span>
        </button>
        <div class="h-8 w-px bg-slate-200"></div>
        <button @click="handleSave" class="px-4 py-2 text-slate-600 text-xs font-semibold hover:bg-slate-100 rounded-lg transition-colors">保存</button>
        <button @click="handleDownload" class="px-4 py-2 text-slate-600 text-xs font-semibold hover:bg-slate-100 rounded-lg transition-colors">导出</button>
      </div>
    </header>

    <main class="flex-1 overflow-y-auto flex justify-center p-6 relative scroll-smooth" @click.self="editor?.commands.focus()">

      <div class="w-full max-w-[850px] bg-white rounded-xl shadow-sm border border-slate-200 flex flex-col h-fit min-h-[900px]">

        <div v-if="editor" class="sticky top-0 z-50 bg-white/95 backdrop-blur-sm border-b border-slate-100 px-4 py-2 rounded-t-xl flex items-center flex-wrap gap-1 transition-all">

          <div class="flex items-center gap-0.5 pr-2 border-r border-slate-200 mr-2">
            <button @click="editor.chain().focus().undo().run()" :disabled="!editor.can().undo()" :class="toolbarItemClass">
              <svg class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 7v6h6"/><path d="M21 17a9 9 0 0 0-9-9 9 9 0 0 0-6 2.3L3 13"/></svg>
            </button>
            <button @click="editor.chain().focus().redo().run()" :disabled="!editor.can().redo()" :class="toolbarItemClass">
              <svg class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 7v6h-6"/><path d="M3 17a9 9 0 0 1 9-9 9 9 0 0 1 6 2.3l3 3.7"/></svg>
            </button>
          </div>

          <div class="relative mr-2" ref="headingDropdownRef">
            <button @click="toggleHeadingDropdown" :class="[toolbarItemClass, 'w-auto px-2 gap-2 min-w-[100px] justify-between']">
              <span class="text-xs font-medium truncate">{{ currentFontSizeLabel }}</span>
              <svg class="w-3 h-3 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"/></svg>
            </button>

            <div v-if="showHeadingDropdown" class="absolute top-full left-0 mt-1 w-48 bg-white border border-slate-200 rounded-lg shadow-xl py-1 z-50 flex flex-col">
              <button @click="setTextStyle('normal')" :class="[dropdownItemClass]">
                <span class="text-lg w-6 text-center text-slate-400">T</span>
                <span class="text-sm">正文 (默认)</span>
              </button>
              <button @click="setTextStyle('large')" :class="[dropdownItemClass]">
                <span class="text-xl w-6 text-center font-bold text-slate-800">Aa</span>
                <span class="text-sm font-bold">大标题 (30px)</span>
              </button>
              <button @click="setTextStyle('medium')" :class="[dropdownItemClass]">
                <span class="text-lg w-6 text-center font-bold text-slate-800">Aa</span>
                <span class="text-sm font-bold">中标题 (24px)</span>
              </button>
              <button @click="setTextStyle('small')" :class="[dropdownItemClass]">
                <span class="text-base w-6 text-center font-bold text-slate-800">Aa</span>
                <span class="text-sm font-bold">小标题 (20px)</span>
              </button>
            </div>

            <div v-if="showHeadingDropdown" @click="showHeadingDropdown = false" class="fixed inset-0 z-40 bg-transparent"></div>
          </div>

          <div class="h-5 w-px bg-slate-200 mr-2"></div>

          <div class="flex items-center gap-0.5">
            <button @click="editor.chain().focus().toggleBold().run()" :class="[toolbarItemClass, editor.isActive('bold') ? activeClass : '']">
              <svg class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M6 4h8a4 4 0 0 1 4 4 4 4 0 0 1-4 4H6z"/><path d="M6 12h9a4 4 0 0 1 4 4 4 4 0 0 1-4 4H6z"/></svg>
            </button>
            <button @click="editor.chain().focus().toggleItalic().run()" :class="[toolbarItemClass, editor.isActive('italic') ? activeClass : '']">
              <svg class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><line x1="19" y1="4" x2="10" y2="4"/><line x1="14" y1="20" x2="5" y2="20"/><line x1="15" y1="4" x2="9" y2="20"/></svg>
            </button>
            <button @click="editor.chain().focus().toggleStrike().run()" :class="[toolbarItemClass, editor.isActive('strike') ? activeClass : '']">
              <svg class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M17.3 19c-1.6.6-3.4 1-5.3 1-6.6 0-12-3.6-12-8 0-2 .9-3.9 2.4-5.4"/><path d="M16 5c2.3.9 4 2.8 4 6 0 1.6-.6 3.1-1.6 4.4"/><line x1="4" y1="12" x2="20" y2="12"/></svg>
            </button>
            <button @click="editor.chain().focus().toggleCode().run()" :class="[toolbarItemClass, editor.isActive('code') ? activeClass : '']">
              <svg class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="16 18 22 12 16 6"/><polyline points="8 6 2 12 8 18"/></svg>
            </button>

            <div class="relative ml-1">
              <button
                @click="showColorDropdown = !showColorDropdown"
                :class="[toolbarItemClass, 'relative flex-col gap-0 px-2']"
                title="字体颜色"
              >
                <span class="text-xs font-bold leading-none mt-0.5">A</span>
                <div class="w-3 h-1 rounded-full mt-0.5" :style="{ backgroundColor: currentColor }"></div>
              </button>

              <div v-if="showColorDropdown" class="absolute top-full left-0 mt-2 p-3 bg-white border border-slate-200 rounded-xl shadow-xl z-50 w-48">
                <div class="grid grid-cols-5 gap-2">
                  <button
                    @click="setTextColor('#000000')"
                    class="w-6 h-6 rounded-full border border-slate-200 hover:scale-110 transition-transform relative flex items-center justify-center bg-black"
                    title="默认黑色"
                  ></button>

                  <button
                    v-for="color in presetColors"
                    :key="color"
                    @click="setTextColor(color)"
                    class="w-6 h-6 rounded-full border border-slate-100 hover:scale-110 transition-transform hover:shadow-sm"
                    :style="{ backgroundColor: color }"
                  ></button>
                </div>
              </div>

              <div v-if="showColorDropdown" @click="showColorDropdown = false" class="fixed inset-0 z-40 bg-transparent"></div>
            </div>
          </div>

        </div>

        <editor-content :editor="editor" class="editor-content-wrapper flex-1 p-8 sm:p-12 min-h-[500px]" />

        <bubble-menu
          v-if="editor"
          :editor="editor"
          :tippy-options="{ duration: 120, placement: 'bottom-start', maxWidth: 420, zIndex: 999 }"
          :should-show="shouldShowBubble"
          class="ai-bubble-menu"
        >
          <div class="bg-white rounded-xl shadow-xl border border-slate-200 overflow-hidden w-[380px] ring-1 ring-slate-900/5">
            <div class="flex items-center justify-between px-4 py-2.5 border-b bg-slate-50">
              <span class="text-[10px] font-bold text-slate-400 uppercase tracking-widest flex items-center gap-1.5">
                🤖 AI 建议
              </span>
              <div class="flex items-center gap-2 text-xs text-slate-500 font-mono">
                <button @click="navigateIssue(-1)" :disabled="currentIssueIndex <= 0" class="w-6 h-6 flex items-center justify-center hover:bg-white rounded border border-transparent hover:border-slate-200 disabled:opacity-30">←</button>
                <span>{{ currentIssueIndex + 1 }}/{{ suggestions.length }}</span>
                <button @click="navigateIssue(1)" :disabled="currentIssueIndex >= suggestions.length - 1" class="w-6 h-6 flex items-center justify-center hover:bg-white rounded border border-transparent hover:border-slate-200 disabled:opacity-30">→</button>
              </div>
            </div>

            <div class="p-4 bg-white">
              <div class="space-y-3">
                 <div class="text-xs text-slate-400 mb-1 font-medium">原文</div>
                 <div class="text-sm text-slate-500 line-through bg-rose-50 px-3 py-2 rounded border border-rose-100 decoration-rose-400/50">
                    {{ currentIssue?.original || '' }}
                 </div>

                 <div class="flex items-center justify-between mt-3">
                    <div class="text-xs text-slate-400 font-medium">建议修改</div>
                    <span v-if="currentIssue?.type" class="text-[10px] px-1.5 py-0.5 bg-slate-100 text-slate-500 rounded border border-slate-200">
                      {{ currentIssue.type }}
                    </span>
                 </div>
                 <div class="text-sm font-medium text-emerald-700 bg-emerald-50 px-3 py-2 rounded border border-emerald-100/50">
                    {{ currentIssue?.content || '（建议删除）' }}
                 </div>

                 <div v-if="currentIssue?.message" class="text-xs text-slate-500 bg-slate-50 p-2 rounded italic border border-slate-100 mt-2">
                    💡 {{ currentIssue.message }}
                 </div>
              </div>
            </div>

            <div class="grid grid-cols-2 border-t divide-x divide-slate-100">
              <button @click="rejectSuggestion"
                class="py-3 text-xs font-semibold text-slate-500 hover:bg-slate-50 hover:text-slate-800 transition-colors">
                忽略
              </button>
              <button @click="acceptSuggestion"
                class="py-3 text-xs font-semibold text-emerald-600 hover:bg-emerald-50 transition-colors">
                采纳
              </button>
            </div>
          </div>
        </bubble-menu>
      </div>

      <transition name="slide-up">
        <div v-if="analyzing" class="fixed bottom-8 left-1/2 -translate-x-1/2 w-[min(92vw,680px)] bg-slate-900 text-white p-4 rounded-2xl shadow-2xl z-[100] ring-4 ring-white/20">
          <div class="flex items-start gap-3">
            <div class="w-5 h-5 border-2 border-white/20 border-t-white rounded-full animate-spin mt-0.5"></div>
            <div class="flex-1 min-w-0 space-y-3">
              <div class="flex items-center justify-between gap-3">
                <span class="text-sm font-medium tracking-wide truncate">{{ currentStatusMsg }}</span>
                <span class="text-xs text-slate-300 shrink-0">已耗时 {{ analysisElapsedLabel }}</span>
              </div>

              <div class="w-full h-1.5 bg-white/15 rounded-full overflow-hidden">
                <div
                  class="h-full bg-gradient-to-r from-sky-400 to-emerald-400 transition-all duration-500 ease-out"
                  :style="{ width: `${analysisProgress}%` }"
                ></div>
              </div>

              <div class="flex flex-wrap items-center gap-2">
                <span
                  v-for="stage in ANALYSIS_STAGES"
                  :key="stage.key"
                  class="text-[11px] px-2 py-1 rounded-full border transition-colors"
                  :class="activeStage === stage.key
                    ? 'bg-white text-slate-900 border-white'
                    : stageOrderMap[activeStage] > stageOrderMap[stage.key]
                      ? 'bg-emerald-500/20 text-emerald-200 border-emerald-300/30'
                      : 'bg-white/5 text-slate-300 border-white/15'"
                >
                  {{ stage.label }}
                </span>
              </div>
            </div>
          </div>
        </div>
      </transition>
    </main>

    <teleport to="body">
      <transition name="toast-fade">
        <div v-if="toast.show" class="fixed top-4 left-1/2 -translate-x-1/2 z-[99999] px-4 py-2 rounded-lg shadow-lg bg-slate-800 text-white text-sm font-medium flex items-center gap-3">
          <span :class="toast.type === 'success' ? 'text-emerald-400' : 'text-rose-400'">●</span>
          {{ toast.message }}
        </div>
      </transition>
    </teleport>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, onBeforeUnmount, nextTick } from 'vue'
import { useRoute } from 'vue-router'
import { useEditor, EditorContent, Extension } from '@tiptap/vue-3'
import { BubbleMenu } from '@tiptap/vue-3/menus'
import StarterKit from '@tiptap/starter-kit'
import { TextStyle } from '@tiptap/extension-text-style'
import { Color } from '@tiptap/extension-color'
import { Mark, mergeAttributes } from '@tiptap/core'
import Placeholder from '@tiptap/extension-placeholder'
// import StarterKit from '@tiptap/starter-kit';
import { Table } from '@tiptap/extension-table';
import { TableRow } from '@tiptap/extension-table-row';
import { TableCell } from '@tiptap/extension-table-cell';
import { TableHeader } from '@tiptap/extension-table-header';

import {
  getDocumentDetail,
  saveDocumentContent,
  downloadDocumentFile,
  analyzeDocumentAI
} from '@/api/review'

// ==================== 1. 样式常量 ====================
const toolbarItemClass = "p-1.5 rounded-md text-slate-500 hover:bg-slate-100 hover:text-slate-900 transition-all flex items-center justify-center text-sm font-medium h-8 min-w-[32px] disabled:opacity-30 disabled:cursor-not-allowed"
const dropdownItemClass = "flex items-center gap-2 w-full px-3 py-2 text-left hover:bg-slate-50 text-slate-600 transition-colors rounded-md"
const activeClass = "bg-slate-100 text-slate-900 font-bold"

// 🎨 预设颜色板 (Simple Editor 风格)
const presetColors = [
  '#958DF1', '#F98181', '#FBBC88', '#FAF594', '#70CFF8',
  '#94FADB', '#B9F18D', '#64748b', '#ef4444', '#f59e0b',
  '#10b981', '#3b82f6', '#6366f1', '#8b5cf6'
]

// ==================== 2. 自定义扩展: FontSize ====================
const FontSize = Extension.create({
  name: 'fontSize',
  addOptions() { return { types: ['textStyle'] } },
  addGlobalAttributes() {
    return [
      {
        types: this.options.types,
        attributes: {
          fontSize: {
            default: null,
            parseHTML: element => element.style.fontSize.replace('px', ''),
            renderHTML: attributes => {
              if (!attributes.fontSize) return {}
              return { style: `font-size: ${attributes.fontSize}px` }
            },
          },
        },
      },
    ]
  },
  addCommands() {
    return {
      setFontSize: fontSize => ({ chain }) => {
        return chain().setMark('textStyle', { fontSize }).run()
      },
      unsetFontSize: () => ({ chain }) => {
        return chain().setMark('textStyle', { fontSize: null }).removeEmptyTextStyle().run()
      },
    }
  },
})

// ==================== 自定义 Mark: AiCorrection ====================
const AiCorrection = Mark.create({
  name: 'aiCorrection',
  keepOnSplit: false,
  addAttributes() {
    return {
      'data-ai-id': { default: null },
      'data-reason': { default: null }
    }
  },
  parseHTML() { return [{ tag: 'span.ai-correction-mark' }] },
  renderHTML({ HTMLAttributes }) {
    return ['span', mergeAttributes({ class: 'ai-correction-mark' }, HTMLAttributes), 0]
  },
})

// ==================== 状态 ====================
const route = useRoute()
const documentName = ref('Untitled')
const suggestions = ref([])
const analyzing = ref(false)
const currentStatusMsg = ref('')
const analysisProgress = ref(0)
const activeStage = ref('connecting')
const analysisElapsedSeconds = ref(0)
let analysisTicker = null
const toast = reactive({ show: false, message: '', type: 'success' })
const showHeadingDropdown = ref(false)
const showColorDropdown = ref(false) // 🌈 颜色下拉状态

const currentIssueId = ref(null)
const currentIssue = computed(() => suggestions.value.find(s => s.id === currentIssueId.value))
const currentIssueIndex = computed(() => suggestions.value.findIndex(s => s.id === currentIssueId.value))

const currentFontSizeLabel = computed(() => {
  if (!editor.value) return '正文'
  const fontSize = editor.value.getAttributes('textStyle').fontSize
  if (fontSize === '30') return '大标题'
  if (fontSize === '24') return '中标题'
  if (fontSize === '20') return '小标题'
  return '正文'
})

const currentColor = computed(() => {
  if (!editor.value) return '#000000'
  return editor.value.getAttributes('textStyle').color || '#000000'
})

const ANALYSIS_STAGES = [
  { key: 'connecting', label: '连接服务' },
  { key: 'start', label: '预处理' },
  { key: 'scanning', label: '初审扫描' },
  { key: 'verifying', label: '复核确认' },
  { key: 'applying', label: '整理结果' },
  { key: 'complete', label: '完成' }
]

const stageOrderMap = ANALYSIS_STAGES.reduce((acc, stage, index) => {
  acc[stage.key] = index
  return acc
}, {})

const stageProgressMap = {
  connecting: 8,
  start: 18,
  scanning: 52,
  verifying: 82,
  applying: 92,
  complete: 100,
  error: 100
}

const analysisElapsedLabel = computed(() => `${analysisElapsedSeconds.value}s`)

const startAnalysisTicker = () => {
  stopAnalysisTicker()
  analysisElapsedSeconds.value = 0
  analysisTicker = setInterval(() => {
    analysisElapsedSeconds.value += 1
  }, 1000)
}

const stopAnalysisTicker = () => {
  if (!analysisTicker) return
  clearInterval(analysisTicker)
  analysisTicker = null
}

const setAnalysisStage = (stage, desc = '') => {
  if (stageProgressMap[stage] !== undefined) {
    analysisProgress.value = Math.max(analysisProgress.value, stageProgressMap[stage])
  }
  if (stageOrderMap[stage] !== undefined) {
    activeStage.value = stage
  }
  if (desc) currentStatusMsg.value = desc
}

// ==================== Tiptap 配置 ====================
const editor = useEditor({
  content: '',
  extensions: [
    StarterKit.configure({
       heading: false,
       codeBlock: { HTMLAttributes: { class: 'code-block' } }
    }),
    TextStyle,
    FontSize,
    Color, // 必须
    AiCorrection,
    Placeholder.configure({
      placeholder: '开始输入内容，或输入 "/" 使用命令...',
    }),
    Table.configure({
      resizable: true, // 允许调整列宽
    }),
    TableRow,
    TableHeader,
    TableCell,
  ],
  editorProps: {
    attributes: {
      class: 'prose prose-slate max-w-none focus:outline-none min-h-[400px]',
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
    showHeadingDropdown.value = false
    showColorDropdown.value = false // 选中变化时关闭下拉
  }
})

const shouldShowBubble = ({ editor: e }) => e.isActive('aiCorrection')

// ==================== 工具栏逻辑 ====================
const toggleHeadingDropdown = () => {
  showHeadingDropdown.value = !showHeadingDropdown.value
  showColorDropdown.value = false // 互斥
}

const setTextStyle = (type) => {
  if (!editor.value) return

  if (type === 'normal') {
    editor.value.chain().focus().unsetFontSize().unsetBold().run()
  } else if (type === 'large') {
    editor.value.chain().focus().setFontSize('30').setBold().run()
  } else if (type === 'medium') {
    editor.value.chain().focus().setFontSize('24').setBold().run()
  } else if (type === 'small') {
    editor.value.chain().focus().setFontSize('20').setBold().run()
  }
  showHeadingDropdown.value = false
}

// 🌈 设置文字颜色
const setTextColor = (color) => {
  if (!editor.value) return
  editor.value.chain().focus().setColor(color).run()
  showColorDropdown.value = false
}

// ==================== AI 逻辑 ====================
const handleStartAI = async () => {
  if (!editor.value) return
  analyzing.value = true
  analysisProgress.value = 0
  activeStage.value = 'connecting'
  setAnalysisStage('connecting', '正在连接 AI 服务...')
  startAnalysisTicker()

  clearAllMarks()
  suggestions.value = []
  currentIssueId.value = null
  const processedFingerprints = new Set()

  try {
    const contentToSend = editor.value.getHTML()
    const response = await analyzeDocumentAI(route.params.id, { content: contentToSend })

    if (!response.ok) throw new Error(`API 请求失败: ${response.status}`)
    if (!response.body) throw new Error('API response does not support streaming')
    setAnalysisStage('start')

    const reader = response.body.getReader()
    const decoder = new TextDecoder()
    let buffer = ''

    while (true) {
      const { done, value } = await reader.read()
      if (done) break
      buffer += decoder.decode(value, { stream: true })
      const parts = buffer.split('\n\n')
      buffer = parts.pop()

      for (const part of parts) {
        if (part.startsWith('data: ')) {
          try {
            const payload = JSON.parse(part.slice(6))
            handleStreamPayload(payload, processedFingerprints)
          } catch (e) { console.warn('JSON 解析失败:', e) }
        }
      }
    }
    setAnalysisStage('complete', '分析完成')
    if (suggestions.value.length > 0) {
       showToast(`分析完成，发现 ${suggestions.value.length} 处建议`)
       nextTick(() => navigateIssue(0))
    } else {
       showToast('文档质量良好，未发现可修改项', 'success')
    }
  } catch (err) {
    setAnalysisStage('error')
    showToast('校阅中断: ' + (err.message || '未知错误'), 'error')
  } finally {
    stopAnalysisTicker()
    analyzing.value = false
    currentStatusMsg.value = ''
  }
}

const handleStreamPayload = (payload, processedFingerprints) => {
  if (payload.step) setAnalysisStage(payload.step, payload.desc)
  if (payload.step === 'error') { showToast(payload.desc, 'error'); return }
  if (payload.data && Array.isArray(payload.data)) {
    setAnalysisStage('applying', '正在整理并标注结果...')
    applyIssuesIdeally(payload.data, processedFingerprints)
  }
}

const applyIssuesIdeally = (newIssues, processedFingerprints) => {
  const tr = editor.value.state.tr
  let hasChanges = false

  newIssues.forEach(issue => {
    const positions = findTextPositions(editor.value.state.doc, issue.original)
    for (const { from, to } of positions) {
      const hasMark = tr.doc.rangeHasMark(from, to, editor.value.schema.marks.aiCorrection)
      if (!hasMark) {
        const issueId = `issue-${Date.now()}-${Math.random().toString(36).substr(2,9)}`
        tr.addMark(from, to, editor.value.schema.marks.aiCorrection.create({
          'data-ai-id': issueId, 'data-reason': issue.reason
        }))
        suggestions.value.push({
          id: issueId, original: issue.original, content: issue.suggestion,
          message: issue.reason, type: issue.type
        })
        hasChanges = true
        break
      }
    }
  })
  if (hasChanges) editor.value.view.dispatch(tr)
}

const findTextPositions = (doc, searchText) => {
  const positions = []
  if (!searchText) return positions
  doc.descendants((node, pos) => {
    if (node.isText) {
      const index = node.text.indexOf(searchText)
      if (index !== -1) positions.push({ from: pos + index, to: pos + index + searchText.length })
    }
  })
  return positions
}

const clearAllMarks = () => {
  const tr = editor.value.state.tr
  const { doc } = tr
  doc.descendants((node, pos) => {
    const mark = node.marks.find(m => m.type.name === 'aiCorrection')
    if (mark) tr.removeMark(pos, pos + node.nodeSize, mark)
  })
  editor.value.view.dispatch(tr)
}

const scrollToIssue = (id) => {
  const el = document.querySelector(`span[data-ai-id="${id}"]`)
  if (el) el.scrollIntoView({ behavior: 'smooth', block: 'nearest' })
}

const navigateIssue = (step) => {
  if (suggestions.value.length === 0) return
  let idx = currentIssueIndex.value + step
  idx = Math.max(0, Math.min(idx, suggestions.value.length - 1))
  currentIssueId.value = suggestions.value[idx].id
  nextTick(() => scrollToIssue(currentIssueId.value))
}

const removeSuggestionAndSelectNext = (sugId) => {
  const currentIdx = currentIssueIndex.value
  suggestions.value = suggestions.value.filter(s => s.id !== sugId)
  if (suggestions.value.length > 0) {
    const nextIdx = Math.min(currentIdx, suggestions.value.length - 1)
    currentIssueId.value = suggestions.value[nextIdx].id
    nextTick(() => scrollToIssue(currentIssueId.value))
  } else {
    currentIssueId.value = null
  }
}

const acceptSuggestion = () => {
  const sug = currentIssue.value
  if (!sug || !editor.value) return
  editor.value.chain().focus().command(({ tr, dispatch }) => {
    let found = false
    editor.value.state.doc.descendants((node, pos) => {
      if (found) return false
      const mark = node.marks.find(m => m.type.name === 'aiCorrection' && m.attrs['data-ai-id'] === sug.id)
      if (mark) {
        const from = pos; const to = pos + node.nodeSize
        tr.deleteRange(from, to)
        if (sug.content) tr.insertText(sug.content, from)
        found = true
      }
    })
    if (dispatch && found) dispatch(tr)
    return found
  }).run()
  removeSuggestionAndSelectNext(sug.id)
  showToast('已采纳建议')
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
  removeSuggestionAndSelectNext(sug.id)
  showToast('已忽略建议')
}

const fetchBasicDetail = async () => {
  try {
    const res = await getDocumentDetail(route.params.id)
    documentName.value = res.name || 'Untitled'
    editor.value?.commands.setContent(res.content_html || res.content || '')
  } catch (e) {
    showToast('加载失败', 'error')
  }
}

const handleSave = async () => {
  try {
    let html = editor.value.getHTML()
    html = html.replace(/<span[^>]*class="ai-correction-mark"[^>]*>([\s\S]*?)<\/span>/g, '$1')
    await saveDocumentContent(route.params.id, html)
    showToast('保存成功')
  } catch (err) { showToast('保存失败', 'error') }
}

const handleDownload = async () => {
  try {
    const blob = await downloadDocumentFile(route.params.id)
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `${documentName.value}_校核版.docx`
    a.click()
    URL.revokeObjectURL(url)
  } catch (err) { showToast('导出失败', 'error') }
}

const showToast = (msg, type = 'success') => {
  toast.message = msg; toast.type = type; toast.show = true
  setTimeout(() => { toast.show = false }, 3000)
}

onMounted(() => fetchBasicDetail())
onBeforeUnmount(() => {
  stopAnalysisTicker()
  editor.value?.destroy()
})
</script>

<style scoped>
/* 编辑器内部样式优化 */
:deep(.prose) {
  font-size: 1rem;
  line-height: 1.75;
  color: #334155;
}

/* 引用块样式 */
:deep(.prose blockquote) {
  border-left: 3px solid #e2e8f0;
  padding-left: 1rem;
  color: #64748b;
  font-style: italic;
  margin: 1.5rem 0;
}

/* 代码块样式 */
:deep(.prose pre) {
  background: #0d0d0d;
  color: #fff;
  font-family: 'JetBrains Mono', monospace;
  padding: 0.75rem 1rem;
  border-radius: 0.5rem;
  margin: 1.5rem 0;
}
:deep(.prose code) {
  color: inherit;
  padding: 0;
  background: none;
  font-size: 0.875em;
}

/* 行内代码样式 */
:deep(.prose :not(pre) > code) {
  background-color: #f1f5f9;
  color: #ef4444; /* 红色 */
  padding: 0.25rem 0.375rem;
  border-radius: 0.375rem;
  font-size: 0.875em;
  font-weight: 600;
}

/* 占位符样式 */
:deep(.is-editor-empty:first-child::before) {
  color: #94a3b8;
  content: attr(data-placeholder);
  float: left;
  height: 0;
  pointer-events: none;
}

/* AI 高亮标记 */
:deep(.ai-correction-mark) {
  background-color: #fef9c3; /* yellow-100 */
  border-bottom: 2px dashed #ca8a04; /* yellow-600 */
  padding: 2px 0;
  cursor: pointer;
  transition: all 0.2s;
  scroll-margin-top: 120px;
}
:deep(.ai-correction-mark:hover) {
  background-color: #fde047;
}
/* 针对 Tiptap 内容的表格样式（scoped 下需 deep） */
:deep(.ProseMirror table) {
  border-collapse: collapse;
  table-layout: fixed;
  width: 100%;
  margin: 1rem 0;
  overflow: hidden;
  border: 1px solid #cbd5e1;
  border-radius: 0.375rem;
}

:deep(.ProseMirror td), :deep(.ProseMirror th) {
  min-width: 1em;
  border: 1px solid #ced4da;
  padding: 6px 8px;
  vertical-align: top;
  box-sizing: border-box;
  position: relative;
  background: #ffffff;
}

:deep(.ProseMirror th) {
  background: #f8fafc;
  font-weight: 600;
}

:deep(.ProseMirror table p) {
  margin: 0;
}

/* 动画 */
.slide-up-enter-active, .slide-up-leave-active { transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1); }
.slide-up-enter-from, .slide-up-leave-to { transform: translate(-50%, 100%); opacity: 0; }

.toast-fade-enter-active, .toast-fade-leave-active { transition: all 0.3s ease; }
.toast-fade-enter-from, .toast-fade-leave-to { opacity: 0; transform: translate(-50%, -20px); }
</style>

