import request from './request'

// 获取公文列表
export function getDocumentList(params) {
    return request({
        url: '/review/',
        method: 'get',
        params // 包含 page 和 size
    })
}
// 上传公文
export function uploadDocument(file) {
    const formData = new FormData()
    formData.append('file', file)
    return request({
        url: '/review/upload',
        method: 'post',
        data: formData,
        headers: {
            'Content-Type': 'multipart/form-data'
        }
    })
}