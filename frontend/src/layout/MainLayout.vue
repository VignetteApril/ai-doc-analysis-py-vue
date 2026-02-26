<template>
  <div class="h-screen bg-[#f0f5ff] flex flex-col font-sans relative overflow-hidden">
    <div class="absolute top-0 left-0 w-full h-full pointer-events-none">
      <div class="absolute top-[-10%] left-[-10%] w-[40%] h-[40%] bg-blue-200/20 blur-[120px] rounded-full"></div>
      <div class="absolute bottom-[-10%] right-[-10%] w-[40%] h-[40%] bg-purple-200/10 blur-[120px] rounded-full"></div>
    </div>

    <nav class="h-16 bg-white/70 backdrop-blur-xl border-b border-white/50 px-8 flex items-center sticky top-0 z-50 shadow-sm">
      <div class="flex-1 flex items-center">
        <div class="flex items-center gap-2.5 cursor-pointer" @click="$router.push('/')">
          <div class="w-9 h-9 bg-[#1d70f5] rounded-lg flex items-center justify-center shadow-lg shadow-blue-500/30">
            <span class="text-white font-bold italic text-lg">Ai</span>
          </div>
          <span class="text-xl font-bold text-slate-800 tracking-tight">AI公文校对系统</span>
        </div>
      </div>

      <div class="flex items-center gap-10 h-16 shrink-0">
        <router-link
          to="/review"
          class="relative font-semibold flex items-center gap-2 h-full transition-colors"
          :class="$route.path.includes('/review') ? 'text-[#1d70f5]' : 'text-slate-500 hover:text-slate-800'"
        >
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"/></svg>
          公文校审
          <div v-if="$route.path.includes('/review')" class="absolute bottom-0 left-0 w-full h-0.5 bg-[#1d70f5] rounded-full"></div>
        </router-link>

        <router-link
          to="/vocabulary"
          class="relative font-semibold flex items-center gap-2 h-full transition-colors"
          :class="$route.path.includes('/vocabulary') ? 'text-[#1d70f5]' : 'text-slate-500 hover:text-slate-800'"
        >
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path d="M4 7v10c0 2.21 3.582 4 8 4s8-1.79 8-4V7M4 7c0 2.21 3.582 4 8 4s8-1.79 8-4M4 7c0-2.21 3.582-4 8-4s8 1.79 8 4m0 5c0 2.21-3.582 4-8 4s-8-1.79-8-4" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"/></svg>
          词库管理
          <div v-if="$route.path.includes('/vocabulary')" class="absolute bottom-0 left-0 w-full h-0.5 bg-[#1d70f5] rounded-full"></div>
        </router-link>
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
            <span class="text-xs text-slate-500 flex items-center gap-1 group-hover:text-slate-800">
              更多
              <svg class="w-3 h-3 transition-transform duration-300" :class="{'rotate-180': showUserMenu}" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path d="M19 9l-7 7-7-7" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"/></svg>
            </span>
          </div>

          <Transition name="menu-fade">
            <div v-if="showUserMenu" class="absolute right-0 top-12 w-40 bg-white rounded-xl shadow-2xl border border-slate-100 py-2 z-[60]">
              <button @click="openChangePwd" class="w-full px-4 py-2.5 text-left text-sm text-slate-600 hover:bg-blue-50 hover:text-blue-600 flex items-center gap-2 transition-colors">
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

    <main class="flex-1 relative z-10 overflow-hidden">
      <router-view v-slot="{ Component }">
        <transition name="page-fade" mode="out-in">
          <component :is="Component" />
        </transition>
      </router-view>
    </main>

    <!-- 修改密码弹窗 -->
    <Transition name="modal">
      <div v-if="pwdModal.show" class="fixed inset-0 z-[200] flex items-center justify-center">
        <div class="absolute inset-0 bg-black/20 backdrop-blur-sm" @click="closeChangePwd"></div>
        <div class="relative bg-white rounded-3xl shadow-2xl w-[420px] p-8 z-10">

          <!-- 标题 -->
          <div class="flex items-center gap-3 mb-6">
            <div class="w-9 h-9 bg-blue-50 rounded-xl flex items-center justify-center">
              <svg class="w-5 h-5 text-[#1d70f5]" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"/></svg>
            </div>
            <h3 class="text-lg font-bold text-slate-800">修改密码</h3>
          </div>

          <!-- 表单 -->
          <div class="space-y-4">
            <div>
              <label class="block text-sm font-medium text-slate-600 mb-1.5">原密码</label>
              <div class="relative">
                <input
                  v-model="pwdForm.old_password"
                  :type="pwdShow.old ? 'text' : 'password'"
                  placeholder="请输入原密码"
                  class="w-full px-4 py-2.5 pr-10 bg-slate-50 border border-slate-200 rounded-xl text-sm focus:ring-2 focus:ring-blue-400 focus:outline-none"
                  :class="{'border-red-300 focus:ring-red-300': pwdError}"
                >
                <button type="button" @click="pwdShow.old = !pwdShow.old" class="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600">
                  <svg v-if="pwdShow.old" class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"/><path d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"/></svg>
                  <svg v-else class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.478 0 8.268 2.943 9.543 7a10.025 10.025 0 01-4.132 5.411m0 0L21 21" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"/></svg>
                </button>
              </div>
            </div>

            <div>
              <label class="block text-sm font-medium text-slate-600 mb-1.5">新密码</label>
              <div class="relative">
                <input
                  v-model="pwdForm.new_password"
                  :type="pwdShow.new ? 'text' : 'password'"
                  placeholder="请输入新密码（不少于6位）"
                  class="w-full px-4 py-2.5 pr-10 bg-slate-50 border border-slate-200 rounded-xl text-sm focus:ring-2 focus:ring-blue-400 focus:outline-none"
                >
                <button type="button" @click="pwdShow.new = !pwdShow.new" class="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600">
                  <svg v-if="pwdShow.new" class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"/><path d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"/></svg>
                  <svg v-else class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.478 0 8.268 2.943 9.543 7a10.025 10.025 0 01-4.132 5.411m0 0L21 21" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"/></svg>
                </button>
              </div>
            </div>

            <div>
              <label class="block text-sm font-medium text-slate-600 mb-1.5">确认新密码</label>
              <div class="relative">
                <input
                  v-model="pwdForm.confirm_password"
                  :type="pwdShow.confirm ? 'text' : 'password'"
                  placeholder="再次输入新密码"
                  class="w-full px-4 py-2.5 pr-10 bg-slate-50 border border-slate-200 rounded-xl text-sm focus:ring-2 focus:ring-blue-400 focus:outline-none"
                  :class="{'border-red-300': pwdForm.confirm_password && pwdForm.new_password !== pwdForm.confirm_password}"
                  @keyup.enter="handleChangePwd"
                >
                <button type="button" @click="pwdShow.confirm = !pwdShow.confirm" class="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600">
                  <svg v-if="pwdShow.confirm" class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"/><path d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"/></svg>
                  <svg v-else class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.478 0 8.268 2.943 9.543 7a10.025 10.025 0 01-4.132 5.411m0 0L21 21" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"/></svg>
                </button>
              </div>
              <p v-if="pwdForm.confirm_password && pwdForm.new_password !== pwdForm.confirm_password" class="mt-1.5 text-xs text-red-500">两次密码输入不一致</p>
            </div>

            <!-- 错误提示 -->
            <div v-if="pwdError" class="flex items-center gap-2 px-3 py-2.5 bg-red-50 border border-red-100 rounded-xl">
              <svg class="w-4 h-4 text-red-500 shrink-0" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clip-rule="evenodd"/></svg>
              <span class="text-xs text-red-600">{{ pwdError }}</span>
            </div>
          </div>

          <!-- 按钮 -->
          <div class="flex items-center justify-end gap-3 mt-7">
            <button @click="closeChangePwd" class="px-6 py-2.5 border border-slate-200 text-slate-600 rounded-xl text-sm hover:bg-slate-50 transition-colors">取消</button>
            <button
              @click="handleChangePwd"
              :disabled="pwdModal.saving"
              class="px-6 py-2.5 bg-[#1d70f5] text-white rounded-xl text-sm font-bold hover:bg-blue-700 transition-all disabled:opacity-50 flex items-center gap-2"
            >
              <span v-if="pwdModal.saving" class="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></span>
              确认修改
            </button>
          </div>
        </div>
      </div>
    </Transition>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { changePassword } from '@/api/auth'

