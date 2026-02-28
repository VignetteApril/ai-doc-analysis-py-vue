<template>
  <div class="h-full w-full flex items-center justify-center p-6 md:p-10 font-sans">
    <div class="upload-card rounded-[40px] p-8 flex flex-col relative shadow-sm overflow-hidden">

      <div class="flex items-center justify-between mb-8">
        <div class="flex items-center gap-6">
          <div class="flex items-center gap-3">
            <span class="text-sm text-slate-500">公文名称</span>
            <input
              v-model="filters.name"
              type="text"
              placeholder="请输入"
              class="px-4 py-2 bg-slate-50 border border-slate-200 rounded-lg text-sm w-56 focus:ring-2 focus:ring-blue-400 focus:outline-none"
              @keyup.enter="handleSearch"
            >
          </div>
          <div class="flex items-center gap-3 text-sm">
            <span class="text-slate-500">上传时间</span>
            <div class="flex items-center gap-2">
              <input v-model="filters.start" type="date" class="px-3 py-2 bg-slate-50 border border-slate-200 rounded-lg">
              <span class="text-slate-300">至</span>
              <input v-model="filters.end" type="date" class="px-3 py-2 bg-slate-50 border border-slate-200 rounded-lg">
            </div>
          </div>
          <div class="flex items-center gap-2 ml-2">
            <button @click="resetFilters" class="px-5 py-2 border border-slate-200 text-slate-600 rounded-lg text-sm hover:bg-slate-50 transition-colors">重置</button>
            <button @click="handleSearch" class="px-5 py-2 bg-[#1d70f5] text-white rounded-lg text-sm hover:bg-blue-700 shadow-md transition-all">查询</button>
          </div>
        </div>

        <button
          @click="goToCreate"
          class="flex items-center gap-2 px-6 py-2.5 bg-[#1d70f5] text-white rounded-xl text-sm font-bold hover:bg-blue-700 shadow-lg transition-all active:scale-95"
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
              <th class="px-6 py-4 font-medium text-center">操作</th>
            </tr>
          </thead>
          <tbody class="text-sm divide-y divide-slate-50">
            <tr v-if="tableData.length === 0 && !loading">
              <td colspan="6" class="px-6 py-20 text-center text-slate-400 font-medium tracking-wide">暂无匹配的公文记录</td>
            </tr>
            <tr v-for="(item, index) in tableData" :key="item.id" class="hover:bg-slate-50/50 transition-colors">
              <td class="px-6 py-4 text-slate-400">{{ (currentPage - 1) * pageSize + index + 1 }}</td>
              <td class="px-6 py-4 font-medium text-slate-700">{{ item.name }}</td>
              <td class="px-6 py-4 text-slate-400 text-center">{{ item.time }}</td>
              <td class="px-6 py-4 text-center">
                <span :class="getStatusClass(item.status)" class="px-3 py-1 rounded-full text-xs font-bold">
                  {{ item.status }}
                </span>
              </td>
              <td class="px-6 py-4 text-slate-400 text-center">{{ item.lastReview || '—' }}</td>
              <td class="px-6 py-4">
                <div class="flex items-center justify-center gap-4 text-[#1d70f5]">
                   <button @click="handleEdit(item.id)" class="hover:scale-110 transition-transform" title="校对详情"><svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"/></svg></button>
                   <button class="hover:scale-110 transition-transform" title="下载"><svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"/></svg></button>
                   <button @click="handleDelete(item.id)" class="hover:text-red-500 hover:scale-110 transition-all" title="删除"><svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"/></svg></button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <div class="mt-6 flex items-center justify-end gap-6 text-sm text-slate-400">
        <span>共 {{ total }} 条</span>
        <div class="flex items-center gap-1">
          <button @click="changePage(currentPage - 1)" :disabled="currentPage === 1" class="w-8 h-8 flex items-center justify-center rounded hover:bg-slate-100 disabled:opacity-30"><svg class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20"><path d="M12.707 5.293a1 1 0 010 1.414L9.414 10l3.293 3.293a1 1 0 01-1.414 1.414l-4-4a1 1 0 010-1.414l4-4a1 1 0 011.414 0z"/></svg></button>
          <button v-for="p in totalPages" :key="p" @click="changePage(p)" :class="p === currentPage ? 'bg-[#1d70f5] text-white' : 'hover:bg-slate-100'" class="w-8 h-8 rounded flex items-center justify-center transition-colors">{{ p }}</button>
          <button @click="changePage(currentPage + 1)" :disabled="currentPage === totalPages" class="w-8 h-8 flex items-center justify-center rounded hover:bg-slate-100 disabled:opacity-30"><svg class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20"><path d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z"/></svg></button>
        </div>
        <div class="flex items-center gap-2">
           <select v-model="pageSize" @change="handleSearch" class="bg-white border border-slate-200 rounded px-2 py-1 outline-none">
             <option :value="10">10条/页</option>
             <option :value="20">20条/页</option>
           </select>
        </div>
      </div>
    </div>

    <teleport to="body">
      <Transition name="toast">
        <div v-if="toast.show"
             class="fixed top-4 left-1/2 -translate-x-1/2 z-[99999] px-8 py-3.5 rounded-2xl shadow-2xl border backdrop-blur-md transition-all font-bold text-sm tracking-wide"
             :class="toast.type === 'success' ? 'bg-emerald-500/90 border-emerald-400 text-white' : 'bg-red-500/90 border-red-400 text-white'">
          {{ toast.message }}
        </div>
      </Transition>
    </teleport>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { getDocumentList, deleteDocument } from '@/api/review'

