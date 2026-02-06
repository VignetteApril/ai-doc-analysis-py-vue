<template>
  <div class="h-full flex flex-col bg-[#f8f9fc] font-sans overflow-hidden">
    <header class="h-16 bg-white shrink-0 border-b border-slate-200 px-8 flex items-center justify-between z-50 shadow-sm">
      <div class="flex items-center gap-4">
        <button @click="$router.push('/review')" class="p-2 hover:bg-slate-100 rounded-full text-slate-400 transition-colors">
          <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path d="M15 19l-7-7 7-7" stroke-width="2" stroke-linecap="round"/></svg>
        </button>
        <div class="h-6 w-[1px] bg-slate-200"></div>
        <h2 class="text-lg font-extrabold text-slate-800 tracking-tight">{{ documentName }}</h2>
      </div>
      <div class="flex gap-3">
        <button @click="handleDownload" class="px-5 py-2 border border-slate-200 text-[#1d70f5] rounded-xl text-sm font-medium hover:bg-blue-50 transition-all">导出原文</button>
        <button @click="handleSave" class="px-8 py-2 bg-[#1d70f5] text-white rounded-xl text-sm font-bold shadow-lg shadow-blue-500/30 hover:bg-blue-700 transition-all active:scale-95">
          保存修改
        </button>
      </div>
    </header>

    <div class="flex-1 flex overflow-hidden">
      <aside class="w-[420px] border-r border-slate-200 bg-white flex flex-col shadow-2xl z-10 relative">
        <div class="p-5 border-b flex justify-between items-center bg-white/50 backdrop-blur-sm sticky top-0 z-20">
          <div class="flex flex-col">
            <h3 class="font-bold text-slate-800 text-base">Agent 深度校审</h3>
            <span class="text-[10px] text-slate-400 uppercase tracking-widest">Multi-Agent Workflow</span>
          </div>
          <button @click="handleStartAI" :disabled="analyzing"
                  class="px-4 py-2 bg-[#1d70f5] text-white rounded-xl text-xs font-bold transition-all disabled:opacity-50 hover:shadow-md hover:-translate-y-0.5">
             {{ analyzing ? '校审中...' : '开始深度校对' }}
          </button>
        </div>

        <div class="flex-1 overflow-y-auto p-4 space-y-4 bg-slate-50/50 relative scroll-smooth">

          <div v-if="analyzing" class="absolute inset-0 z-50 bg-white/95 backdrop-blur-md flex flex-col p-8 animate-in fade-in duration-300">
            <div class="mt-12 flex flex-col items-center w-full">
              <div class="relative flex items-center justify-center mb-10">
                <div class="w-20 h-20 border-4 border-slate-100 rounded-full"></div>
                <div class="absolute w-20 h-20 border-4 border-[#1d70f5] border-t-transparent rounded-full animate-spin"></div>
                <span class="absolute text-xs font-black text-[#1d70f5]">{{ progressPercent }}%</span>
              </div>

              <h3 class="text-lg font-bold text-slate-800 mb-2">泰山 Agent 正在思考</h3>
              <p class="text-[11px] text-[#1d70f5] font-mono mb-12 h-5 text-center px-4 w-full truncate">{{ currentStatusMsg }}</p>

              <div class="w-full max-w-[260px] space-y-5">
                <div v-for="step in agentSteps" :key="step.id" class="flex items-center gap-4 group">
                  <div class="w-7 h-7 rounded-full flex items-center justify-center transition-all duration-500 shadow-sm"
                       :class="{
                         'bg-emerald-500 shadow-emerald-200': step.status === 'done',
                         'bg-[#1d70f5] shadow-blue-200 animate-pulse': step.status === 'active',
                         'bg-slate-200': step.status === 'wait'
                       }">
                    <svg v-if="step.status === 'done'" class="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path d="M5 13l4 4L19 7" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/></svg>
                    <div v-else-if="step.status === 'active'" class="w-2 h-2 bg-white rounded-full"></div>
                  </div>

                  <div class="flex flex-col">
                    <span class="text-sm font-bold transition-colors duration-300"
                          :class="step.status === 'wait' ? 'text-slate-400' : 'text-slate-800'">
                      {{ step.label }}
                    </span>
                    <span v-if="step.status === 'active'" class="text-[10px] text-[#1d70f5] animate-pulse">正在处理...</span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div v-if="suggestions.length === 0 && !analyzing" class="h-full flex flex-col items-center justify-center text-slate-300 opacity-60 min-h-[400px]">
            <svg class="w-20 h-20 mb-4 text-slate-200" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" stroke-width="1.5"/></svg>
            <p class="text-sm">点击上方按钮开启 AI 智能校审</p>
          </div>

          <div v-for="(sug, idx) in suggestions" :key="sug.id"
               class="suggestion-card bg-white rounded-2xl p-5 border-l-4 shadow-sm hover:shadow-md transition-all relative overflow-hidden group"
               :class="{
                 'border-rose-500': !sug.content && !sug.handled,
                 'border-[#1d70f5]': sug.content && !sug.handled,
                 'opacity-60 grayscale border-slate-300': sug.handled
               }">

            <div v-if="sug.handled" class="absolute inset-0 bg-slate-50/80 flex items-center justify-center z-20 backdrop-blur-[1px]">
               <div class="bg-slate-800 text-white text-xs px-3 py-1.5 rounded-full font-bold shadow-lg flex items-center gap-2">
                 <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path d="M5 13l4 4L19 7" stroke-width="3" stroke-linecap="round"/></svg>
                 已完成
               </div>
            </div>

            <div class="flex justify-between items-center mb-3">
              <span class="text-[9px] font-mono bg-slate-100 text-slate-500 px-2 py-0.5 rounded uppercase tracking-wider">{{ sug.type }}</span>
              <span v-if="!sug.content" class="text-[10px] text-rose-500 font-bold bg-rose-50 px-2 py-0.5 rounded">建议删除</span>
            </div>

            <div class="space-y-3 mb-4">
              <div class="text-xs text-slate-400 line-through leading-relaxed font-mono bg-slate-50 p-1.5 rounded decoration-slate-300">
                {{ sug.original }}
              </div>
              <div class="text-sm font-bold flex items-start gap-2">
                <span class="shrink-0 mt-0.5 text-slate-300">➔</span>
                <span :class="!sug.content ? 'text-rose-500' : 'text-[#1d70f5]'">{{ sug.content || '删除此段内容' }}</span>
              </div>
              <div class="mt-2 bg-blue-50/50 p-2.5 rounded-lg border border-blue-100/50">
                <p class="text-[11px] text-slate-600 leading-relaxed flex gap-1.5">
                  <span class="shrink-0 text-blue-400">💡</span>
                  {{ sug.message }}
                </p>
              </div>
            </div>

            <div class="flex gap-2 pt-2 border-t border-slate-50">
              <button @click="locateById(sug.id)" class="flex-1 py-2 border border-slate-200 text-slate-600 text-xs rounded-lg hover:bg-slate-50 hover:border-slate-300 transition-colors font-medium">
                定位
              </button>
              <button @click="replaceById(idx)" class="flex-1 py-2 text-white text-xs rounded-lg shadow-md shadow-blue-500/20 font-bold hover:brightness-110 active:scale-95 transition-all"
                :class="!sug.content ? 'bg-rose-500' : 'bg-[#1d70f5]'">
                {{ !sug.content ? '确认删除' : '确认修改' }}
              </button>
            </div>
          </div>
        </div>
      </aside>

      <main class="flex-1 bg-slate-100/50 flex flex-col relative">
        <Toolbar class="border-b bg-white px-4 shrink-0" :editor="editorRef" mode="default" />
        <div class="flex-1 overflow-y-auto p-12 flex justify-center">
          <div class="w-full max-w-4xl bg-white shadow-2xl min-h-[1000px] rounded-sm editor-paper">
            <Editor v-model="valueHtml" :defaultConfig="editorConfig" mode="default" style="height: auto; min-height: 1000px;" @onCreated="handleCreated" />
          </div>
        </div>
        <div v-if="loading" class="absolute inset-0 bg-white/90 z-[100] flex items-center justify-center">
           <div class="w-10 h-10 border-4 border-[#1d70f5] border-t-transparent rounded-full animate-spin"></div>
        </div>
      </main>
    </div>

    <Transition name="toast">
      <div v-if="toast.show" class="fixed top-24 left-1/2 -translate-x-1/2 z-[100] px-6 py-3 rounded-full shadow-2xl border text-white font-bold text-sm flex items-center gap-2"
           :class="toast.type === 'success' ? 'bg-slate-800 border-slate-700' : 'bg-rose-500 border-rose-600'">
        <span v-if="toast.type === 'success'">🎉</span>
        <span v-else>⚠️</span>
        {{ toast.message }}
      </div>
    </Transition>
  </div>
