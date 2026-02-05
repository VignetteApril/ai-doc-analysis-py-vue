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
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { uploadDocument } from '@/api/review' // 确保你已创建此 API 文件

const router = useRouter()
const fileInput = ref(null)
const isDragging = ref(false)
const uploading = ref(false)

// 处理文件上传核心逻辑
const processFile = async (file) => {
  // 1. 文件格式检查
  const ext = file.name.split('.').pop().toLowerCase()
  if (!['pdf', 'doc', 'docx'].includes(ext)) {
    alert('格式错误：仅支持 PDF、DOC 或 DOCX 文件')
    return
  }

  // 2. 准备上传
  uploading.value = true

  try {
    // 调用我们在 api/review.js 定义的函数
    await uploadDocument(file)

    // 3. 上传成功处理
    console.log('文件上传并解析成功:', file.name)
    // 跳转回列表页，并带上刷新标记（可选）
    router.push('/review')
  } catch (error) {
    console.error('上传失败:', error)
    alert(error.response?.data?.detail || '服务器解析文档失败，请检查文件内容或格式')
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