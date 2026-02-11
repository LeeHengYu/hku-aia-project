import { useEffect, useMemo, useState } from 'react'
import Sidebar from './components/Sidebar'
import ChatView from './components/ChatView'
import Composer from './components/Composer'
import type { Chat, Message, VertexPromptExport } from './lib/types'
import {
  hydrateChatFromExport,
  loadActiveChatId,
  loadChats,
  saveActiveChatId,
  saveChats,
} from './lib/storage'

const createChat = (title = 'New chat'): Chat => {
  const now = new Date().toISOString()
  return {
    id: crypto.randomUUID(),
    title,
    createdAt: now,
    updatedAt: now,
    messages: [],
  }
}

const SAMPLE_MARKDOWN = `### Sample Markdown

Here is a quick render check:

- **Bold text**
- *Italic text*
- \`inline code\`
- [Link](https://example.com)

| Feature | Value |
| --- | --- |
| Response | Rich text |
| Tables | Supported |

\`\`\`bash
curl -X POST /api/chat
\`\`\`
`

const buildSampleChat = (): Chat => {
  const now = new Date().toISOString()
  return {
    id: crypto.randomUUID(),
    title: 'Sample markdown',
    createdAt: now,
    updatedAt: now,
    messages: [
      {
        id: crypto.randomUUID(),
        role: 'user',
        content: 'Render sample markdown',
        createdAt: now,
      },
      {
        id: crypto.randomUUID(),
        role: 'assistant',
        content: SAMPLE_MARKDOWN,
        createdAt: now,
      },
    ],
  }
}

const titleFromMessage = (value: string) => {
  const trimmed = value.trim()
  if (!trimmed) return 'New chat'
  return trimmed.length > 44 ? `${trimmed.slice(0, 44)}…` : trimmed
}

function App() {
  const [chats, setChats] = useState<Chat[]>(() => loadChats())
  const [activeChatId, setActiveChatId] = useState<string | null>(() =>
    loadActiveChatId(),
  )
  const [input, setInput] = useState('')
  const [isLoading, setIsLoading] = useState(false)

  useEffect(() => {
    if (!activeChatId && chats.length > 0) {
      setActiveChatId(chats[0].id)
    }
  }, [activeChatId, chats])

  useEffect(() => {
    saveChats(chats)
  }, [chats])

  useEffect(() => {
    saveActiveChatId(activeChatId)
  }, [activeChatId])

  const activeChat = useMemo(
    () => chats.find((chat) => chat.id === activeChatId) ?? null,
    [chats, activeChatId],
  )

  const updateChat = (chatId: string, updater: (chat: Chat) => Chat) => {
    setChats((prev) =>
      prev.map((chat) => (chat.id === chatId ? updater(chat) : chat)),
    )
  }

  const handleNewChat = () => {
    const nextChat = createChat()
    setChats((prev) => [nextChat, ...prev])
    setActiveChatId(nextChat.id)
  }

  const handleSelectChat = (chatId: string) => {
    setActiveChatId(chatId)
  }

  const handleImport = (data: VertexPromptExport) => {
    const imported = hydrateChatFromExport(data)
    setChats((prev) => [imported, ...prev])
    setActiveChatId(imported.id)
  }

  const handleLoadSample = () => {
    const sample = buildSampleChat()
    setChats((prev) => [sample, ...prev])
    setActiveChatId(sample.id)
  }

  const handleDeleteChat = (chatId: string) => {
    setChats((prev) => {
      const remaining = prev.filter((chat) => chat.id !== chatId)
      if (activeChatId === chatId) {
        setActiveChatId(remaining.length > 0 ? remaining[0].id : null)
      }
      return remaining
    })
  }

  const handleSend = async () => {
    if (!activeChat) return
    const trimmed = input.trim()
    if (!trimmed || isLoading) return

    const chatId = activeChat.id
    const userMessage: Message = {
      id: crypto.randomUUID(),
      role: 'user',
      content: trimmed,
      createdAt: new Date().toISOString(),
    }

    updateChat(chatId, (chat) => {
      const title =
        chat.title === 'New chat' ? titleFromMessage(trimmed) : chat.title
      return {
        ...chat,
        title,
        updatedAt: new Date().toISOString(),
        messages: [...chat.messages, userMessage],
      }
    })

    setInput('')
    setIsLoading(true)

    try {
      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          messages: [...activeChat.messages, userMessage].map((message) => ({
            role: message.role,
            content: message.content,
          })),
          systemInstruction: activeChat.systemInstruction ?? null,
          parameters: activeChat.parameters ?? null,
          model: activeChat.model ?? null,
        }),
      })

      if (!response.ok) {
        throw new Error(`Request failed with status ${response.status}`)
      }

      const data = (await response.json()) as { text?: string }
      const assistantText = data.text?.trim() || 'No response generated.'

      const assistantMessage: Message = {
        id: crypto.randomUUID(),
        role: 'assistant',
        content: assistantText,
        createdAt: new Date().toISOString(),
      }

      updateChat(chatId, (chat) => ({
        ...chat,
        updatedAt: new Date().toISOString(),
        messages: [...chat.messages, assistantMessage],
      }))
    } catch (error) {
      const assistantMessage: Message = {
        id: crypto.randomUUID(),
        role: 'assistant',
        content:
          error instanceof Error
            ? `Error: ${error.message}`
            : 'Error: Unable to reach the backend.',
        createdAt: new Date().toISOString(),
      }

      updateChat(chatId, (chat) => ({
        ...chat,
        updatedAt: new Date().toISOString(),
        messages: [...chat.messages, assistantMessage],
      }))
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="app">
      <Sidebar
        chats={chats}
        activeChatId={activeChatId}
        onSelectChat={handleSelectChat}
        onNewChat={handleNewChat}
        onImport={handleImport}
        onLoadSample={handleLoadSample}
        onDeleteChat={handleDeleteChat}
      />
      <main className="main">
        <div className="main-header">
          <div>
            <div className="main-title">Gemini</div>
            <div className="main-subtitle">
              Grounded responses with clean markdown rendering.
            </div>
          </div>
          {activeChat?.systemInstruction ? (
            <div className="system-indicator">Prompt loaded</div>
          ) : null}
        </div>
        <ChatView messages={activeChat?.messages ?? []} isLoading={isLoading} />
        <Composer
          value={input}
          onChange={setInput}
          onSend={handleSend}
          disabled={!activeChat || isLoading}
        />
      </main>
    </div>
  )
}

export default App
