import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
    history: createWebHistory(import.meta.env.BASE_URL),
    routes: [
        {
            path: '/login',
            name: 'login',
            component: () => import('../views/LoginView.vue')
        },
        {
            path: '/',
            component: () => import('../layout/MainLayout.vue'), // 统一布局
            redirect: '/review',
            children: [
                {
                    path: 'review',
                    name: 'review-list',
                    component: () => import('../views/DocumentReview/ReviewList.vue'),
                    meta: { title: '公文校审' }
                },
                {
                    path: 'review/create',
                    name: 'review-create',
                    component: () => import('../views/DocumentReview/FileUpload.vue'),
                    meta: { title: '新建校审' }
                },
                {
                    path: 'review/:id',
                    name: 'review-detail',
                    component: () => import('../views/DocumentReview/ReviewDetail.vue'),
                    meta: { title: '公文校审详情' }
                }
            ]
        }
    ]
})

// 导航守卫
router.beforeEach((to, from, next) => {
    const token = localStorage.getItem('token')
    if (to.path !== '/login' && !token) next('/login')
    else next()
})

export default router