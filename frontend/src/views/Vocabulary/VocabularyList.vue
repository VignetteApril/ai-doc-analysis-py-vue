<template>
  <div class="h-full w-full flex items-center justify-center p-6 md:p-10 font-sans">
    <div class="upload-card rounded-[40px] p-8 flex flex-col relative shadow-sm overflow-hidden">

      <!-- 顶部工具栏 -->
      <div class="flex items-center justify-between mb-8">
        <div class="flex items-center gap-6">
          <div class="flex items-center gap-3">
            <span class="text-sm text-slate-500">原词/替换词</span>
            <input
              v-model="filters.keyword"
              type="text"
              placeholder="请输入"
              class="px-4 py-2 bg-slate-50 border border-slate-200 rounded-lg text-sm w-48 focus:ring-2 focus:ring-blue-400 focus:outline-none"
              @keyup.enter="handleSearch"
            >
          </div>
          <div class="flex items-center gap-3 text-sm">
            <span class="text-slate-500">创建时间</span>
            <div class="flex items-center gap-2">
              <input v-model="filters.start" type="date" class="px-3 py-2 bg-slate-50 border border-slate-200 rounded-lg text-sm">
              <span class="text-slate-300">至</span>
              <input v-model="filters.end" type="date" class="px-3 py-2 bg-slate-50 border border-slate-200 rounded-lg text-sm">
            </div>
          </div>
          <div class="flex items-center gap-2 ml-2">
            <button @click="resetFilters" class="px-5 py-2 border border-slate-200 text-slate-600 rounded-lg text-sm hover:bg-slate-50 transition-colors">重置</button>
            <button @click="handleSearch" class="px-5 py-2 bg-[#1d70f5] text-white rounded-lg text-sm hover:bg-blue-700 shadow-md transition-all">查询</button>
          </div>
        </div>

        <button
          @click="openModal()"
          class="flex items-center gap-2 px-6 py-2.5 bg-[#1d70f5] text-white rounded-xl text-sm font-bold hover:bg-blue-700 shadow-lg transition-all active:scale-95"
        >
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path d="M12 4v16m8-8H4" stroke-linecap="round" stroke-linejoin="round" stroke-width="3"/></svg>
          新增替换词
        </button>
      </div>

      <!-- 表格 -->
      <div class="flex-1 overflow-auto rounded-xl border border-slate-50 relative">
        <div v-if="loading" class="absolute inset-0 bg-white/50 backdrop-blur-[2px] z-20 flex items-center justify-center">
          <div class="w-10 h-10 border-4 border-blue-600 border-t-transparent rounded-full animate-spin"></div>
        </div>

        <table class="w-full text-left">
          <thead class="sticky top-0 z-10">
            <tr class="bg-[#f8faff] text-slate-500 text-sm border-b border-slate-100">
              <th class="px-6 py-4 font-medium w-20">序号</th>
              <th class="px-6 py-4 font-medium">原词</th>
              <th class="px-6 py-4 font-medium">
                <div class="flex items-center gap-1 cursor-pointer select-none" @click="toggleSort">
                  创建时间
                  <svg class="w-3.5 h-3.5 text-slate-400 transition-transform" :class="sortDesc ? '' : 'rotate-180'" fill="currentColor" viewBox="0 0 20 20">
                    <path d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z"/>
                  </svg>
                </div>
              </th>
              <th class="px-6 py-4 font-medium">替换词</th>
              <th class="px-6 py-4 font-medium text-center w-24">权重</th>
              <th class="px-6 py-4 font-medium text-center w-28">操作</th>
            </tr>
          </thead>
          <tbody class="text-sm divide-y divide-slate-50">
            <tr v-if="tableData.length === 0 && !loading">
              <td colspan="6" class="px-6 py-20 text-center text-slate-400 font-medium tracking-wide">暂无词库记录，点击右上角「新增替换词」开始添加</td>
            </tr>
            <tr v-for="(item, index) in tableData" :key="item.id" class="hover:bg-slate-50/50 transition-colors">
              <td class="px-6 py-4 text-slate-400">{{ (currentPage - 1) * pageSize + index + 1 }}</td>
              <td class="px-6 py-4 font-medium text-slate-700">
                <span class="inline-flex items-center px-2.5 py-0.5 rounded-md bg-orange-50 text-orange-700 border border-orange-100 text-xs font-mono">{{ item.original_word }}</span>
              </td>
              <td class="px-6 py-4 text-slate-400">{{ item.created_at }}</td>
              <td class="px-6 py-4 text-slate-700">
                <span class="inline-flex items-center px-2.5 py-0.5 rounded-md bg-emerald-50 text-emerald-700 border border-emerald-100 text-xs font-mono">{{ item.replacement_word }}</span>
              </td>
              <td class="px-6 py-4 text-center">
                <span class="inline-block w-8 h-8 leading-8 text-center rounded-full text-xs font-bold"
                  :class="item.weight >= 8 ? 'bg-red-100 text-red-600' : item.weight >= 5 ? 'bg-orange-100 text-orange-600' : 'bg-slate-100 text-slate-500'">
                  {{ item.weight }}
                </span>
              </td>
              <td class="px-6 py-4">
                <div class="flex items-center justify-center gap-4 text-[#1d70f5]">
                  <button @click="openModal(item)" class="hover:scale-110 transition-transform" title="编辑">
                    <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"/></svg>
                  </button>
                  <button @click="handleDelete(item.id)" class="hover:text-red-500 hover:scale-110 transition-all" title="删除">
                    <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"/></svg>
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- 分页 -->
      <div class="mt-6 flex items-center justify-end gap-6 text-sm text-slate-400">
        <span>共 {{ total }} 条</span>
        <div class="flex items-center gap-1">
          <button @click="changePage(currentPage - 1)" :disabled="currentPage === 1" class="w-8 h-8 flex items-center justify-center rounded hover:bg-slate-100 disabled:opacity-30">
            <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20"><path d="M12.707 5.293a1 1 0 010 1.414L9.414 10l3.293 3.293a1 1 0 01-1.414 1.414l-4-4a1 1 0 010-1.414l4-4a1 1 0 011.414 0z"/></svg>
          </button>
          <button
            v-for="p in totalPages" :key="p"
            @click="changePage(p)"
            :class="p === currentPage ? 'bg-[#1d70f5] text-white' : 'hover:bg-slate-100'"
            class="w-8 h-8 rounded flex items-center justify-center transition-colors"
          >{{ p }}</button>
          <button @click="changePage(currentPage + 1)" :disabled="currentPage === totalPages" class="w-8 h-8 flex items-center justify-center rounded hover:bg-slate-100 disabled:opacity-30">
            <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20"><path d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z"/></svg>
          </button>
        </div>
        <select v-model="pageSize" @change="handleSearch" class="bg-white border border-slate-200 rounded px-2 py-1 outline-none">
          <option :value="10">10条/页</option>
          <option :value="12">12条/页</option>
          <option :value="20">20条/页</option>
        </select>
      </div>
    </div>

    <!-- 新增/编辑 Modal -->
    <Transition name="modal">
      <div v-if="modal.show" class="fixed inset-0 z-50 flex items-center justify-center">
        <div class="absolute inset-0 bg-black/20 backdrop-blur-sm" @click="closeModal"></div>
        <div class="relative bg-white rounded-3xl shadow-2xl w-[480px] p-8 z-10">
          <h3 class="text-lg font-bold text-slate-800 mb-6">{{ modal.isEdit ? '编辑替换词' : '新增替换词' }}</h3>

          <div class="space-y-5">
            <div>
              <label class="block text-sm font-medium text-slate-600 mb-1.5">原词 <span class="text-red-500">*</span></label>
              <input
                v-model="modal.form.original_word"
                type="text"
                placeholder="输入需要被替换的词"
                class="w-full px-4 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-sm focus:ring-2 focus:ring-blue-400 focus:outline-none"
              >
            </div>
            <div>
              <label class="block text-sm font-medium text-slate-600 mb-1.5">替换词 <span class="text-red-500">*</span></label>
              <input
                v-model="modal.form.replacement_word"
                type="text"
                placeholder="输入替换后的正确词"
                class="w-full px-4 py-2.5 bg-slate-50 border border-slate-200 rounded-xl text-sm focus:ring-2 focus:ring-blue-400 focus:outline-none"
              >
            </div>
            <div>
              <label class="block text-sm font-medium text-slate-600 mb-1.5">
                权重
                <span class="ml-2 text-xs text-slate-400 font-normal">（1-10，越大越优先显示）</span>
              </label>
              <div class="flex items-center gap-3">
                <input
                  v-model.number="modal.form.weight"
                  type="range"
                  min="1"
                  max="10"
                  class="flex-1 accent-[#1d70f5]"
                >
                <span class="w-8 text-center text-sm font-bold text-[#1d70f5]">{{ modal.form.weight }}</span>
              </div>
            </div>
          </div>

          <div class="flex items-center justify-end gap-3 mt-8">
            <button @click="closeModal" class="px-6 py-2.5 border border-slate-200 text-slate-600 rounded-xl text-sm hover:bg-slate-50 transition-colors">取消</button>
            <button
              @click="handleSubmit"
              :disabled="modal.saving"
              class="px-6 py-2.5 bg-[#1d70f5] text-white rounded-xl text-sm font-bold hover:bg-blue-700 transition-all disabled:opacity-50 flex items-center gap-2"
            >
              <span v-if="modal.saving" class="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></span>
              {{ modal.isEdit ? '保存修改' : '确认添加' }}
            </button>
          </div>
        </div>
      </div>
    </Transition>

    <!-- Toast 通知 -->
    <teleport to="body">
      <Transition name="toast">
        <div v-if="toast.show"
             class="fixed top-4 left-1/2 -translate-x-1/2 z-[99999] px-8 py-3.5 rounded-2xl shadow-2xl border backdrop-blur-md font-bold text-sm tracking-wide"
             :class="toast.type === 'success' ? 'bg-emerald-500/90 border-emerald-400 text-white' : 'bg-red-500/90 border-red-400 text-white'">
          {{ toast.message }}
        </div>
      </Transition>
    </teleport>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { getVocabularyList, createVocabulary, updateVocabulary, deleteVocabulary } from '@/api/vocabulary'

