<template>
  <div class="h-full w-full flex items-center justify-center p-6 md:p-10">
    <div class="upload-card rounded-[40px] p-8 flex flex-col relative shadow-sm">

      <div class="flex items-center justify-between mb-8">
        <div class="flex items-center gap-6">
          <div class="flex items-center gap-3">
            <span class="text-sm text-slate-500">公文名称</span>
            <input type="text" placeholder="请输入" class="px-4 py-2 bg-slate-50 border border-slate-200 rounded-lg text-sm w-56 focus:ring-2 focus:ring-blue-400 focus:outline-none">
          </div>
          <div class="flex items-center gap-3">
            <span class="text-sm text-slate-500">上传时间</span>
            <div class="flex items-center gap-2 text-sm">
              <input type="date" class="px-3 py-2 bg-slate-50 border border-slate-200 rounded-lg">
              <span class="text-slate-300">至</span>
              <input type="date" class="px-3 py-2 bg-slate-50 border border-slate-200 rounded-lg">
            </div>
          </div>
          <div class="flex items-center gap-2 ml-2">
            <button class="px-5 py-2 border border-slate-200 text-slate-600 rounded-lg text-sm hover:bg-slate-50">重置</button>
            <button class="px-5 py-2 bg-[#1d70f5] text-white rounded-lg text-sm hover:bg-blue-700 shadow-md shadow-blue-500/20">查询</button>
          </div>
        </div>

        <button
          @click="$router.push('/review/create')"
          class="flex items-center gap-2 px-6 py-2.5 bg-[#1d70f5] text-white rounded-xl text-sm font-bold hover:bg-blue-700 shadow-lg shadow-blue-500/30 transition-all active:scale-95"
        >
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path d="M12 4v16m8-8H4" stroke-linecap="round" stroke-linejoin="round" stroke-width="3"/></svg>
          新建校审
        </button>
      </div>

      <div class="flex-1 overflow-auto rounded-xl border border-slate-50">
        <table class="w-full text-left">
          <thead class="sticky top-0 z-10">
            <tr class="bg-[#f8faff] text-slate-500 text-sm border-b border-slate-100">
              <th class="px-6 py-4 font-medium">序号</th>
              <th class="px-6 py-4 font-medium">公文名称</th>
              <th class="px-6 py-4 font-medium">上传时间</th>
              <th class="px-6 py-4 font-medium">状态</th>
              <th class="px-6 py-4 font-medium">最近校审</th>
              <th class="px-6 py-4 font-medium">校审数</th>
              <th class="px-6 py-4 font-medium">操作</th>
            </tr>
          </thead>
          <tbody class="text-sm divide-y divide-slate-50">
            <tr v-for="(item, index) in tableData" :key="index" class="hover:bg-slate-50/50 transition-colors">
              <td class="px-6 py-4 text-slate-400">{{ index + 1 }}</td>
              <td class="px-6 py-4 font-medium text-slate-700">{{ item.name }}</td>
              <td class="px-6 py-4 text-slate-400">{{ item.time }}</td>
              <td class="px-6 py-4">
                <span :class="getStatusClass(item.status)" class="px-3 py-1 rounded-full text-xs font-medium">
                  {{ item.status }}
                </span>
              </td>
              <td class="px-6 py-4 text-slate-400">{{ item.lastReview || '—' }}</td>
              <td class="px-6 py-4 text-slate-400">{{ item.count || '—' }}</td>
              <td class="px-6 py-4">
                <div class="flex items-center gap-4 text-blue-500">
                   <button class="hover:text-blue-700" title="编辑"><svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"/></svg></button>
                   <button class="hover:text-blue-700" title="下载"><svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"/></svg></button>
                   <button class="hover:text-red-500" title="删除"><svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"/></svg></button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <div class="mt-6 flex items-center justify-end gap-6 text-sm text-slate-400">
        <span>共 55 条数据</span>
        <div class="flex items-center gap-1">
          <button class="w-8 h-8 flex items-center justify-center rounded hover:bg-slate-100"><svg class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20"><path d="M12.707 5.293a1 1 0 010 1.414L9.414 10l3.293 3.293a1 1 0 01-1.414 1.414l-4-4a1 1 0 010-1.414l4-4a1 1 0 011.414 0z"/></svg></button>
          <button v-for="i in 5" :key="i" :class="i===1?'bg-[#1d70f5] text-white':'hover:bg-slate-100'" class="w-8 h-8 rounded flex items-center justify-center transition-colors">{{i}}</button>
          <button class="w-8 h-8 flex items-center justify-center rounded hover:bg-slate-100"><svg class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20"><path d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z"/></svg></button>
        </div>
        <div class="flex items-center gap-2">
           <select class="bg-white border border-slate-200 rounded px-2 py-1 focus:outline-none">
             <option>12条/页</option>
           </select>
           <span>跳至 <input type="text" value="4" class="w-10 border border-slate-200 rounded px-1 py-0.5 text-center focus:outline-none text-slate-600"> 页</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const tableData = ref([
  { name: '关于印发2024年数字化转型方案的通知', time: '2024-08-07', status: '校审中', lastReview: '2024-08-07', count: 2 },
  { name: '某省人民政府关于加强公文规范性的意见', time: '2024-08-06', status: '未校审', lastReview: null, count: 0 },
  { name: '集团公司第三季度安全生产汇报稿', time: '2024-08-05', status: '已校审', lastReview: '2024-08-06', count: 4 },
  { name: '某市教体局2024年秋季招生政策补充说明', time: '2024-08-04', status: '未校审', lastReview: null, count: 0 },
])

const getStatusClass = (status) => {
  switch (status) {
    case '校审中': return 'bg-orange-50 text-orange-500'
    case '已校审': return 'bg-emerald-50 text-emerald-500'
    default: return 'bg-slate-100 text-slate-500'
  }
}
</script>

<style scoped>
.upload-card {
  width: 100%; height: 100%; max-width: 1840px; max-height: 860px;
  background-image: linear-gradient(181deg, #ffffff 0%, #ffffff 65%, #dfedff 100%);
  box-shadow: 0px 3px 12px 0px rgba(255, 255, 255, 0.8);
  border: solid 2px #ffffff;
}
</style>