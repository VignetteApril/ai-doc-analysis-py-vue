<template>
  <div class="h-full w-full overflow-auto p-4 md:p-6 font-sans">
    <div class="upload-card rounded-[32px] p-6 md:p-8 flex flex-col gap-6 shadow-sm w-full max-w-[1200px] min-h-full mx-auto">
      <div class="flex items-center justify-between">
        <div>
          <h2 class="text-2xl font-bold text-slate-800">导入词库</h2>
          <p class="text-sm text-slate-500 mt-1">上传文档后可编辑、删除 AI 结果，确认无误再导入词库。</p>
        </div>
        <button
          @click="goBack"
          class="px-4 py-2 border border-slate-200 text-slate-600 rounded-lg hover:bg-slate-50 text-sm"
        >
          返回词库
        </button>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-4 gap-3">
        <div
          v-for="(s, idx) in steps"
          :key="s.key"
          class="rounded-xl border px-4 py-3"
          :class="stepClass(s.key)"
        >
          <div class="text-xs mb-1">步骤 {{ idx + 1 }}</div>
          <div class="text-sm font-semibold">{{ s.label }}</div>
        </div>
      </div>

      <div class="rounded-2xl border border-slate-100 bg-white p-6">
        <div class="flex flex-wrap items-center gap-3">
          <input
            ref="fileInputRef"
            type="file"
            class="hidden"
            accept=".pdf,.txt,.text,.doc,.docx"
            @change="handleFileChange"
          >
          <button
            @click="triggerSelectFile"
            :disabled="analyzing || importing"
            class="px-5 py-2.5 bg-[#1d70f5] text-white rounded-xl text-sm font-bold disabled:opacity-50"
          >
            上传文档
          </button>
          <span class="text-sm text-slate-500">{{ selectedFileName || '未选择文件' }}</span>
          <span v-if="analyzing" class="text-sm text-[#1d70f5]">AI 正在分析...</span>
          <span v-if="importing" class="text-sm text-[#1d70f5]">正在导入词库...</span>
        </div>

        <div v-if="items.length > 0" class="mt-4 text-sm text-slate-600 flex flex-wrap gap-4">
          <span>识别条目：{{ items.length }}</span>
          <span>可导入：{{ readyItems.length }}</span>
          <span>跳过：{{ skippedCount }}</span>
        </div>
      </div>

      <div class="flex-1 min-h-0 rounded-2xl border border-slate-100 bg-white overflow-auto">
        <table class="w-full text-left text-sm">
          <thead class="sticky top-0 bg-slate-50 z-10 border-b border-slate-100">
            <tr>
              <th class="px-4 py-3 font-medium text-slate-500">原词</th>
              <th class="px-4 py-3 font-medium text-slate-500">替换词</th>
              <th class="px-4 py-3 font-medium text-slate-500 w-24 text-center">操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="items.length === 0">
              <td colspan="3" class="px-4 py-16 text-center text-slate-400">请先上传文档进行分析</td>
            </tr>
            <tr v-for="(item, idx) in items" :key="idx" class="border-b border-slate-50">
              <td class="px-4 py-3">
                <input
                  v-model="item.original_word"
                  type="text"
                  class="w-full px-3 py-1.5 border border-slate-200 rounded-lg focus:ring-2 focus:ring-blue-300 focus:outline-none"
                  placeholder="原词"
                >
              </td>
              <td class="px-4 py-3">
                <input
                  v-model="item.replacement_word"
                  type="text"
                  class="w-full px-3 py-1.5 border border-slate-200 rounded-lg focus:ring-2 focus:ring-blue-300 focus:outline-none"
                  placeholder="替换词"
                >
              </td>
              <td class="px-4 py-3 text-center">
                <button
                  @click="removeItem(idx)"
                  class="text-red-500 hover:text-red-600 text-xs font-medium"
                >
                  删除
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <div class="flex items-center justify-end gap-3">
        <button
          @click="goBack"
          class="px-5 py-2.5 border border-slate-200 text-slate-600 rounded-xl text-sm hover:bg-slate-50"
        >
          取消
        </button>
        <button
          @click="handleConfirmImport"
          :disabled="!previewId || readyItems.length === 0 || analyzing || importing"
          class="px-5 py-2.5 bg-[#1d70f5] text-white rounded-xl text-sm font-bold disabled:opacity-50"
        >
          确认导入词库
        </button>
      </div>
    </div>

    <teleport to="body">
      <Transition name="toast">
        <div
          v-if="toast.show"
          class="fixed top-4 left-1/2 -translate-x-1/2 z-[99999] px-6 py-3 rounded-xl shadow-xl text-sm font-medium"
          :class="toast.type === 'success' ? 'bg-emerald-500 text-white' : 'bg-red-500 text-white'"
        >
          {{ toast.message }}
        </div>
      </Transition>
    </teleport>
  </div>