</template>

<script setup>
import '@wangeditor/editor/dist/css/style.css'
import { shallowRef, ref, reactive, onMounted, onBeforeUnmount } from 'vue'
import { Editor, Toolbar } from '@wangeditor/editor-for-vue'
import { useRoute } from 'vue-router'
import { getDocumentDetail, saveDocumentContent, downloadDocumentFile } from '@/api/review'

const route = useRoute()
const editorRef = shallowRef()
const valueHtml = ref('')
const suggestions = ref([])
const analyzing = ref(false)
const loading = ref(true)

// --- 🌟 关键：Agent 步骤定义 ---
// 这会直接映射到左侧的遮罩层上
const agentSteps = ref([
  { id: 'preprocess', label: '文本预处理与清洗', status: 'wait' },
  { id: 'scan', label: 'Scanner: 全文扫描错误', status: 'wait' },
  { id: 'review', label: 'Reviewer: 专家逻辑复核', status: 'wait' },
  { id: 'finalize', label: 'Finalizer: 生成唯一锚点', status: 'wait' }
])
const currentStatusMsg = ref('')
const progressPercent = ref(0)
const editorConfig = { placeholder: '文档加载中...', autoFocus: false }

// --- 🚀 核心逻辑 1: 注入后端生成的 ID ---

