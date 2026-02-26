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
