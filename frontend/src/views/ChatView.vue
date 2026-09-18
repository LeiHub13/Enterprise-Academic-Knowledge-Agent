<script setup lang="ts">
import { nextTick, ref } from 'vue'
import { streamChat, type Source } from '../api/chat'
import SourceCard from '../components/SourceCard.vue'

interface Message {
  role: 'user' | 'assistant'
  content: string
  sources?: Source[]
  isError?: boolean
}

const messages = ref<Message[]>([
  {
    role: 'assistant',
    content: '你好，我是知识库问答助手。先到「知识库管理」上传文档，然后就可以向我提问了。',
  },
])
const question = ref('')
const loading = ref(false)
const scrollEl = ref<HTMLElement>()
let controller: AbortController | null = null

async function scrollToBottom() {
  await nextTick()
  const el = scrollEl.value
  if (el) el.scrollTop = el.scrollHeight
}

async function send() {
  const q = question.value.trim()
  if (!q || loading.value) return

  question.value = ''
  messages.value.push({ role: 'user', content: q })
  const ai: Message = { role: 'assistant', content: '' }
  messages.value.push(ai)
  loading.value = true
  controller = new AbortController()
  await scrollToBottom()

  try {
    await streamChat(
      q,
      {
        onSources: (sources) => {
          ai.sources = sources
        },
        onToken: (text) => {
          ai.content += text
          scrollToBottom()
        },
        onDone: () => {
          loading.value = false
        },
        onError: (msg) => {
          ai.content += `\n\n[出错] ${msg}`
          ai.isError = true
          loading.value = false
        },
      },
      controller.signal,
    )
  } finally {
    loading.value = false
  }
}

function stop() {
  controller?.abort()
  loading.value = false
}
</script>

<template>
  <div class="chat">
    <div ref="scrollEl" class="messages">
      <div
        v-for="(m, i) in messages"
        :key="i"
        class="row"
        :class="m.role === 'user' ? 'row-user' : 'row-ai'"
      >
        <div class="bubble" :class="{ user: m.role === 'user', error: m.isError }">
          <div class="content">{{ m.content }}<span v-if="loading && i === messages.length - 1 && !m.content" class="cursor">▍</span></div>
          <SourceCard v-if="m.sources" :sources="m.sources" />
        </div>
      </div>
    </div>

    <div class="composer">
      <el-input
        v-model="question"
        type="textarea"
        :rows="2"
        resize="none"
        placeholder="输入问题，Enter 发送，Shift+Enter 换行"
        @keydown.enter.exact.prevent="send"
      />
      <el-button v-if="!loading" type="primary" :disabled="!question.trim()" @click="send">
        发送
      </el-button>
      <el-button v-else type="danger" @click="stop">停止</el-button>
    </div>
  </div>
</template>

<style scoped>
.chat {
  height: 100vh;
  display: flex;
  flex-direction: column;
}
.messages {
  flex: 1;
  overflow-y: auto;
  padding: 24px 18%;
}
.row {
  display: flex;
  margin-bottom: 16px;
}
.row-user {
  justify-content: flex-end;
}
.bubble {
  max-width: 100%;
  background: #fff;
  border: 1px solid #e4e3dd;
  border-radius: 12px;
  padding: 10px 14px;
  font-size: 14px;
  line-height: 1.7;
  white-space: pre-wrap;
  word-break: break-word;
}
.bubble.user {
  background: #9bbbf4;
  border-color: #9bbbf4;
  color: #1a1b1c;
}
.bubble.error {
  border-color: #ea6668;
  color: #c0392b;
}
.content {
  white-space: pre-wrap;
}
.cursor {
  animation: blink 1s steps(2) infinite;
  color: #6b7280;
}
@keyframes blink {
  0% { opacity: 1; }
  50% { opacity: 0; }
}
.composer {
  border-top: 1px solid #e4e3dd;
  background: #fff;
  padding: 12px 18%;
  display: flex;
  gap: 10px;
  align-items: flex-end;
}
@media (max-width: 768px) {
  .messages,
  .composer {
    padding-left: 12px;
    padding-right: 12px;
  }
}
</style>