const injectBackendMarkers = (originalHtml, items) => {
  // 按位置倒序，防止坐标偏移
  const sorted = [...items].sort((a, b) => b.start - a.start);

  let newHtml = originalHtml;

  sorted.forEach(item => {
    // 只有坐标有效才注入
    if (item.start !== undefined && item.start !== -1) {
      const before = newHtml.substring(0, item.start);
      const target = newHtml.substring(item.start, item.end);
      const after = newHtml.substring(item.end);

      // 🟢 注入 ID：后端传来的 item.id 是 "issue-xxxxx"
      // 添加 class="ai-highlight" 用于样式
      const marker = `<span id="${item.id}" class="ai-highlight" style="background:#fef9c3; border-bottom:2px solid #eab308; cursor:pointer; transition:all 0.3s;" title="点击左侧建议定位">${target}</span>`;

      newHtml = before + marker + after;
    }
  });

  return newHtml;
}

// --- 🚀 核心逻辑 2: 基于 DOM ID 的查找与替换 ---

const locateById = (id) => {
  if (!editorRef.value) return;
  const el = editorRef.value.getEditableContainer().querySelector(`#${id}`);

  if (el) {
    el.scrollIntoView({ behavior: 'smooth', block: 'center' });
    // 高亮动画
    el.style.backgroundColor = '#ffd700'; // 瞬间变深黄
    el.style.transform = 'scale(1.1)';
    setTimeout(() => {
        el.style.backgroundColor = '#fef9c3'; // 恢复浅黄
        el.style.transform = 'scale(1)';
    }, 600);
  } else {
    showToast('该位置内容已被移除或修改', 'error');
  }
}

const replaceById = (idx) => {
  const item = suggestions.value[idx];
  if (!editorRef.value || item.handled) return;

  const el = editorRef.value.getEditableContainer().querySelector(`#${item.id}`);

  if (el) {
    if (!item.content) {
      // 删除：移除 DOM 节点
      el.remove();
    } else {
      // 修改：替换为新样式节点
      const newSpan = document.createElement('span');
      newSpan.style.color = '#1d70f5';
      newSpan.style.fontWeight = 'bold';
      newSpan.style.backgroundColor = '#eff6ff';
      newSpan.innerText = item.content;
      el.replaceWith(newSpan);
    }

    suggestions.value[idx].handled = true;
    showToast(item.content ? '修改已应用' : '内容已移除');
    valueHtml.value = editorRef.value.getHtml(); // 同步
  } else {
    showToast('锚点丢失，建议重新分析', 'error');
    suggestions.value[idx].handled = true;
  }
}

