<template>
  <div class="min-h-screen w-full flex items-center justify-center lg:justify-end p-4 md:p-8 lg:pr-40 relative overflow-hidden font-sans">

    <div class="absolute inset-0 z-0">
      <img
        src="@/assets/images/login-bg.png"
        class="w-full h-full object-cover object-center pointer-events-none"
        alt="Login Background"
      />
      <div class="absolute inset-0 bg-slate-900/5"></div>
    </div>

    <div class="absolute top-8 left-8 md:top-12 md:left-12 z-20 flex items-center gap-3 animate-fade-in-down">
      <div class="w-10 h-10 bg-blue-600 rounded-lg flex items-center justify-center shadow-xl shadow-blue-500/40">
        <span class="text-white font-bold italic text-xl">Ai</span>
      </div>
      <h1 class="text-xl md:text-2xl font-bold text-slate-800 tracking-tight">AI 公文校对系统</h1>
    </div>

    <div class="z-10 w-full max-w-md animate-fade-in-up">
      <div class="bg-white/90 backdrop-blur-md rounded-[32px] shadow-[0_20px_50px_rgba(0,0,0,0.1)] p-10 border border-white">

        <div class="mb-10 text-center">
          <h2 class="text-2xl font-bold text-slate-800 mb-2">用户登录</h2>
          <div class="w-12 h-1.5 bg-blue-600 rounded-full mx-auto"></div>
        </div>

        <form @submit.prevent="handleLogin" class="space-y-6">
          <div class="relative group">
            <span class="absolute left-4 top-1/2 -translate-y-1/2 text-slate-400 group-focus-within:text-blue-600 transition-colors">
              <svg xmlns="http://www.w3.org/2000/svg" class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
              </svg>
            </span>
            <input
              v-model="loginForm.username"
              type="text"
              placeholder="请输入用户名"
              class="w-full pl-12 pr-4 py-4 bg-slate-50 border border-slate-100 rounded-2xl focus:outline-none focus:ring-2 focus:ring-blue-400 focus:bg-white transition-all text-slate-700"
              required
            />
          </div>

          <div class="relative group">
            <span class="absolute left-4 top-1/2 -translate-y-1/2 text-slate-400 group-focus-within:text-blue-600 transition-colors">
              <svg xmlns="http://www.w3.org/2000/svg" class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
              </svg>
            </span>
            <input
              v-model="loginForm.password"
              type="password"
              placeholder="请输入密码"
              class="w-full pl-12 pr-4 py-4 bg-slate-50 border border-slate-100 rounded-2xl focus:outline-none focus:ring-2 focus:ring-blue-400 focus:bg-white transition-all text-slate-700"
              required
            />
          </div>

          <div class="flex items-center justify-between text-sm">
            <label class="flex items-center gap-2 cursor-pointer text-slate-500 hover:text-slate-700">
              <input
                v-model="loginForm.remember"
                type="checkbox"
                class="w-4 h-4 rounded border-slate-300 text-blue-600 focus:ring-blue-500"
              >
              记住密码
            </label>
          </div>

          <button
            type="submit"
            :disabled="loading"
            class="w-full py-4 bg-blue-600 hover:bg-blue-700 disabled:bg-blue-300 text-white font-bold rounded-2xl shadow-xl shadow-blue-200 transition-all transform active:scale-[0.98] flex items-center justify-center gap-3"
          >
            <span v-if="loading" class="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin"></span>
            <span>{{ loading ? '验证中...' : '登 录' }}</span>
          </button>
        </form>

        <Transition name="fade">
          <div v-if="errMsg" class="mt-6 p-3 bg-red-50 border border-red-100 rounded-xl flex items-center gap-2 text-red-600 text-sm">
            <svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            {{ errMsg }}
          </div>
        </Transition>
      </div>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
// 导入我们定义的登录 API
import { login } from '@/api/auth'

const router = useRouter()
const loading = ref(false)
const errMsg = ref('')

const loginForm = reactive({
  username: '',
  password: '',
  remember: false // 增加记住密码的状态逻辑
})

// 页面加载时，尝试从本地恢复用户名（如果之前勾选了记住密码）
onMounted(() => {
  const savedUser = localStorage.getItem('saved_username')
  if (savedUser) {
    loginForm.username = savedUser
    loginForm.remember = true
  }
})

const handleLogin = async () => {
  if (!loginForm.username || !loginForm.password) {
    errMsg.value = '请填写完整信息'
    return
  }

  loading.value = true
  errMsg.value = ''

  try {
    // 使用封装好的 login 函数
    const res = await login({
      username: loginForm.username,
      password: loginForm.password
    })

    // 1. 存储核心数据
    localStorage.setItem('token', res.access_token)
    localStorage.setItem('username', res.username)

    // 2. 记住密码逻辑：如果勾选则存用户名，否则清除
    if (loginForm.remember) {
      localStorage.setItem('saved_username', loginForm.username)
    } else {
      localStorage.removeItem('saved_username')
    }

    // 3. 跳转至仪表盘
    router.push('/dashboard')

  } catch (error) {
    // 捕获后端返回的错误信息（如“用户名或密码错误”）
    console.error('Login Error:', error)
    errMsg.value = error.response?.data?.detail || '登录失败，请检查网络连接'
  } finally {
    loading.value = false
  }
}
</script>