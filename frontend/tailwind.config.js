/** @type {import('tailwindcss').Config} */
export default {
    // 🌟 确保 content 包含了所有 vue 文件
    content: [
        "./index.html",
        "./src/**/*.{vue,js,ts,jsx,tsx}",
    ],
    theme: {
        extend: {},
    },
    plugins: [],
}