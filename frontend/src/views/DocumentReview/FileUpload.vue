<template>
  <div class="h-full w-full flex items-center justify-center p-6 md:p-10">
    <div
      class="upload-card rounded-[40px] flex flex-col items-center justify-center relative transition-all duration-300"
      @dragover.prevent="isDragging = true"
      @dragleave.prevent="isDragging = false"
      @drop.prevent="handleDrop"
      :class="{'scale-[1.01] border-blue-300 bg-blue-50/30 shadow-2xl': isDragging}"
    >
      <button
        @click="$router.push('/review')"
        :disabled="uploading"
        class="absolute top-8 left-10 flex items-center gap-2 text-slate-400 hover:text-[#1d70f5] transition-colors font-medium disabled:opacity-50"
      >
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path d="M10 19l-7-7m0 0l7-7m-7 7h18" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"/></svg>
        返回列表
      </button>

      <Transition name="fade">
        <div v-if="uploading" class="absolute inset-0 z-50 bg-white/60 backdrop-blur-md rounded-[40px] flex flex-col items-center justify-center">
          <div class="w-14 h-14 border-4 border-[#1d70f5] border-t-transparent rounded-full animate-spin"></div>
          <p class="mt-6 text-slate-800 font-bold text-lg animate-pulse">正在解析文档并提取内容...</p>
          <p class="mt-2 text-slate-400 text-sm">请勿关闭页面，AI 正在异步初始化校审任务</p>
        </div>
      </Transition>

      <div class="flex flex-col items-center transition-opacity duration-300" :class="{'opacity-20': uploading}">
        <div class="relative mb-8">
          <div class="w-24 h-24 bg-blue-50/50 rounded-3xl flex items-center justify-center shadow-inner">
             <svg class="w-12 h-12 text-blue-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"/><path d="M9 13h6m-6 4h6" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"/></svg>
          </div>
          <div class="absolute -bottom-1 -right-1 w-7 h-7 bg-[#1d70f5] rounded-full border-2 border-white flex items-center justify-center shadow-md">
            <svg class="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path d="M5 10l7-7m0 0l7 7m-7-7v18" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"/></svg>
          </div>
        </div>

        <h3 class="text-2xl font-bold text-slate-800 mb-3 tracking-tight">点击或将文档拖拽到这里上传</h3>
        <p class="text-slate-400 text-base mb-10">格式支持 pdf / doc / docx</p>

        <input type="file" ref="fileInput" class="hidden" accept=".pdf,.doc,.docx" @change="handleFileChange">
        <button
          @click="$refs.fileInput.click()"
          :disabled="uploading"
          class="px-12 py-3.5 bg-[#1d70f5] hover:bg-blue-700 text-white font-bold rounded-xl shadow-xl shadow-blue-500/20 transition-all transform active:scale-95 disabled:bg-slate-300"
        >
          立即上传
        </button>
      </div>
    </div>
    
    <teleport to="body">
      <Transition name="toast">
        <div v-if="toast.show"
             class="fixed top-4 left-1/2 -translate-x-1/2 z-[99999] px-8 py-3.5 rounded-2xl shadow-2xl border backdrop-blur-md font-bold text-sm tracking-wide"
             :class="toast.type === 'success' ? 'bg-emerald-500/90 border-emerald-400 text-white' : 'bg-red-500/90 border-red-400 text-white'">
          {{ toast.message }}
        </div>
      </Transition>
    </teleport>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { uploadDocument } from '@/api/review' // 确保你已创建此 API 文件

const router = useRouter()
const fileInput = ref(null)
const isDragging = ref(false)
const uploading = ref(false)

// --- Toast 状态定义 ---
const toast = reactive({ show: false, message: '', type: 'success' })

const showToast = (msg, type = 'success') => {
  toast.message = msg
  toast.type = type
  toast.show = true
  setTimeout(() => { toast.show = false }, 3000)
}
// 处理文件上传核心逻辑
/**
 * 核心：处理文件上传逻辑 [cite: 2026-02-05]
 * 解决了 Multipart Boundary 缺失及字段名匹配（422）的问题
 */
const processFile = async (file) => {
  // 1. 基础校验：后缀名检查
  const ext = file.name.split('.').pop().toLowerCase()
  const allowedExtensions = ['pdf', 'doc', 'docx']

  if (!allowedExtensions.includes(ext)) {
    showToast('格式不支持：仅允许 PDF, DOC 或 DOCX', 'error')
    return
  }

  // 2. 准备上传状态
  uploading.value = true

  // --- ✨ 核心修复：构造符合 FastAPI Form 定义的 FormData ---
  const formData = new FormData()

  // 对应后端的 file: UploadFile = File(...) [cite: 2026-02-05]
  formData.append('file', file)

  // 对应后端的 name: str = Form(...) [cite: 2026-02-05]
  // 必须添加此字段，否则后端会报 422 Field required
  formData.append('name', file.name)

  try {
    // 3. 执行请求
    // 注意：不要在请求头里手动设置 Content-Type，让浏览器自己处理 Boundary
    const res = await uploadDocument(formData)

    // 4. 成功后的业务流转 [cite: 2026-02-02]
    showToast('文档上传成功，AI 正在解析...', 'success')

    // 延迟跳转，给用户一点看成功反馈的时间
    setTimeout(() => {
      // 直接跳转到校审详情页，实现“即传即改”的高效体验
      router.push({
        name: 'review-detail',
        params: { id: res.id }
      })
    }, 800)

  } catch (error) {
    // 5. 异常审计：捕获并显示后端传回的 422 或 500 错误详情 [cite: 2026-02-05]
    console.error('上传链路异常:', error)
    const backendMsg = error.response?.data?.detail

    // 如果返回的是 422 数组，提取第一个错误的 msg
    const errorHint = Array.isArray(backendMsg)
      ? `字段错误: ${backendMsg[0].loc.join('.')}`
      : (backendMsg || '服务器解析失败')

    showToast(errorHint, 'error')
  } finally {
    uploading.value = false
  }
}

// 拖拽释放处理
const handleDrop = (e) => {
  isDragging.value = false
  if (uploading.value) return
  const files = e.dataTransfer.files
  if (files.length > 0) processFile(files[0])
}

// 文件选择处理
const handleFileChange = (e) => {
  const file = e.target.files[0]
  if (file) processFile(file)
}
</script>

<style scoped>
.upload-card {
  width: 100%; height: 100%; max-width: 1840px; max-height: 860px;
  background-image: linear-gradient(181deg, #ffffff 0%, #ffffff 65%, #dfedff 100%);
  box-shadow: 0px 3px 12px 0px rgba(255, 255, 255, 0.8);
  border: solid 2px #ffffff;
}

.fade-enter-active, .fade-leave-active { transition: opacity 0.3s ease; }
.fade-enter-from, .fade-leave-to { opacity: 0; }
</style>