const tableData = ref([])
const total = ref(0)
const loading = ref(false)
const currentPage = ref(1)
const pageSize = ref(12)
const sortDesc = ref(true)

const filters = reactive({ keyword: '', start: '', end: '' })
const toast = reactive({ show: false, message: '', type: 'success' })
const modal = reactive({
  show: false,
  isEdit: false,
  saving: false,
  editId: null,
  form: { original_word: '', replacement_word: '', weight: 5 }
})

// --- 工具函数 ---
const showToast = (msg, type = 'success') => {
  toast.message = msg; toast.type = type; toast.show = true
  setTimeout(() => toast.show = false, 3000)
}

// --- 数据加载 ---
const fetchList = async () => {
  loading.value = true
  try {
    const res = await getVocabularyList({
      page: currentPage.value,
      size: pageSize.value,
      keyword: filters.keyword,
      start_date: filters.start,
      end_date: filters.end
    })
    tableData.value = res.items
    total.value = res.total
  } catch {
    showToast('获取词库失败，请检查服务状态', 'error')
  } finally {
    loading.value = false
  }
}

// --- 搜索 / 分页 ---
const handleSearch = () => { currentPage.value = 1; fetchList() }
const resetFilters = () => { Object.assign(filters, { keyword: '', start: '', end: '' }); handleSearch() }
const changePage = (p) => { if (p < 1 || p > totalPages.value) return; currentPage.value = p; fetchList() }
const totalPages = computed(() => Math.ceil(total.value / pageSize.value) || 1)
const toggleSort = () => { sortDesc.value = !sortDesc.value; fetchList() }

