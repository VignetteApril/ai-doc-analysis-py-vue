<template>
  <div class="h-full w-full flex items-center justify-center p-6 md:p-10">
    <div class="upload-card rounded-[40px] flex flex-col items-center justify-center relative transition-all">

      <button
        @click="$router.push('/review')"
        class="absolute top-8 left-10 flex items-center gap-2 text-slate-400 hover:text-[#1d70f5] transition-colors font-medium"
      >
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path d="M10 19l-7-7m0 0l7-7m-7 7h18" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"/></svg>
        返回列表
      </button>

      <div class="flex flex-col items-center">
        <div class="relative mb-8">
          <div class="w-24 h-24 bg-blue-50/50 rounded-3xl flex items-center justify-center shadow-inner">
             <svg class="w-12 h-12 text-blue-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"/><path d="M9 13h6m-6 4h6" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"/></svg>
          </div>
          <div class="absolute -bottom-1 -right-1 w-7 h-7 bg-[#1d70f5] rounded-full border-2 border-white flex items-center justify-center shadow-md shadow-blue-500/30">
            <svg class="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path d="M5 10l7-7m0 0l7 7m-7-7v18" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"/></svg>
          </div>
        </div>

        <h3 class="text-2xl font-bold text-slate-800 mb-3 tracking-tight">点击或将文档拖拽到这里上传</h3>
        <p class="text-slate-400 text-base mb-10">格式支持 pdf / doc / docx</p>

        <input type="file" ref="fileInput" class="hidden" accept=".pdf,.doc,.docx" @change="handleFileChange">
        <button
          @click="$refs.fileInput.click()"
          class="px-12 py-3.5 bg-[#1d70f5] hover:bg-blue-700 text-white font-bold rounded-xl shadow-xl shadow-blue-500/20 transition-all transform active:scale-95"
        >
          立即上传
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const handleFileChange = (e) => {
  const file = e.target.files[0]
  if (file) alert('准备上传: ' + file.name)
}
</script>

<style scoped>
.upload-card {
  width: 100%; height: 100%; max-width: 1840px; max-height: 860px;
  background-image: linear-gradient(181deg, #ffffff 0%, #ffffff 65%, #dfedff 100%);
  box-shadow: 0px 3px 12px 0px rgba(255, 255, 255, 0.8);
  border: solid 2px #ffffff;
}
</style>