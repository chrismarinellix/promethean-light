<script>
  import { chatMessages, saveFavorite } from '../stores.js';
  import { marked } from 'marked';

  // Configure marked for tables
  marked.setOptions({
    gfm: true,
    breaks: true
  });

  let inputValue = '';
  let isLoading = false;
  let savingId = null;
  let savedId = null;
  let copiedId = null;

  function renderMarkdown(text) {
    try {
      return marked(text);
    } catch (e) {
      return text;
    }
  }

  async function sendMessage() {
    if (!inputValue.trim() || isLoading) return;

    const userMessage = inputValue;
    inputValue = '';

    // Add user message
    chatMessages.update(msgs => [...msgs, {
      role: 'user',
      content: userMessage,
      timestamp: new Date().toISOString()
    }]);

    isLoading = true;

    try {
      const response = await fetch('http://127.0.0.1:8000/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: userMessage })
      });

      if (!response.ok) throw new Error('Chat failed');

      const data = await response.json();

      chatMessages.update(msgs => [...msgs, {
        role: 'assistant',
        content: data.response || data.message || 'No response',
        sources: data.sources || [],
        timestamp: new Date().toISOString()
      }]);
    } catch (e) {
      chatMessages.update(msgs => [...msgs, {
        role: 'assistant',
        content: 'Error: Could not connect to Promethean Light daemon.',
        isError: true,
        timestamp: new Date().toISOString()
      }]);
    } finally {
      isLoading = false;
    }
  }

  function handleKeydown(e) {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  }

  async function saveResponse(msgIndex) {
    const assistantMsg = $chatMessages[msgIndex];
    const userMsg = $chatMessages[msgIndex - 1];

    if (!assistantMsg || !userMsg || userMsg.role !== 'user') return;

    savingId = msgIndex;

    try {
      // Save to favorites store (shows in sidebar)
      saveFavorite(userMsg.content, [{
        content: assistantMsg.content,
        source: 'chat-response',
        timestamp: assistantMsg.timestamp
      }]);

      // Also save to database for persistence
      const conversationText = `# Query
${userMsg.content}

# Response
${assistantMsg.content}

---
Saved: ${new Date().toLocaleString()}`;

      await fetch('http://127.0.0.1:8000/add', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          text: conversationText,
          source: 'saved-chat'
        })
      });

      savedId = msgIndex;
      setTimeout(() => { if (savedId === msgIndex) savedId = null; }, 3000);
    } catch (e) {
      console.error('Failed to save:', e);
    } finally {
      savingId = null;
    }
  }

  function copyResponse(text, idx) {
    navigator.clipboard.writeText(text);
    copiedId = idx;
    setTimeout(() => { if (copiedId === idx) copiedId = null; }, 2000);
  }

  function clearHistory() {
    chatMessages.set([]);
  }
</script>

