import axios from 'axios'

const baseURL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1'

const service = axios.create({
    baseURL: baseURL,
    timeout: 120000
})

// 请求拦截器：注入 Token
service.interceptors.request.use(
    config => {
        const token = localStorage.getItem('token')
        if (token) config.headers['Authorization'] = `Bearer ${token}`
        return config
    },
    error => Promise.reject(error)
)

// 响应拦截器
service.interceptors.response.use(
    response => response.data,
    error => {
        if (error.response?.status === 401) {
            localStorage.clear()
            window.location.href = '/login'
        }
        return Promise.reject(error)
    }
)

export default service