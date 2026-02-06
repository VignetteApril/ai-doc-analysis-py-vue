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
 * ✅ 补上缺少的：获取单篇公文详情
 * 用于详情页初始化加载
 */
export function getDocumentDetail(id) {
    return request({
        url: `/review/${id}`,
        method: 'get'
    })
}

/**
 * ✅ 补上缺少的：保存文档草稿
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
 * ✅ 补上缺少的：下载导出的 Word 文档
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

// 新增分析接口导出
export function analyzeDocumentAI(id) {
    return request({
        url: `/review/${id}/analyze`,
        method: 'post'
    })
}