const router = useRouter()
const username = ref('张三')
const showUserMenu = ref(false)
const userMenuRef = ref(null)

const handleClickOutside = (event) => {
  if (userMenuRef.value && !userMenuRef.value.contains(event.target)) showUserMenu.value = false
}

onMounted(() => {
  username.value = localStorage.getItem('username') || '管理员'
  window.addEventListener('click', handleClickOutside)
})

onUnmounted(() => window.removeEventListener('click', handleClickOutside))

const handleLogout = () => {
  localStorage.clear()
  router.push('/login')
}

// ── 修改密码弹窗 ──────────────────────────────────────────────
const pwdModal = reactive({ show: false, saving: false })
const pwdForm = reactive({ old_password: '', new_password: '', confirm_password: '' })
const pwdShow = reactive({ old: false, new: false, confirm: false })
const pwdError = ref('')

const openChangePwd = () => {
  showUserMenu.value = false
  pwdForm.old_password = ''
  pwdForm.new_password = ''
  pwdForm.confirm_password = ''
  pwdShow.old = false
  pwdShow.new = false
  pwdShow.confirm = false
  pwdError.value = ''
  pwdModal.show = true
}

const closeChangePwd = () => {
  pwdModal.show = false
}

const handleChangePwd = async () => {
  pwdError.value = ''

  if (!pwdForm.old_password || !pwdForm.new_password || !pwdForm.confirm_password) {
    pwdError.value = '请填写所有字段'
    return
  }
  if (pwdForm.new_password !== pwdForm.confirm_password) {
    pwdError.value = '两次密码输入不一致'
    return
  }
  if (pwdForm.new_password.length < 6) {
    pwdError.value = '新密码长度不能少于6位'
    return
  }

  pwdModal.saving = true
  try {
    await changePassword({
      old_password: pwdForm.old_password,
      new_password: pwdForm.new_password
    })
    closeChangePwd()
    // 修改成功后重新登录
    localStorage.clear()
    router.push('/login')
  } catch (err) {
    pwdError.value = err?.response?.data?.detail || '修改失败，请稍后重试'
  } finally {
    pwdModal.saving = false
  }
}
</script>

<style scoped>
.menu-fade-enter-active, .menu-fade-leave-active { transition: all 0.2s ease; }
.menu-fade-enter-from, .menu-fade-leave-to { opacity: 0; transform: translateY(-10px); }

.page-fade-enter-active, .page-fade-leave-active { transition: opacity 0.3s ease; }
.page-fade-enter-from, .page-fade-leave-to { opacity: 0; }

.modal-enter-active, .modal-leave-active { transition: opacity 0.25s ease; }
.modal-enter-from, .modal-leave-to { opacity: 0; }
.modal-enter-active .relative, .modal-leave-active .relative { transition: transform 0.25s ease; }
.modal-enter-from .relative { transform: scale(0.95) translateY(10px); }
</style>
