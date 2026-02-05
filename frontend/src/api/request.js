import axios from 'axios'

const service = axios.create({
    baseURL: 'http://localhost:8000/api/v1', // 对应你的 FastAPI 地址
    timeout: 5000
})

// --- 请求拦截器：自动注入 Token ---
service.interceptors.request.use(
    config => {
        const token = localStorage.getItem('token')
        if (token) {
            // 在 Header 中加入 Bearer Token
            config.headers['Authorization'] = `Bearer ${token}`
        }
        return config
    },
    error => {
        return Promise.reject(error)
    }
)

// --- 响应拦截器：处理登录失效 ---
service.interceptors.response.use(
    response => response.data,
    error => {
        if (error.response && error.response.status === 401) {
            // 如果后端返回 401，说明 Token 过期或无效
            localStorage.removeItem('token')
            window.location.href = '/login'
        }
        return Promise.reject(error)
    }
)

export default service