import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
// 🌟 必须确保这一行存在，且路径指向你写了 @tailwind 的那个文件
import './assets/main.css'

const app = createApp(App)
app.use(router)
app.mount('#app')