// --- 新增/编辑 Modal ---
const openModal = (item = null) => {
  modal.isEdit = !!item
  modal.editId = item?.id ?? null
  modal.form.original_word = item?.original_word ?? ''
  modal.form.replacement_word = item?.replacement_word ?? ''
  modal.form.weight = item?.weight ?? 5
  modal.show = true
}
const closeModal = () => { modal.show = false }

const handleSubmit = async () => {
  if (!modal.form.original_word.trim() || !modal.form.replacement_word.trim()) {
    showToast('原词和替换词不能为空', 'error')
    return
  }
  modal.saving = true
  try {
    if (modal.isEdit) {
      await updateVocabulary(modal.editId, modal.form)
      showToast('修改成功')
    } else {
      await createVocabulary(modal.form)
      showToast('添加成功')
    }
    closeModal()
    fetchList()
  } catch (err) {
    const msg = err?.response?.data?.detail || (modal.isEdit ? '修改失败' : '添加失败')
    showToast(msg, 'error')
  } finally {
    modal.saving = false
  }
}

// --- 删除 ---
const handleDelete = async (id) => {
  if (!confirm('确定删除该词条吗？')) return
  loading.value = true
  try {
    await deleteVocabulary(id)
    showToast('删除成功')
    if (tableData.value.length === 1 && currentPage.value > 1) currentPage.value--
    fetchList()
  } catch {
    showToast('删除失败', 'error')
  } finally {
    loading.value = false
  }
}

onMounted(() => fetchList())
</script>

<style scoped>
.upload-card {
  width: 100%; height: 100%; max-width: 1840px; max-height: 860px;
  background: linear-gradient(181deg, #ffffff 0%, #ffffff 65%, #dfedff 100%);
  border: solid 2px #ffffff;
}

/* Toast */
.toast-enter-active { animation: slide-in 0.4s cubic-bezier(0.18, 0.89, 0.32, 1.28); }
.toast-leave-active { transition: opacity 0.3s; }
.toast-leave-to { opacity: 0; }
@keyframes slide-in {
  from { opacity: 0; transform: translate(-50%, -20px); }
  to   { opacity: 1; transform: translate(-50%, 0); }
}

/* Modal */
.modal-enter-active, .modal-leave-active { transition: opacity 0.25s ease; }
.modal-enter-from, .modal-leave-to { opacity: 0; }
.modal-enter-active .relative, .modal-leave-active .relative { transition: transform 0.25s ease; }
.modal-enter-from .relative { transform: scale(0.95) translateY(10px); }
</style>