</template>

<script setup>
import { computed, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { previewVocabularyImport, confirmVocabularyImport } from '@/api/vocabulary'

const router = useRouter()

const fileInputRef = ref(null)
const selectedFileName = ref('')
const previewId = ref('')
const analyzing = ref(false)
const importing = ref(false)
const currentStep = ref('upload')
const items = ref([])

const toast = reactive({ show: false, message: '', type: 'success' })

const steps = [
  { key: 'upload', label: '上传文档' },
  { key: 'analyzing', label: 'AI 分析' },
  { key: 'preview', label: '结果确认' },
  { key: 'completed', label: '导入完成' }
]

const isValidItem = (item, idx) => {
  const original = String(item?.original_word || '').trim()
  const replacement = String(item?.replacement_word || '').trim()

  if (!original || !replacement) {
    return false
  }
  if (original === replacement) {
    return false
  }
  if (original.length < 2 || replacement.length < 2) {
    return false
  }

  const duplicate = items.value.some((row, i) => i !== idx && String(row?.original_word || '').trim() === original)
  if (duplicate) {
    return false
  }

  return true
}

const readyItems = computed(() => items.value.filter((item, idx) => isValidItem(item, idx)))
const skippedCount = computed(() => items.value.length - readyItems.value.length)

const showToast = (message, type = 'success') => {
  toast.message = message
  toast.type = type
  toast.show = true
  setTimeout(() => {
    toast.show = false
  }, 3000)
}

const stepClass = (stepKey) => {
  const order = ['upload', 'analyzing', 'preview', 'completed']
  const currentIndex = order.indexOf(currentStep.value)
  const stepIndex = order.indexOf(stepKey)

  if (stepIndex < currentIndex) return 'border-emerald-200 bg-emerald-50 text-emerald-700'
  if (stepIndex === currentIndex) return 'border-blue-200 bg-blue-50 text-[#1d70f5]'
  return 'border-slate-200 bg-slate-50 text-slate-400'
}

const goBack = () => {
  router.push('/vocabulary')
}

const triggerSelectFile = () => {
  if (analyzing.value || importing.value) return
  fileInputRef.value?.click()
}

const handleFileChange = async (event) => {
  const file = event.target?.files?.[0]
  if (!file) return

  const ext = (file.name.split('.').pop() || '').toLowerCase()
  const allowed = new Set(['pdf', 'txt', 'text', 'doc', 'docx'])
  if (!allowed.has(ext)) {
    showToast('仅支持 pdf/txt/doc/docx', 'error')
    event.target.value = ''
    return
  }

  selectedFileName.value = file.name
  currentStep.value = 'analyzing'
  analyzing.value = true
  previewId.value = ''
  items.value = []

  try {
    const formData = new FormData()
    formData.append('file', file)

    const res = await previewVocabularyImport(formData)
    previewId.value = res.preview_id || ''
    items.value = (Array.isArray(res.items) ? res.items : []).map((item) => ({
      original_word: item.original_word || '',
      replacement_word: item.replacement_word || ''
    }))
    currentStep.value = 'preview'

    if (!previewId.value || items.value.length === 0) {
      showToast(res.message || '未识别到可导入词条', 'error')
    } else {
      showToast('分析完成，可编辑后确认导入')
    }
  } catch (err) {
    currentStep.value = 'upload'
    const msg = err?.response?.data?.detail || '分析失败，请稍后重试'
    showToast(msg, 'error')
  } finally {
    analyzing.value = false
    event.target.value = ''
  }
}

const removeItem = (idx) => {
  items.value.splice(idx, 1)
}

const handleConfirmImport = async () => {
  if (!previewId.value || readyItems.value.length === 0) return

  importing.value = true
  try {
    const res = await confirmVocabularyImport({
      preview_id: previewId.value,
      selected_items: readyItems.value.map((item) => ({
        original_word: String(item.original_word || '').trim(),
        replacement_word: String(item.replacement_word || '').trim()
      }))
    })
    currentStep.value = 'completed'
    showToast(`导入完成：新增 ${res.inserted || 0} 条，跳过 ${res.skipped || 0} 条`)
  } catch (err) {
    const msg = err?.response?.data?.detail || '导入失败，请稍后重试'
    showToast(msg, 'error')
  } finally {
    importing.value = false
  }
}
</script>

<style scoped>
.upload-card {
  background: linear-gradient(181deg, #ffffff 0%, #ffffff 65%, #dfedff 100%);
  border: solid 2px #ffffff;
}

.toast-enter-active { animation: slide-in 0.25s ease-out; }
.toast-leave-active { transition: opacity 0.2s; }
.toast-leave-to { opacity: 0; }

@keyframes slide-in {
  from { opacity: 0; transform: translate(-50%, -12px); }
  to { opacity: 1; transform: translate(-50%, 0); }
}
</style>
