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
        <a href="#" class="relative text-[#1d70f5] font-semibold flex items-center gap-2 h-full group">
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
        <div class="relative" ref="userMenuRef">
          <div
            @click="showUserMenu = !showUserMenu"
            class="flex items-center gap-3 bg-white/50 border border-slate-200 py-1.5 pl-2 pr-4 rounded-full cursor-pointer hover:bg-white transition-all select-none"
            :class="{'bg-white border-blue-200 shadow-sm': showUserMenu}"
          >
            <img src="https://api.dicebear.com/7.x/avataaars/svg?seed=Jack" class="w-7 h-7 rounded-full bg-blue-100" />
            <span class="text-sm font-medium text-slate-700">{{ username }}</span>
            <div class="h-3 w-[1px] bg-slate-300 mx-1"></div>
            <span class="text-xs text-slate-500 flex items-center gap-1">
              更多
              <svg
                class="w-3 h-3 transition-transform duration-300"
                :class="{'rotate-180': showUserMenu}"
                fill="none" stroke="currentColor" viewBox="0 0 24 24"
              >
                <path d="M19 9l-7 7-7-7" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"/>
              </svg>
            </span>
          </div>

          <Transition name="menu-fade">
            <div
              v-if="showUserMenu"
              class="absolute right-0 top-12 w-40 bg-white rounded-xl shadow-2xl border border-slate-100 py-2 z-[60]"
            >
              <button class="w-full px-4 py-2.5 text-left text-sm text-slate-600 hover:bg-blue-50 hover:text-blue-600 flex items-center gap-2 transition-colors">
                <svg class="w-4 h-4 text-blue-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"/></svg>
                修改密码
              </button>
              <div class="h-[1px] bg-slate-50 my-1 mx-2"></div>
              <button @click="handleLogout" class="w-full px-4 py-2.5 text-left text-sm text-red-500 hover:bg-red-50 flex items-center gap-2 transition-colors">
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"/></svg>
                退出登录
              </button>
            </div>
          </Transition>
        </div>
      </div>
    </nav>

    <main class="flex-1 p-6 md:p-10 flex items-center justify-center overflow-hidden">
      <div
        class="upload-card rounded-[40px] flex flex-col items-center justify-center relative transition-all duration-300"
        @dragover.prevent="isDragging = true"
        @dragleave.prevent="isDragging = false"
        @drop.prevent="handleDrop"
        :class="{'scale-[1.01] border-blue-200': isDragging}"
      >
        <div class="flex flex-col items-center animate-fade-in">
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

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const username = ref('张三')
const isDragging = ref(false)
const showUserMenu = ref(false)
const userMenuRef = ref(null)
const fileInput = ref(null)

// 1. 处理点击外部关闭用户菜单的逻辑
const handleClickOutside = (event) => {
  if (userMenuRef.value && !userMenuRef.value.contains(event.target)) {
    showUserMenu.value = false
  }
}

onMounted(() => {
  // 从本地恢复登录信息
  const savedName = localStorage.getItem('username')
  if (savedName) username.value = savedName
  window.addEventListener('click', handleClickOutside)
})

onUnmounted(() => {
  window.removeEventListener('click', handleClickOutside)
})

// 2. 退出登录逻辑
const handleLogout = () => {
  localStorage.removeItem('token')
  localStorage.removeItem('username')
  router.push('/login')
}

// 3. 文件处理逻辑
const handleDrop = (e) => {
  isDragging.value = false
  const files = e.dataTransfer.files
  if (files.length > 0) processFile(files[0])
}

const handleFileChange = (e) => {
  const files = e.target.files
  if (files.length > 0) processFile(files[0])
}

const processFile = (file) => {
  console.log('正在解析公文内容:', file.name)
  // 下一步：实现 axios 上传并触发后端校对任务
}
</script>

<style scoped>
/* 精准复刻您提供的线性渐变参数 */
.upload-card {
  width: 100%;
  height: 100%;
  max-width: 1840px;
  max-height: 860px;

  background-image: linear-gradient(181deg,
    #ffffff 0%,
    #ffffff 65%,
    #dfedff 100%);
  box-shadow: 0px 3px 12px 0px rgba(255, 255, 255, 0.8);
  border: solid 2px #ffffff;
}

/* 导航栏下拉菜单动画 */
.menu-fade-enter-active, .menu-fade-leave-active {
  transition: all 0.2s ease;
}
.menu-fade-enter-from, .menu-fade-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}

/* 页面加载动画 */
.animate-fade-in {
  animation: fadeIn 0.8s ease-out forwards;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}
</style>