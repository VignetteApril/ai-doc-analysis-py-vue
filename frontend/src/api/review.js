import request from './request'

/**
 * 获取公文列表（分页）
 */
export function getDocumentList(params) {
    return request({
        url: '/review/',
        method: 'get',
        params
    })
}

/**
 * 用于详情页初始化加载
 */
export function getDocumentDetail(id) {
    return request({
        url: `/review/${id}`,
        method: 'get'
    })
}

/**
 * 用于编辑器内容的持久化
 */
export function saveDocumentContent(id, html) {
    return request({
        url: `/review/${id}/save`,
        method: 'post',
        data: { html }
    })
}

/**
 * 处理二进制文件流
 */
export function downloadDocumentFile(id) {
    return request({
        url: `/review/${id}/download`,
        method: 'get',
        responseType: 'blob'
    })
}

/**
 * 删除公文记录
 * @param {number} id 公文ID
 */
export function deleteDocument(id) {
    return request({
        url: `/review/${id}`,
        method: 'delete'
    })
}

/**
 * 上传公文文件进行校审 [cite: 2026-02-05]
 * @param {FormData} formData 包含 file 和 name 的表单数据
 */
export function uploadDocument(formData) {
    return request({
        url: '/review/upload', // 确保这个路径与你 FastAPI 定义的上传路由一致
        method: 'post',
        data: formData
    })
}

/**
 * AI 流式分析接口
 */
export function analyzeDocumentAI(docId, data) {
    // 1. 获取 Token
    const token = localStorage.getItem('token') || ''

    // 2. 获取 BaseURL (关键修复点)
    // 必须与 request.js 中的逻辑保持一致，指向后端 8000 端口
    let baseURL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1'

    // 如果 baseURL 结尾有斜杠，去掉它，防止拼成 //review
    if (baseURL.endsWith('/')) {
        baseURL = baseURL.slice(0, -1)
    }

    // 3. 拼接完整 URL
    // 结果示例: http://localhost:8000/api/v1/review/4/analyze
    const url = `${baseURL}/review/${docId}/analyze`

    // 4. 返回原生 fetch Promise
    return fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            // 如果存在 token 则添加
            ...(token ? { 'Authorization': `Bearer ${token}` } : {})
        },
        body: JSON.stringify(data)
    })
}