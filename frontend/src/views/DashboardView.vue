<template>
  <div class="h-screen bg-[#f0f5ff] flex flex-col font-sans relative overflow-hidden">
    <div class="absolute top-0 left-0 w-full h-full pointer-events-none">
      <div class="absolute top-[-10%] left-[-10%] w-[40%] h-[40%] bg-blue-200/20 blur-[120px] rounded-full"></div>
      <div class="absolute bottom-[-10%] right-[-10%] w-[40%] h-[40%] bg-purple-200/10 blur-[120px] rounded-full"></div>
    </div>

    <nav class="h-16 bg-white/70 backdrop-blur-xl border-b border-white/50 px-8 flex items-center sticky top-0 z-50 shadow-sm">
      <div class="flex-1 flex items-center">
        <div class="flex items-center gap-2.5">
          <div class="w-9 h-9 bg-[#1d70f5] rounded-lg flex items-center justify-center shadow-lg shadow-blue-500/30">
            <span class="text-white font-bold italic text-lg">Ai</span>
          </div>
          <span class="text-xl font-bold text-slate-800 tracking-tight">AI公文校对系统</span>
        </div>
      </div>

      <div class="flex items-center gap-10 h-16 shrink-0">
        <a href="#" class="relative text-[#1d70f5] font-semibold flex items-center gap-2 h-full">
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"/></svg>
          公文校审
          <div class="absolute bottom-0 left-0 w-full h-0.5 bg-[#1d70f5] rounded-full"></div>
        </a>
        <a href="#" class="text-slate-500 hover:text-slate-800 font-medium flex items-center gap-2 transition-colors h-full">
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path d="M4 7v10c0 2.21 3.582 4 8 4s8-1.79 8-4V7M4 7c0 2.21 3.582 4 8 4s8-1.79 8-4M4 7c0-2.21 3.582-4 8-4s8 1.79 8 4m0 5c0 2.21-3.582 4-8 4s-8-1.79-8-4" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"/></svg>
          词库管理
        </a>
      </div>

      <div class="flex-1 flex items-center justify-end">
        <div class="relative group">
          <div class="flex items-center gap-3 bg-white/50 border border-slate-200 py-1.5 pl-2 pr-4 rounded-full cursor-pointer hover:bg-white transition-all">
            <img src="https://api.dicebear.com/7.x/avataaars/svg?seed=Jack" class="w-7 h-7 rounded-full bg-blue-100" />
            <span class="text-sm font-medium text-slate-700">{{ username }}</span>
            <div class="h-3 w-[1px] bg-slate-300 mx-1"></div>
            <span class="text-xs text-slate-500 flex items-center gap-1 group-hover:text-slate-800">
              更多 <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path d="M19 9l-7 7-7-7" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"/></svg>
            </span>
          </div>
        </div>
      </div>
    </nav>

    <main class="flex-1 p-6 md:p-10 lg:p-12 flex items-center justify-center overflow-hidden">
      <div
        class="upload-card rounded-[40px] flex flex-col items-center justify-center relative transition-all duration-300"
        @dragover.prevent="isDragging = true"
        @dragleave.prevent="isDragging = false"
        @drop.prevent="handleDrop"
        :class="{'scale-[1.01] border-blue-200 shadow-2xl': isDragging}"
      >
        <div class="flex flex-col items-center animate-fade-in">
          <div class="relative mb-8">
            <div class="w-24 h-24 bg-blue-50/50 rounded-3xl flex items-center justify-center">
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
            @click="fileInput.click()"
            class="px-12 py-3.5 bg-[#1d70f5] hover:bg-blue-700 text-white font-bold rounded-xl shadow-xl shadow-blue-500/20 transition-all transform active:scale-95"
          >
            点击上传
          </button>
        </div>
      </div>
    </main>
  </div>
</template>

<style scoped>
.upload-card {
  /* 使用相对宽度和高度 */
  width: 100%;
  height: 100%;

  /* 设置最大尺寸，确保在大屏幕上不会过度扩张 */
  max-width: 1840px;
  max-height: 860px;

  /* 继承你提供的渐变和边框逻辑 */
  background-image: linear-gradient(181deg,
    #ffffff 0%,
    #ffffff 65%,
    #dfedff 100%);
  box-shadow: 0px 3px 12px 0px rgba(255, 255, 255, 0.8);
  border: solid 2px #ffffff;
}

.animate-fade-in {
  animation: fadeIn 0.8s ease-out forwards;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}
</style>