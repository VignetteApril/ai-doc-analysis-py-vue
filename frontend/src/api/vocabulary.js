import request from './request'

/**
 * 获取词库列表（分页+搜索+日期过滤）
 */
export function getVocabularyList(params) {
    return request({
        url: '/vocabulary/',
        method: 'get',
        params
    })
}

/**
 * 新增替换词条
 */
export function createVocabulary(data) {
    return request({
        url: '/vocabulary/',
        method: 'post',
        data
    })
}

/**
 * 修改词条
 */
export function updateVocabulary(id, data) {
    return request({
        url: `/vocabulary/${id}`,
        method: 'put',
        data
    })
}

/**
 * 删除词条
 */
export function deleteVocabulary(id) {
    return request({
        url: `/vocabulary/${id}`,
        method: 'delete'
    })
}

/**
 * 导入词库文件（pdf/txt/doc/docx）
 */
export function importVocabularyFile(formData) {
    return request({
        url: '/vocabulary/import',
        method: 'post',
        data: formData
    })
}

/**
 * 上传文档并预览 AI 提取结果
 */
export function previewVocabularyImport(formData) {
    return request({
        url: '/vocabulary/import/preview',
        method: 'post',
        data: formData
    })
}

/**
 * 确认导入预览结果
 */
export function confirmVocabularyImport(data) {
    return request({
        url: '/vocabulary/import/confirm',
        method: 'post',
        data
    })
}
