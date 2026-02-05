<template>
  <div class="h-full w-full flex items-center justify-center p-6 md:p-10">
    <div class="upload-card rounded-[40px] p-8 flex flex-col relative shadow-sm">

      <div class="flex items-center justify-between mb-8">
        <div class="flex items-center gap-6">
          <div class="flex items-center gap-3">
            <span class="text-sm text-slate-500">公文名称</span>
            <input
              v-model="filters.name"
              type="text"
              placeholder="请输入"
              class="px-4 py-2 bg-slate-50 border border-slate-200 rounded-lg text-sm w-56 focus:ring-2 focus:ring-blue-400 focus:outline-none"
            >
          </div>
          <div class="flex items-center gap-3">
            <span class="text-sm text-slate-500">上传时间</span>
            <div class="flex items-center gap-2 text-sm">
              <input v-model="filters.start" type="date" class="px-3 py-2 bg-slate-50 border border-slate-200 rounded-lg">
              <span class="text-slate-300">至</span>
              <input v-model="filters.end" type="date" class="px-3 py-2 bg-slate-50 border border-slate-200 rounded-lg">
            </div>
          </div>
          <div class="flex items-center gap-2 ml-2">
            <button @click="resetFilters" class="px-5 py-2 border border-slate-200 text-slate-600 rounded-lg text-sm hover:bg-slate-50 transition-colors">重置</button>
            <button @click="handleSearch" class="px-5 py-2 bg-[#1d70f5] text-white rounded-lg text-sm hover:bg-blue-700 shadow-md shadow-blue-500/20 transition-all">查询</button>
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

      <div class="flex-1 overflow-auto rounded-xl border border-slate-50 relative">
        <div v-if="loading" class="absolute inset-0 bg-white/50 backdrop-blur-[2px] z-20 flex items-center justify-center">
          <div class="w-10 h-10 border-4 border-blue-600 border-t-transparent rounded-full animate-spin"></div>
        </div>

        <table class="w-full text-left">
          <thead class="sticky top-0 z-10">
            <tr class="bg-[#f8faff] text-slate-500 text-sm border-b border-slate-100">
              <th class="px-6 py-4 font-medium">序号</th>
              <th class="px-6 py-4 font-medium">公文名称</th>
              <th class="px-6 py-4 font-medium text-center">上传时间</th>
              <th class="px-6 py-4 font-medium text-center">状态</th>
              <th class="px-6 py-4 font-medium text-center">最近校审</th>
              <th class="px-6 py-4 font-medium text-center">校审数</th>
              <th class="px-6 py-4 font-medium text-center">操作</th>
            </tr>
          </thead>
          <tbody class="text-sm divide-y divide-slate-50">
            <tr v-if="tableData.length === 0 && !loading">
              <td colspan="7" class="px-6 py-20 text-center text-slate-400">暂无相关公文记录</td>
            </tr>
            <tr v-for="(item, index) in tableData" :key="item.id" class="hover:bg-slate-50/50 transition-colors">
              <td class="px-6 py-4 text-slate-400">{{ (currentPage - 1) * pageSize + index + 1 }}</td>
              <td class="px-6 py-4 font-medium text-slate-700">{{ item.name }}</td>
              <td class="px-6 py-4 text-slate-400 text-center">{{ item.time }}</td>
              <td class="px-6 py-4 text-center">
                <span :class="getStatusClass(item.status)" class="px-3 py-1 rounded-full text-xs font-medium">
                  {{ item.status }}
                </span>
              </td>
              <td class="px-6 py-4 text-slate-400 text-center">{{ item.lastReview || '—' }}</td>
              <td class="px-6 py-4 text-slate-400 text-center">{{ item.count || 0 }}</td>
              <td class="px-6 py-4">
                <div class="flex items-center justify-center gap-4 text-blue-500">
                   <button
                     class="hover:text-blue-700 transition-colors"
                     title="编辑/校审"
                     @click="handleEdit(item.id)"
                   >
                     <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                       <path d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"/>
                     </svg>
                   </button>
                   <button class="hover:text-blue-700 transition-colors" title="下载文件">
                     <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                       <path d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"/>
                     </svg>
                   </button>
                   <button @click="handleDelete(item.id)" class="hover:text-red-500 transition-colors" title="删除">
                     <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                       <path d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"/>
                     </svg>
                   </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <div class="mt-6 flex items-center justify-end gap-6 text-sm text-slate-400">
        <span>共 {{ total }} 条数据</span>
        <div class="flex items-center gap-1">
          <button
            @click="changePage(currentPage - 1)"
            :disabled="currentPage === 1 || loading"
            class="w-8 h-8 flex items-center justify-center rounded hover:bg-slate-100 disabled:opacity-30 transition-all"
          >
            <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20"><path d="M12.707 5.293a1 1 0 010 1.414L9.414 10l3.293 3.293a1 1 0 01-1.414 1.414l-4-4a1 1 0 010-1.414l4-4a1 1 0 011.414 0z"/></svg>
          </button>

          <button
            v-for="p in totalPages"
            :key="p"
            @click="changePage(p)"
            :class="p === currentPage ? 'bg-[#1d70f5] text-white shadow-md' : 'hover:bg-slate-100'"
            class="w-8 h-8 rounded flex items-center justify-center transition-all"
          >
            {{ p }}
          </button>

          <button
            @click="changePage(currentPage + 1)"
            :disabled="currentPage === totalPages || loading"
            class="w-8 h-8 flex items-center justify-center rounded hover:bg-slate-100 disabled:opacity-30 transition-all"
          >
            <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20"><path d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z"/></svg>
          </button>
        </div>
        <div class="flex items-center gap-2">
           <select
             v-model="pageSize"
             @change="handleSearch"
             class="bg-white border border-slate-200 rounded px-2 py-1 focus:outline-none cursor-pointer"
           >
             <option :value="10">10条/页</option>
             <option :value="12">12条/页</option>
             <option :value="20">20条/页</option>
             <option :value="50">50条/页</option>
           </select>
           <span>跳至
             <input
               type="text"
               v-model.lazy="jumpPage"
               class="w-10 border border-slate-200 rounded px-1 py-0.5 text-center focus:outline-none text-slate-600"
               @keyup.enter="handleJump"
             > 页
           </span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { getDocumentList } from '@/api/review'

