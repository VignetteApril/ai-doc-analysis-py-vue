import request from './request'

export function login(data) {
    return request({
        url: '/auth/login',
        method: 'post',
        data // 包含 username 和 password
    })
}

export function changePassword(data) {
    return request({
        url: '/auth/change-password',
        method: 'post',
        data // 包含 old_password 和 new_password
    })
}