// --- 🌟 业务与 SSE 流式逻辑 ---

const handleStartAI = async () => {
  if(analyzing.value) return;
  analyzing.value = true;
  suggestions.value = [];
  agentSteps.value.forEach(s => s.status = 'wait');
  progressPercent.value = 0;

  try {
    const rawHtml = editorRef.value.getHtml();
    // 清洗 URL
    const baseUrl = (import.meta.env.VITE_API_BASE_URL || '').replace(/\/+$/, '').replace(/\/api\/v1$/, '');
    const res = await fetch(`${baseUrl}/api/v1/review/${route.params.id}/analyze`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${localStorage.getItem('token')}` },
      body: JSON.stringify({ content: rawHtml })
    });

    const reader = res.body.getReader();
    const decoder = new TextDecoder();
    let finalResults = [];

    while (true) {
      const { value, done } = await reader.read();
      if (done) break;
      const lines = decoder.decode(value).split('\n');
      for (const line of lines) {
        if (!line.startsWith('data: ')) continue;
        const payload = JSON.parse(line.slice(6));

        if (payload.step === 'complete') {
          finalResults = payload.results || [];
          if (finalResults.length > 0) {
            // 任务完成，注入 ID
            const taggedHtml = injectBackendMarkers(rawHtml, finalResults);
            editorRef.value.setHtml(taggedHtml);
            suggestions.value = finalResults.map(s => ({...s, handled: false}));
          }
          progressPercent.value = 100;
        } else if (payload.step !== 'error') {
          // 🌟 实时更新左侧步骤条状态
          currentStatusMsg.value = payload.desc;
          const idx = agentSteps.value.findIndex(s => s.id === payload.step);
          if (idx !== -1) {
            agentSteps.value[idx].status = 'done'; // 标记该步骤完成
            progressPercent.value = (idx + 1) * 25;
            // 激活下一步
            if (agentSteps.value[idx+1]) agentSteps.value[idx+1].status = 'active';
          }
        }
      }
    }
  } catch (e) {
    showToast('校审服务中断', 'error');
  } finally {
    // 延迟关闭遮罩，让用户看清 100%
    setTimeout(() => { analyzing.value = false }, 800)
  }
}

const handleSave = async () => {
  let html = editorRef.value.getHtml();
  // 保存前去除所有 ID 锚点标签
  const cleanRegex = /<span id="issue-[a-z0-9]+"[^>]*>([\s\S]*?)<\/span>/g;
  const cleanHtml = html.replace(cleanRegex, '$1');
  await saveDocumentContent(route.params.id, cleanHtml);
  showToast('文档保存成功');
}

// ... 基础代码 ...
const handleCreated = (editor) => { editorRef.value = editor; if(remoteHtml) editor.setHtml(remoteHtml); }
const handleDownload = async () => {
  const blob = await downloadDocumentFile(route.params.id);
  const a = document.createElement('a'); a.href = window.URL.createObjectURL(new Blob([blob]));
  a.download = `校核结果_${documentName.value}.docx`; a.click();
}
let remoteHtml = '';
const documentName = ref('');
const fetchBasicDetail = async () => {
  const res = await getDocumentDetail(route.params.id);
  documentName.value = res.name;
  remoteHtml = res.content_html || res.content || '';
  if(editorRef.value) editorRef.value.setHtml(remoteHtml);
  valueHtml.value = remoteHtml;
  loading.value = false;
}

const toast = reactive({ show: false, message: '', type: 'success' })
const showToast = (msg, type='success') => { toast.message = msg; toast.type = type; toast.show = true; setTimeout(()=>toast.show=false, 3000) }

onMounted(() => fetchBasicDetail())
onBeforeUnmount(() => { if (editorRef.value) editorRef.value.destroy() })
</script>

<style scoped>
/* 悬停高亮增强 */
:deep(.ai-highlight:hover) { filter: brightness(0.92); }
.suggestion-card { will-change: transform; }
</style>