const router = useRouter()

// --- 状态定义 ---
const tableData = ref([])
const total = ref(0)
const loading = ref(false)
const currentPage = ref(1)
const pageSize = ref(12)
const jumpPage = ref(1)

const filters = reactive({
  name: '',
  start: '',
  end: ''
})

// --- 计算属性 ---
const totalPages = computed(() => Math.ceil(total.value / pageSize.value) || 1)

// --- 核心方法 ---

// 1. 获取列表数据
const fetchList = async () => {
  loading.value = true
  try {
    const res = await getDocumentList({
      page: currentPage.value,
      size: pageSize.value,
      name: filters.name,
      start_date: filters.start,
      end_date: filters.end
    })

    // 对接后端返回的字典结构 { total, items } [cite: 2026-02-05]
    tableData.value = res.items
    total.value = res.total
    jumpPage.value = currentPage.value
  } catch (error) {
    console.error('获取列表失败:', error)
  } finally {
    loading.value = false
  }
}

// 2. 跳转到详情页
const handleEdit = (id) => {
  // 使用命名路由跳转，并携带 ID 参数
  router.push({
    name: 'review-detail',
    params: { id: id }
  })
}

// 3. 搜索与重置
const handleSearch = () => {
  currentPage.value = 1
  fetchList()
}

const resetFilters = () => {
  filters.name = ''
  filters.start = ''
  filters.end = ''
  handleSearch()
}

// 4. 分页逻辑
const changePage = (p) => {
  if (p < 1 || p > totalPages.value) return
  currentPage.value = p
  fetchList()
}

const handleJump = () => {
  const p = parseInt(jumpPage.value)
  if (!isNaN(p)) changePage(p)
}

// 5. 删除逻辑
const handleDelete = async (id) => {
  if (confirm('确定要删除这份公文记录吗？')) {
    console.log('执行删除 ID:', id)
    // 此处待对接删除接口
  }
}

// 6. 状态颜色转换
const getStatusClass = (status) => {
  switch (status) {
    case '校审中': return 'bg-orange-50 text-orange-500'
    case '已校审': return 'bg-emerald-50 text-emerald-500'
    default: return 'bg-slate-100 text-slate-500'
  }
}

// --- 生命周期 ---
onMounted(() => {
  fetchList()
})
</script>

<style scoped>
.upload-card {
  width: 100%;
  height: 100%;
  max-width: 1840px;
  max-height: 860px;
  background-image: linear-gradient(181deg, #ffffff 0%, #ffffff 65%, #dfedff 100%);
  box-shadow: 0px 3px 12px 0px rgba(255, 255, 255, 0.8);
  border: solid 2px #ffffff;
}

select {
  appearance: none;
  background-image: url("data:image/svg+xml;charset=UTF-8,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='currentColor' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpolyline points='6 9 12 15 18 9'%3E%3C/polyline%3E%3C/svg%3E");
  background-repeat: no-repeat;
  background-position: right 0.5rem center;
  background-size: 1em;
  padding-right: 2rem;
}
</style>