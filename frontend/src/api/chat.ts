import { fetchEventSource } from '@microsoft/fetch-event-source'

export interface Source {
  index: number
  source: string
  snippet: string
}

export interface ChatHandlers {
  onSources?: (sources: Source[]) => void
  onToken: (text: string) => void
  onDone?: () => void
  onError?: (message: string) => void
}

/**
 * 以 SSE 方式调用 /api/chat：
 * sources 事件（引用来源）-> 多个 token 事件（增量文本）-> done / error
 */
export async function streamChat(
  question: string,
  handlers: ChatHandlers,
  signal?: AbortSignal,
): Promise<void> {
  await fetchEventSource('/api/chat', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ question }),
    signal,
    openWhenHidden: true,
    onmessage(ev) {
      const data = ev.data ? JSON.parse(ev.data) : {}
      switch (ev.event) {
        case 'sources':
          handlers.onSources?.(data.sources ?? [])
          break
        case 'token':
          if (data.content) handlers.onToken(data.content)
          break
        case 'done':
          handlers.onDone?.()
          break
        case 'error':
          handlers.onError?.(data.message ?? '未知错误')
          break
      }
    },
    onerror(err) {
      handlers.onError?.(err instanceof Error ? err.message : String(err))
      throw err // 抛出后停止自动重连
    },
  })
}