<div class="terminal">
  <div class="terminal-header">
    <div class="terminal-title">
      <span class="prompt-symbol">></span>
      <span>Ask your data anything</span>
    </div>
    {#if $chatMessages.length > 0}
      <button class="clear-btn" on:click={clearHistory} title="Clear history">
        Clear
      </button>
    {/if}
  </div>

  <div class="terminal-output">
    {#if $chatMessages.length === 0}
      <div class="welcome">
        <p class="hint">Type a question and press Enter. Examples:</p>
        <button class="example" on:click={() => inputValue = 'List my team members'}>
          > List my team members
        </button>
        <button class="example" on:click={() => inputValue = 'What projects are we working on?'}>
          > What projects are we working on?
        </button>
        <button class="example" on:click={() => inputValue = 'Show recent emails about budget'}>
          > Show recent emails about budget
        </button>
      </div>
    {:else}
      {#each $chatMessages as msg, idx}
        <div class="entry" class:error={msg.isError}>
          {#if msg.role === 'user'}
            <div class="query">
              <span class="prompt">> </span>{msg.content}
            </div>
          {:else}
            <div class="response">
              <div class="response-text">{@html renderMarkdown(msg.content)}</div>
              {#if !msg.isError}
                <div class="response-actions">
                  <button
                    class="action-btn"
                    class:success={copiedId === idx}
                    on:click={() => copyResponse(msg.content, idx)}
                  >
                    {copiedId === idx ? 'Copied!' : 'Copy'}
                  </button>
                  <button
                    class="action-btn save"
                    class:saving={savingId === idx}
                    class:success={savedId === idx}
                    on:click={() => saveResponse(idx)}
                    disabled={savingId === idx}
                  >
                    {#if savedId === idx}
                      Saved!
                    {:else if savingId === idx}
                      Saving...
                    {:else}
                      Save
                    {/if}
                  </button>
                </div>
              {/if}
            </div>
          {/if}
        </div>
      {/each}
      {#if isLoading}
        <div class="entry">
          <div class="response loading">
            <span class="cursor">_</span>
          </div>
        </div>
      {/if}
    {/if}
  </div>

  <div class="terminal-input">
    <span class="prompt">> </span>
    <input
      type="text"
      bind:value={inputValue}
      on:keydown={handleKeydown}
      placeholder="Ask a question..."
      disabled={isLoading}
    />
  </div>
</div>

<style>
  .terminal {
    display: flex;
    flex-direction: column;
    height: 100%;
    background: var(--bg-primary);
    font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
  }

  .terminal-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 12px 16px;
    background: var(--bg-secondary);
    border-bottom: 1px solid var(--border-color);
  }

  .terminal-title {
    display: flex;
    align-items: center;
    gap: 8px;
    color: var(--text-secondary);
    font-size: 13px;
  }

  .prompt-symbol {
    color: var(--accent-orange);
    font-weight: bold;
  }

  .clear-btn {
    background: transparent;
    border: 1px solid var(--border-color);
    color: var(--text-muted);
    padding: 4px 12px;
    border-radius: 4px;
    font-size: 11px;
    cursor: pointer;
    font-family: inherit;
  }

  .clear-btn:hover {
    border-color: var(--accent-red);
    color: var(--accent-red);
  }

  .terminal-output {
    flex: 1;
    overflow-y: auto;
    padding: 16px;
  }

  .welcome {
    color: var(--text-muted);
  }

  .welcome .hint {
    margin-bottom: 16px;
    font-size: 13px;
  }

  .example {
    display: block;
    background: transparent;
    border: none;
    color: var(--text-secondary);
    font-family: inherit;
    font-size: 13px;
    padding: 6px 0;
    cursor: pointer;
    text-align: left;
    width: 100%;
  }

  .example:hover {
    color: var(--accent-orange);
  }

  .entry {
    margin-bottom: 16px;
  }

  .entry.error .response-text {
    color: var(--accent-red);
  }

  .query {
    color: var(--accent-orange);
    font-size: 14px;
    margin-bottom: 8px;
  }

  .prompt {
    color: var(--accent-orange);
    font-weight: bold;
    user-select: none;
  }

  .response {
    background: var(--bg-secondary);
    border: 1px solid var(--border-color);
    border-radius: 6px;
    overflow: hidden;
  }

  .response-text {
    margin: 0;
    padding: 16px;
    font-size: 13px;
    line-height: 1.6;
    color: var(--text-primary);
    word-wrap: break-word;
    font-family: inherit;
    overflow-x: auto;
  }

  .response-text :global(p) {
    margin: 0 0 12px 0;
  }

  .response-text :global(p:last-child) {
    margin-bottom: 0;
  }

  .response-text :global(table) {
    border-collapse: collapse;
    width: 100%;
    margin: 12px 0;
    font-size: 12px;
  }

  .response-text :global(th),
  .response-text :global(td) {
    border: 1px solid var(--border-color);
    padding: 8px 12px;
    text-align: left;
  }

  .response-text :global(th) {
    background: var(--bg-tertiary);
    font-weight: 600;
    color: var(--text-primary);
  }

  .response-text :global(tr:nth-child(even)) {
    background: var(--bg-tertiary);
  }

  .response-text :global(tr:hover) {
    background: var(--accent-orange-dim);
  }

  .response-text :global(h1),
  .response-text :global(h2),
  .response-text :global(h3) {
    margin: 16px 0 8px 0;
    color: var(--text-primary);
  }

  .response-text :global(h1) { font-size: 18px; }
  .response-text :global(h2) { font-size: 16px; }
  .response-text :global(h3) { font-size: 14px; }

  .response-text :global(ul),
  .response-text :global(ol) {
    margin: 8px 0;
    padding-left: 24px;
  }

  .response-text :global(li) {
    margin: 4px 0;
  }

  .response-text :global(code) {
    background: var(--bg-tertiary);
    padding: 2px 6px;
    border-radius: 4px;
    font-family: 'Consolas', 'Monaco', monospace;
    font-size: 12px;
  }

  .response-text :global(pre) {
    background: var(--bg-tertiary);
    padding: 12px;
    border-radius: 6px;
    overflow-x: auto;
    margin: 12px 0;
  }

  .response-text :global(pre code) {
    background: none;
    padding: 0;
  }

  .response-text :global(blockquote) {
    margin: 12px 0;
    padding: 8px 16px;
    border-left: 3px solid var(--accent-orange);
    background: var(--bg-tertiary);
    color: var(--text-secondary);
    font-style: italic;
  }

  .response-text :global(blockquote p) {
    margin: 0;
  }

  .response-text :global(hr) {
    border: none;
    border-top: 1px solid var(--border-color);
    margin: 16px 0;
  }

  .response-text :global(strong) {
    color: var(--text-primary);
    font-weight: 700;
  }

  .response-text :global(em) {
    color: var(--text-secondary);
  }

  .response-text :global(a) {
    color: var(--accent-blue);
    text-decoration: none;
  }

  .response-text :global(a:hover) {
    text-decoration: underline;
  }

  .response-text :global(mark) {
    background: var(--accent-orange-dim);
    color: var(--text-primary);
    padding: 1px 4px;
    border-radius: 2px;
  }

  .response-text :global(del) {
    color: var(--text-muted);
    text-decoration: line-through;
  }

  .response-text :global(img) {
    max-width: 100%;
    border-radius: 6px;
    margin: 8px 0;
  }

  .response-actions {
    display: flex;
    gap: 8px;
    padding: 10px 16px;
    background: var(--bg-tertiary);
    border-top: 1px solid var(--border-color);
  }

  .action-btn {
    background: var(--bg-secondary);
    border: 1px solid var(--border-color);
    color: var(--text-secondary);
    padding: 6px 16px;
    border-radius: 4px;
    font-size: 12px;
    font-family: inherit;
    cursor: pointer;
    transition: all 0.2s;
  }

  .action-btn:hover:not(:disabled) {
    border-color: var(--text-muted);
    color: var(--text-primary);
  }

  .action-btn.save {
    background: var(--accent-orange);
    border-color: var(--accent-orange);
    color: white;
    font-weight: 600;
  }

  .action-btn.save:hover:not(:disabled) {
    background: #ea580c;
    border-color: #ea580c;
  }

  .action-btn.success {
    background: var(--accent-green) !important;
    border-color: var(--accent-green) !important;
    color: white !important;
  }

  .action-btn:disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }

  .loading {
    padding: 16px;
    color: var(--text-muted);
  }

  .cursor {
    animation: blink 1s step-end infinite;
  }

  @keyframes blink {
    0%, 100% { opacity: 1; }
    50% { opacity: 0; }
  }

  .terminal-input {
    display: flex;
    align-items: center;
    padding: 16px;
    background: var(--bg-secondary);
    border-top: 1px solid var(--border-color);
  }

  .terminal-input input {
    flex: 1;
    background: transparent;
    border: none;
    color: var(--text-primary);
    font-family: inherit;
    font-size: 14px;
    outline: none;
  }

  .terminal-input input::placeholder {
    color: var(--text-muted);
  }

  .terminal-input input:disabled {
    opacity: 0.5;
  }
</style>