const router = useRouter()
const tableData = ref([])
const total = ref(0)
const loading = ref(false)
const currentPage = ref(1)
const pageSize = ref(12)

const filters = reactive({ name: '', start: '', end: '' })
const toast = reactive({ show: false, message: '', type: 'success' })

// --- 核心逻辑 ---

const showToast = (msg, type = 'success') => {
  toast.message = msg; toast.type = type; toast.show = true
  setTimeout(() => toast.show = false, 3000)
}

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
    tableData.value = res.items
    total.value = res.total
  } catch (error) {
    showToast('无法获取数据，请检查服务状态', 'error')
  } finally {
    loading.value = false
  }
}

// ✅ 补全：新建跳转逻辑，带控制台调试
const goToCreate = () => {
  console.log('尝试跳转到 [review-create]...');
  router.push({ name: 'review-create' }).catch(err => {
    // 如果这里打印了错误，说明 FileUpload.vue 组件加载失败了
    console.error('路由导航异常:', err);
    showToast('组件加载失败，请检查文件路径', 'error');
  });
}

const handleEdit = (id) => {
  router.push({ name: 'review-detail', params: { id } })
}

const handleDelete = async (id) => {
  if (!confirm('确定彻底删除该公文及其物理文件吗？')) return

  loading.value = true
  try {
    await deleteDocument(id)
    showToast('记录及文件已同步清理')
    if (tableData.value.length === 1 && currentPage.value > 1) {
      currentPage.value--
    }
    fetchList()
  } catch (error) {
    showToast('删除失败', 'error')
  } finally {
    loading.value = false
  }
}

const handleSearch = () => { currentPage.value = 1; fetchList() }
const resetFilters = () => { Object.assign(filters, { name: '', start: '', end: '' }); handleSearch() }
const changePage = (p) => { currentPage.value = p; fetchList() }
const totalPages = computed(() => Math.ceil(total.value / pageSize.value) || 1)

const getStatusClass = (status) => {
  return status === '已校审' ? 'bg-emerald-50 text-emerald-600' : 'bg-orange-50 text-orange-600'
}

onMounted(() => fetchList())
</script>

<style scoped>
.upload-card {
  width: 100%; height: 100%; max-width: 1840px; max-height: 860px;
  background: linear-gradient(181deg, #ffffff 0%, #ffffff 65%, #dfedff 100%);
  border: solid 2px #ffffff;
}

.toast-enter-active { animation: slide-in 0.4s cubic-bezier(0.18, 0.89, 0.32, 1.28); }
.toast-leave-active { transition: opacity 0.3s; }
.toast-leave-to { opacity: 0; }

@keyframes slide-in {
  from { opacity: 0; transform: translate(-50%, -20px); }
  to { opacity: 1; transform: translate(-50%, 0); }
}
</style>