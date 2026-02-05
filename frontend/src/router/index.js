import { createRouter, createWebHistory } from 'vue-router'
import LoginView from '../views/LoginView.vue'

const router = createRouter({
    history: createWebHistory(import.meta.env.BASE_URL),
    routes: [
        {
            path: '/',
            name: 'home',
            redirect: '/dashboard' // 修改：默认尝试去仪表盘
        },
        {
            path: '/login',
            name: 'login',
            component: LoginView,
            meta: { requiresAuth: false } // 标记：不需要登录即可访问
        },
        {
            path: '/dashboard',
            name: 'dashboard',
            component: () => import('../views/DashboardView.vue'),
            meta: { requiresAuth: true } // 标记：必须登录才能访问
        }
    ]
})

// --- 全局路由守卫 ---
router.beforeEach((to, from, next) => {
    // 1. 获取本地存储的 Token
    const token = localStorage.getItem('token')

    // 2. 检查目标路由是否需要登录权限
    const requiresAuth = to.matched.some(record => record.meta.requiresAuth)

    if (requiresAuth && !token) {
        // 情况 A：访问受限页面但没登录 -> 踢回登录页
        next({ name: 'login' })
    } else if (to.name === 'login' && token) {
        // 情况 B：已经登录了还想去登录页 -> 直接送去仪表盘
        next({ name: 'dashboard' })
    } else {
        // 情况 C：正常放行
        next()
    }
})

export default router