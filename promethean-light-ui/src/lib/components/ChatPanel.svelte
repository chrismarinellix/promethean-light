<script>
  import { chatMessages, saveFavorite, savedFolders, saveToFolder, loadSavedFolders, viewMode, daemonConnected } from '../stores.js';
  import { chat as apiChat } from '../api.js';
  import { onMount, onDestroy } from 'svelte';
  import { marked } from 'marked';
  import DataViewPanel from './DataViewPanel.svelte';
  import ViewModeToolbar from './ViewModeToolbar.svelte';

  // Debug logger
  function debugLog(context, message, data = null) {
    const timestamp = new Date().toISOString().split('T')[1].slice(0, 12);
    const prefix = `[PL ${timestamp}] [ChatPanel:${context}]`;
    if (data !== null) {
      console.log(prefix, message, data);
    } else {
      console.log(prefix, message);
    }
  }

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
  let showFolderMenu = null; // Index of response showing folder menu
  let expandedViewIndex = null; // Index of message showing in data view mode

  // Add note modal state
  let showAddNoteModal = false;
  let noteContext = ''; // Context from the conversation
  let noteText = '';
  let isSavingNote = false;
  let noteSaved = false;

  // Voice input state
  let isListening = false;
  let speechRecognition = null;
  let voiceSupported = false;
  let interimTranscript = '';

  // Animated spinner
  const spinnerFrames = ['/', '—', '\\', '|'];
  let spinnerIndex = 0;
  let spinnerChar = spinnerFrames[0];
  let spinnerInterval = null;

  onMount(() => {
    loadSavedFolders();
    initSpeechRecognition();
  });

  onDestroy(() => {
    if (speechRecognition) {
      speechRecognition.abort();
    }
  });

  function initSpeechRecognition() {
    // Check for browser support
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;

    if (!SpeechRecognition) {
      console.log('Speech recognition not supported');
      voiceSupported = false;
      return;
    }

    voiceSupported = true;
    speechRecognition = new SpeechRecognition();
    speechRecognition.continuous = false;
    speechRecognition.interimResults = true;
    speechRecognition.lang = 'en-AU'; // Australian English

    speechRecognition.onstart = () => {
      isListening = true;
      interimTranscript = '';
    };

    speechRecognition.onend = () => {
      isListening = false;
      interimTranscript = '';
    };

    speechRecognition.onerror = (event) => {
      console.error('Speech recognition error:', event.error);
      isListening = false;
      interimTranscript = '';

      if (event.error === 'not-allowed') {
        alert('Microphone access denied. Please allow microphone access in your browser settings.');
      }
    };

    speechRecognition.onresult = (event) => {
      let finalTranscript = '';
      interimTranscript = '';

      for (let i = event.resultIndex; i < event.results.length; i++) {
        const transcript = event.results[i][0].transcript;
        if (event.results[i].isFinal) {
          finalTranscript += transcript;
        } else {
          interimTranscript += transcript;
        }
      }

      if (finalTranscript) {
        inputValue = finalTranscript;
        // Auto-send after voice input
        setTimeout(() => {
          if (inputValue.trim()) {
            sendMessage();
          }
        }, 300);
      }
    };
  }

  function toggleVoiceInput() {
    if (!voiceSupported) {
      alert('Voice input is not supported in this browser. Try using Chrome or Edge.');
      return;
    }

    if (isListening) {
      speechRecognition.stop();
    } else {
      try {
        speechRecognition.start();
      } catch (e) {
        // Already started, restart
        speechRecognition.stop();
        setTimeout(() => speechRecognition.start(), 100);
      }
    }
  }

  // Start/stop spinner animation based on loading state
  $: if (isLoading) {
    if (!spinnerInterval) {
      spinnerInterval = setInterval(() => {
        spinnerIndex = (spinnerIndex + 1) % spinnerFrames.length;
        spinnerChar = spinnerFrames[spinnerIndex];
      }, 100);
    }
  } else {
    if (spinnerInterval) {
      clearInterval(spinnerInterval);
      spinnerInterval = null;
      spinnerIndex = 0;
      spinnerChar = spinnerFrames[0];
    }
  }

  function toggleDataView(idx) {
    if (expandedViewIndex === idx) {
      expandedViewIndex = null;
      viewMode.set('response');
    } else {
      expandedViewIndex = idx;
    }
  }

  function getLastAssistantMessage() {
    for (let i = $chatMessages.length - 1; i >= 0; i--) {
      if ($chatMessages[i].role === 'assistant' && !$chatMessages[i].isError) {
        return { msg: $chatMessages[i], idx: i };
      }
    }
    return null;
  }

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

    debugLog('SEND', `Sending message: "${userMessage.substring(0, 50)}..."`);

    // Check if daemon is connected first
    if (!$daemonConnected) {
      debugLog('SEND', 'WARNING: Daemon not marked as connected, attempting anyway...');
    }

    // Add user message
    chatMessages.update(msgs => [...msgs, {
      role: 'user',
      content: userMessage,
      timestamp: new Date().toISOString()
    }]);

    isLoading = true;
    const startTime = performance.now();

    try {
      debugLog('API', 'Calling chat API...');

      // Use the API helper which handles both Tauri and browser contexts
      const data = await apiChat(userMessage);

      const elapsed = Math.round(performance.now() - startTime);
      debugLog('API', `Response received in ${elapsed}ms`, {
        responseLength: data.response?.length || 0,
        sources: data.sources?.length || 0
      });

      chatMessages.update(msgs => [...msgs, {
        role: 'assistant',
        content: data.response || data.message || 'No response received from API',
        sources: data.sources || [],
        timestamp: new Date().toISOString()
      }]);

      // Auto-expand War Room view for the new response
      const newMsgIndex = $chatMessages.length; // This will be the index after update
      setTimeout(() => {
        expandedViewIndex = newMsgIndex;
        viewMode.set('warroom');
      }, 100);
    } catch (e) {
      const elapsed = Math.round(performance.now() - startTime);
      debugLog('ERROR', `Chat failed after ${elapsed}ms: ${e.message}`, { error: e });

      let errorMessage = 'Error: Could not connect to Promethean Light daemon.';

      // Provide more specific error messages
      if (e.message.includes('Failed to fetch') || e.message.includes('Cannot connect')) {
        errorMessage = 'Error: Cannot connect to Promethean Light daemon. Please ensure:\n' +
          '1. The daemon is running (check the terminal window)\n' +
          '2. Click the Refresh button in the sidebar\n' +
          '3. If the daemon crashed, restart it with START_PL2000.bat';
      } else if (e.message.includes('API error')) {
        errorMessage = `Error: ${e.message}`;
      } else if (e.message.includes('timeout')) {
        errorMessage = 'Error: Request timed out. The query may be too complex or the daemon is overloaded.';
      }

      chatMessages.update(msgs => [...msgs, {
        role: 'assistant',
        content: errorMessage,
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

    debugLog('SAVE', `Saving response at index ${msgIndex}`);
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

      const response = await fetch('http://127.0.0.1:8000/add', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          text: conversationText,
          source: 'saved-chat'
        })
      });

      if (!response.ok) {
        debugLog('SAVE', `Save failed with status ${response.status}`);
        throw new Error(`Save failed: ${response.status}`);
      }

      debugLog('SAVE', 'Response saved successfully');
      savedId = msgIndex;
      setTimeout(() => { if (savedId === msgIndex) savedId = null; }, 3000);
    } catch (e) {
      debugLog('SAVE', `Failed to save: ${e.message}`);
      console.error('Failed to save:', e);
      // Still mark as saved locally even if server save fails
      savedId = msgIndex;
      setTimeout(() => { if (savedId === msgIndex) savedId = null; }, 3000);
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

  // Ask a question immediately (for lozenge clicks)
  function askQuestion(question) {
    inputValue = question;
    sendMessage();
  }

  function toggleFolderMenu(idx) {
    showFolderMenu = showFolderMenu === idx ? null : idx;
  }

  function saveToSelectedFolder(folderId, msgIndex) {
    const assistantMsg = $chatMessages[msgIndex];
    const userMsg = $chatMessages[msgIndex - 1];

    if (!assistantMsg || !userMsg || userMsg.role !== 'user') return;

    saveToFolder(folderId, {
      query: userMsg.content,
      response: assistantMsg.content,
      sources: assistantMsg.sources || [],
      timestamp: assistantMsg.timestamp
    });

    showFolderMenu = null;
    savedId = msgIndex;
    setTimeout(() => { if (savedId === msgIndex) savedId = null; }, 2000);
  }

  function openAddNoteWithContext(msgIndex) {
    const assistantMsg = $chatMessages[msgIndex];
    const userMsg = $chatMessages[msgIndex - 1];

    if (userMsg && assistantMsg) {
      noteContext = `Re: "${userMsg.content.substring(0, 100)}${userMsg.content.length > 100 ? '...' : ''}"`;
    } else {
      noteContext = '';
    }
    noteText = '';
    noteSaved = false;
    showAddNoteModal = true;
  }

  async function saveNote() {
    if (!noteText.trim()) return;

    isSavingNote = true;

    try {
      const fullNote = noteContext
        ? `${noteContext}\n\n${noteText}`
        : noteText;

      const response = await fetch('http://127.0.0.1:8000/add', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          text: fullNote,
          source: 'note:user-annotation'
        })
      });

      if (response.ok) {
        noteSaved = true;
        setTimeout(() => {
          showAddNoteModal = false;
          noteSaved = false;
        }, 1500);
      }
    } catch (e) {
      console.error('Failed to save note:', e);
    } finally {
      isSavingNote = false;
    }
  }

  function closeNoteModal() {
    showAddNoteModal = false;
    noteText = '';
    noteContext = '';
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
        <p class="welcome-title">What would you like to know?</p>

        <!-- Centered search lozenge -->
        <div class="center-search-container">
          <div class="center-search-lozenge">
            <svg class="search-icon" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <circle cx="11" cy="11" r="8"/>
              <path d="m21 21-4.35-4.35"/>
            </svg>
            {#if isListening}
              <input
                type="text"
                value={interimTranscript || 'Listening...'}
                placeholder="Listening..."
                disabled={true}
                class="center-input listening-input"
              />
            {:else}
              <input
                type="text"
                bind:value={inputValue}
                on:keydown={handleKeydown}
                placeholder="Ask a question about your data..."
                disabled={isLoading}
                class="center-input"
                autofocus
              />
            {/if}
            {#if voiceSupported}
              <button
                class="center-mic-btn"
                class:listening={isListening}
                on:click={toggleVoiceInput}
                title={isListening ? 'Stop listening' : 'Voice input'}
                disabled={isLoading}
              >
                {#if isListening}
                  <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor">
                    <rect x="6" y="6" width="12" height="12" rx="2"/>
                  </svg>
                {:else}
                  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z"/>
                    <path d="M19 10v2a7 7 0 0 1-14 0v-2"/>
                    <line x1="12" y1="19" x2="12" y2="23"/>
                    <line x1="8" y1="23" x2="16" y2="23"/>
                  </svg>
                {/if}
              </button>
            {/if}
            <button
              class="center-send-btn"
              on:click={sendMessage}
              disabled={isLoading || isListening || !inputValue.trim()}
              title="Send message"
            >
              {#if isLoading}
                <span class="btn-spinner">{spinnerChar}</span>
              {:else}
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <line x1="22" y1="2" x2="11" y2="13"/>
                  <polygon points="22 2 15 22 11 13 2 9 22 2"/>
                </svg>
              {/if}
            </button>
          </div>
          <p class="search-hint">Press Enter to search, or click a suggestion below</p>
        </div>

        <div class="query-section">
          <span class="section-label">Team & People</span>
          <div class="lozenges">
            <button class="lozenge people" on:click={() => askQuestion('List all team members with their roles')}>
              Team members
            </button>
            <button class="lozenge people" on:click={() => askQuestion('Show team salary summary by region')}>
              Salary by region
            </button>
            <button class="lozenge people" on:click={() => askQuestion('Who has retention bonuses and when do they expire?')}>
              Retention bonuses
            </button>
            <button class="lozenge people" on:click={() => askQuestion('Show India team details with salary bands')}>
              India team
            </button>
            <button class="lozenge people" on:click={() => askQuestion('Show Australia team salaries')}>
              Australia team
            </button>
          </div>
        </div>

        <div class="query-section">
          <span class="section-label">Projects & Pipeline</span>
          <div class="lozenges">
            <button class="lozenge projects" on:click={() => askQuestion('What active projects are we working on?')}>
              Active projects
            </button>
            <button class="lozenge projects" on:click={() => askQuestion('Show project pipeline summary')}>
              Pipeline summary
            </button>
            <button class="lozenge projects" on:click={() => askQuestion('What are the key project milestones coming up?')}>
              Upcoming milestones
            </button>
            <button class="lozenge projects" on:click={() => askQuestion('Show Mt Challenger project details')}>
              Mt Challenger
            </button>
          </div>
        </div>

        <div class="query-section">
          <span class="section-label">Emails & Communications</span>
          <div class="lozenges">
            <button class="lozenge emails" on:click={() => askQuestion('Show recent important emails')}>
              Recent emails
            </button>
            <button class="lozenge emails" on:click={() => askQuestion('What urgent items need my attention?')}>
              Urgent items
            </button>
            <button class="lozenge emails" on:click={() => askQuestion('Show emails about budget discussions')}>
              Budget emails
            </button>
            <button class="lozenge emails" on:click={() => askQuestion('What client communications happened this week?')}>
              Client comms
            </button>
          </div>
        </div>

        <div class="query-section">
          <span class="section-label">Analysis & Reports</span>
          <div class="lozenges">
            <button class="lozenge analysis" on:click={() => askQuestion('Show timesheet analysis summary')}>
              Timesheet analysis
            </button>
            <button class="lozenge analysis" on:click={() => askQuestion('What are the key findings from recent reports?')}>
              Report findings
            </button>
            <button class="lozenge analysis" on:click={() => askQuestion('Show PM burn rate analysis')}>
              PM burn rates
            </button>
            <button class="lozenge analysis" on:click={() => askQuestion('Summarize Project Sentinel status')}>
              Project Sentinel
            </button>
          </div>
        </div>

        <div class="query-section">
          <span class="section-label">Quick Actions</span>
          <div class="lozenges">
            <button class="lozenge action" on:click={() => askQuestion('List all saved notes')}>
              My notes
            </button>
            <button class="lozenge action" on:click={() => askQuestion('What documents were recently added?')}>
              Recent docs
            </button>
            <button class="lozenge action" on:click={() => askQuestion('Search for salary review discussions')}>
              Salary reviews
            </button>
          </div>
        </div>

        <div class="query-section">
          <span class="section-label">Quick Reports</span>
          <div class="lozenges">
            <button class="lozenge report" on:click={() => askQuestion('Summarize all team pay by region in a table')}>
              Team Pay Summary
            </button>
            <button class="lozenge report" on:click={() => askQuestion('List all retention bonuses with names, amounts, and expiry dates')}>
              Retention Bonuses
            </button>
            <button class="lozenge report" on:click={() => askQuestion('Show Project Sentinel status and key milestones')}>
              Project Sentinel
            </button>
            <button class="lozenge report" on:click={() => askQuestion('Which staff have had salary reviews and which are still pending?')}>
              Salary Review Status
            </button>
          </div>
        </div>
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
                    class="action-btn view-btn"
                    class:active={expandedViewIndex === idx}
                    on:click={() => toggleDataView(idx)}
                    title="View in different formats"
                  >
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                      <rect x="3" y="3" width="7" height="7"/>
                      <rect x="14" y="3" width="7" height="7"/>
                      <rect x="14" y="14" width="7" height="7"/>
                      <rect x="3" y="14" width="7" height="7"/>
                    </svg>
                    Views
                  </button>
                  <button
                    class="action-btn add-note-btn"
                    on:click={() => openAddNoteWithContext(idx)}
                    title="Add your thoughts or notes about this"
                  >
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                      <path d="M12 5v14M5 12h14"/>
                    </svg>
                    Add Note
                  </button>
                  <button
                    class="action-btn"
                    class:success={copiedId === idx}
                    on:click={() => copyResponse(msg.content, idx)}
                  >
                    {copiedId === idx ? 'Copied!' : 'Copy'}
                  </button>
                  <div class="save-dropdown">
                    <button
                      class="action-btn save"
                      class:success={savedId === idx}
                      on:click={() => toggleFolderMenu(idx)}
                    >
                      {#if savedId === idx}
                        Saved!
                      {:else}
                        Save
                        <svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                          <path d="m6 9 6 6 6-6"/>
                        </svg>
                      {/if}
                    </button>
                    {#if showFolderMenu === idx}
                      <div class="folder-menu">
                        {#each $savedFolders as folder}
                          <button class="folder-option" on:click={() => saveToSelectedFolder(folder.id, idx)}>
                            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                              <path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"/>
                            </svg>
                            {folder.name}
                          </button>
                        {/each}
                      </div>
                    {/if}
                  </div>
                </div>
                {#if expandedViewIndex === idx}
                  <div class="data-view-expanded">
                    <DataViewPanel
                      query={$chatMessages[idx - 1]?.content || ''}
                      response={msg.content}
                      sources={msg.sources || []}
                    />
                  </div>
                {/if}
              {/if}
            </div>
          {/if}
        </div>
      {/each}
      {#if isLoading}
        <div class="entry">
          <div class="response loading">
            <span class="spinner">{spinnerChar}</span>
          </div>
        </div>
      {/if}
    {/if}
  </div>

  {#if $chatMessages.length > 0}
    <div class="terminal-input">
      <span class="prompt">> </span>
      {#if isListening}
        <input
          type="text"
          value={interimTranscript || 'Listening...'}
          placeholder="Listening..."
          disabled={true}
          class="listening-input"
        />
      {:else}
        <input
          type="text"
          bind:value={inputValue}
          on:keydown={handleKeydown}
          placeholder="Ask a question..."
          disabled={isLoading}
        />
      {/if}
      {#if voiceSupported}
        <button
          class="mic-btn"
          class:listening={isListening}
          on:click={toggleVoiceInput}
          title={isListening ? 'Stop listening' : 'Voice input'}
          disabled={isLoading}
        >
          {#if isListening}
            <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
              <rect x="6" y="6" width="12" height="12" rx="2"/>
            </svg>
          {:else}
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z"/>
              <path d="M19 10v2a7 7 0 0 1-14 0v-2"/>
              <line x1="12" y1="19" x2="12" y2="23"/>
              <line x1="8" y1="23" x2="16" y2="23"/>
            </svg>
          {/if}
        </button>
      {/if}
      <button
        class="send-btn"
        on:click={sendMessage}
        disabled={isLoading || isListening || !inputValue.trim()}
        title="Send message"
      >
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <line x1="22" y1="2" x2="11" y2="13"/>
          <polygon points="22 2 15 22 11 13 2 9 22 2"/>
        </svg>
      </button>
    </div>
  {/if}
</div>

<!-- Add Note Modal -->
{#if showAddNoteModal}
  <div class="note-modal-overlay" on:click={closeNoteModal}>
    <div class="note-modal" on:click|stopPropagation>
      <div class="note-modal-header">
        <h3>
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M12 5v14M5 12h14"/>
          </svg>
          Add Note
        </h3>
        <button class="close-modal" on:click={closeNoteModal}>
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M18 6L6 18M6 6l12 12"/>
          </svg>
        </button>
      </div>
      {#if noteContext}
        <div class="note-context">{noteContext}</div>
      {/if}
      <textarea
        class="note-input"
        placeholder="Add your thoughts, insights, or notes..."
        bind:value={noteText}
        rows="6"
        disabled={isSavingNote || noteSaved}
      ></textarea>
      <div class="note-modal-footer">
        <span class="note-hint">This note will be indexed and searchable</span>
        <button
          class="save-note-btn"
          class:success={noteSaved}
          on:click={saveNote}
          disabled={!noteText.trim() || isSavingNote || noteSaved}
        >
          {#if isSavingNote}
            <span class="spinner"></span> Saving...
          {:else if noteSaved}
            Saved!
          {:else}
            Save Note
          {/if}
        </button>
      </div>
    </div>
  </div>
{/if}

<style>
  .terminal {
    display: flex;
    flex-direction: column;
    height: 100%;
    background: var(--bg-primary);
    font-family: 'Segoe UI', 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
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
    padding: 20px 0;
    display: flex;
    flex-direction: column;
    align-items: center;
    text-align: center;
  }

  .welcome-title {
    font-size: 28px;
    font-weight: 600;
    color: var(--text-primary);
    margin: 0 0 28px 0;
  }

  /* Center Search Lozenge Styles */
  .center-search-container {
    width: 100%;
    max-width: 650px;
    margin-bottom: 32px;
  }

  .center-search-lozenge {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 14px 20px;
    background: var(--bg-secondary);
    border: 2px solid var(--border-color);
    border-radius: 50px;
    transition: all 0.2s;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  }

  .center-search-lozenge:focus-within {
    border-color: var(--accent-orange);
    box-shadow: 0 4px 20px rgba(249, 115, 22, 0.2);
  }

  .center-search-lozenge .search-icon {
    color: var(--text-muted);
    flex-shrink: 0;
  }

  .center-search-lozenge:focus-within .search-icon {
    color: var(--accent-orange);
  }

  .center-input {
    flex: 1;
    background: transparent;
    border: none;
    color: var(--text-primary);
    font-family: inherit;
    font-size: 18px;
    outline: none;
    caret-color: var(--accent-orange);
  }

  .center-input::placeholder {
    color: var(--text-muted);
  }

  .center-input:disabled {
    opacity: 0.6;
  }

  .center-mic-btn,
  .center-send-btn {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 38px;
    height: 38px;
    background: var(--bg-tertiary);
    border: 1px solid var(--border-color);
    border-radius: 50%;
    color: var(--text-secondary);
    cursor: pointer;
    transition: all 0.2s;
    flex-shrink: 0;
  }

  .center-mic-btn:hover:not(:disabled),
  .center-send-btn:hover:not(:disabled) {
    background: var(--bg-secondary);
    border-color: var(--text-muted);
    color: var(--text-primary);
  }

  .center-mic-btn:disabled,
  .center-send-btn:disabled {
    opacity: 0.4;
    cursor: not-allowed;
  }

  .center-mic-btn.listening {
    background: var(--accent-red);
    border-color: var(--accent-red);
    color: white;
    animation: pulse 1.5s ease-in-out infinite;
  }

  .center-send-btn {
    background: var(--accent-orange);
    border-color: var(--accent-orange);
    color: white;
  }

  .center-send-btn:hover:not(:disabled) {
    background: #ea580c;
    border-color: #ea580c;
    color: white;
  }

  .btn-spinner {
    font-weight: bold;
    font-size: 16px;
  }

  .search-hint {
    margin-top: 10px;
    font-size: 12px;
    color: var(--text-muted);
  }

  .query-section {
    margin-bottom: 20px;
    width: 100%;
    max-width: 600px;
  }

  .section-label {
    display: block;
    font-size: 13px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    color: var(--text-muted);
    margin-bottom: 12px;
  }

  .lozenges {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    justify-content: center;
  }

  .lozenge {
    display: inline-flex;
    align-items: center;
    padding: 10px 18px;
    border-radius: 22px;
    font-size: 15px;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.2s;
    border: 1px solid transparent;
    font-family: inherit;
  }

  .lozenge.people {
    background: rgba(139, 92, 246, 0.15);
    color: #a78bfa;
    border-color: rgba(139, 92, 246, 0.3);
  }

  .lozenge.people:hover {
    background: rgba(139, 92, 246, 0.25);
    border-color: #a78bfa;
  }

  .lozenge.projects {
    background: rgba(34, 197, 94, 0.15);
    color: #4ade80;
    border-color: rgba(34, 197, 94, 0.3);
  }

  .lozenge.projects:hover {
    background: rgba(34, 197, 94, 0.25);
    border-color: #4ade80;
  }

  .lozenge.emails {
    background: rgba(59, 130, 246, 0.15);
    color: #60a5fa;
    border-color: rgba(59, 130, 246, 0.3);
  }

  .lozenge.emails:hover {
    background: rgba(59, 130, 246, 0.25);
    border-color: #60a5fa;
  }

  .lozenge.analysis {
    background: rgba(249, 115, 22, 0.15);
    color: #fb923c;
    border-color: rgba(249, 115, 22, 0.3);
  }

  .lozenge.analysis:hover {
    background: rgba(249, 115, 22, 0.25);
    border-color: #fb923c;
  }

  .lozenge.action {
    background: rgba(236, 72, 153, 0.15);
    color: #f472b6;
    border-color: rgba(236, 72, 153, 0.3);
  }

  .lozenge.action:hover {
    background: rgba(236, 72, 153, 0.25);
    border-color: #f472b6;
  }

  .lozenge.report {
    background: rgba(234, 179, 8, 0.15);
    color: #fbbf24;
    border-color: rgba(234, 179, 8, 0.3);
  }

  .lozenge.report:hover {
    background: rgba(234, 179, 8, 0.25);
    border-color: #fbbf24;
  }

  .entry {
    margin-bottom: 16px;
  }

  .entry.error .response-text {
    color: var(--accent-red);
  }

  .query {
    color: var(--accent-orange);
    font-size: 18px;
    margin-bottom: 12px;
    font-weight: 500;
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
    padding: 24px;
    font-size: 18px;
    line-height: 1.8;
    color: var(--text-primary);
    word-wrap: break-word;
    font-family: 'Segoe UI', 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    overflow-x: auto;
    letter-spacing: 0.01em;
  }

  .response-text :global(p) {
    margin: 0 0 12px 0;
  }

  .response-text :global(p:last-child) {
    margin-bottom: 0;
  }

  .response-text :global(table) {
    border-collapse: collapse;
    width: auto;
    max-width: 100%;
    margin: 14px 0;
    font-size: 14px;
    border: 1px solid var(--border-color);
    border-radius: 6px;
    overflow: hidden;
  }

  .response-text :global(th),
  .response-text :global(td) {
    border: none;
    border-bottom: 1px solid var(--border-color);
    padding: 6px 14px;
    text-align: left;
    white-space: nowrap;
  }

  .response-text :global(th) {
    background: var(--bg-tertiary);
    font-weight: 600;
    font-size: 13px;
    text-transform: uppercase;
    letter-spacing: 0.3px;
    color: var(--text-secondary);
  }

  .response-text :global(tr:last-child td) {
    border-bottom: none;
  }

  .response-text :global(tbody tr:nth-child(even)) {
    background: rgba(255, 255, 255, 0.02);
  }

  .response-text :global(tbody tr:hover) {
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

  .save-dropdown {
    position: relative;
  }

  .action-btn.save {
    display: flex;
    align-items: center;
    gap: 4px;
  }

  .folder-menu {
    position: absolute;
    bottom: 100%;
    right: 0;
    margin-bottom: 4px;
    background: var(--bg-secondary);
    border: 1px solid var(--border-color);
    border-radius: 6px;
    min-width: 150px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
    z-index: 100;
    overflow: hidden;
  }

  .folder-option {
    display: flex;
    align-items: center;
    gap: 8px;
    width: 100%;
    padding: 10px 14px;
    background: transparent;
    border: none;
    color: var(--text-secondary);
    font-size: 13px;
    text-align: left;
    cursor: pointer;
    transition: all 0.15s;
  }

  .folder-option:hover {
    background: var(--bg-tertiary);
    color: var(--accent-orange);
  }

  .folder-option svg {
    flex-shrink: 0;
  }

  .view-btn {
    display: flex;
    align-items: center;
    gap: 6px;
  }

  .view-btn.active {
    background: var(--accent-blue);
    border-color: var(--accent-blue);
    color: white;
  }

  .data-view-expanded {
    border-top: 1px solid var(--border-color);
    background: var(--bg-primary);
    max-height: 400px;
    overflow: auto;
  }

  .loading {
    padding: 16px;
    color: var(--text-muted);
  }

  .spinner {
    font-weight: bold;
    color: var(--accent-orange);
    font-size: 16px;
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
    font-family: 'Segoe UI', 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    font-size: 18px;
    outline: none;
  }

  .terminal-input input::placeholder {
    color: var(--text-muted);
  }

  .terminal-input input:disabled {
    opacity: 0.5;
  }

  .mic-btn,
  .send-btn {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 36px;
    height: 36px;
    margin-left: 8px;
    background: var(--bg-tertiary);
    border: 1px solid var(--border-color);
    border-radius: 8px;
    color: var(--text-secondary);
    cursor: pointer;
    transition: all 0.2s;
  }

  .mic-btn:hover:not(:disabled),
  .send-btn:hover:not(:disabled) {
    background: var(--bg-secondary);
    border-color: var(--text-muted);
    color: var(--text-primary);
  }

  .mic-btn:disabled,
  .send-btn:disabled {
    opacity: 0.4;
    cursor: not-allowed;
  }

  .mic-btn.listening {
    background: var(--accent-red);
    border-color: var(--accent-red);
    color: white;
    animation: pulse 1.5s ease-in-out infinite;
  }

  @keyframes pulse {
    0%, 100% {
      box-shadow: 0 0 0 0 rgba(239, 68, 68, 0.4);
    }
    50% {
      box-shadow: 0 0 0 8px rgba(239, 68, 68, 0);
    }
  }

  .send-btn {
    background: var(--accent-orange);
    border-color: var(--accent-orange);
    color: white;
  }

  .send-btn:hover:not(:disabled) {
    background: #ea580c;
    border-color: #ea580c;
    color: white;
  }

  /* Add Note Button */
  .add-note-btn {
    display: flex;
    align-items: center;
    gap: 4px;
    color: var(--accent-green) !important;
    border-color: var(--accent-green) !important;
  }

  .add-note-btn:hover {
    background: var(--accent-green) !important;
    color: white !important;
  }

  /* Note Modal Styles */
  .note-modal-overlay {
    position: fixed;
    inset: 0;
    background: rgba(0, 0, 0, 0.7);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 1000;
    backdrop-filter: blur(4px);
  }

  .note-modal {
    background: var(--bg-secondary);
    border: 1px solid var(--border-color);
    border-radius: 12px;
    width: 90%;
    max-width: 500px;
    box-shadow: 0 20px 40px rgba(0, 0, 0, 0.5);
  }

  .note-modal-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 16px 20px;
    border-bottom: 1px solid var(--border-color);
  }

  .note-modal-header h3 {
    display: flex;
    align-items: center;
    gap: 8px;
    margin: 0;
    font-size: 16px;
    font-weight: 600;
    color: var(--text-primary);
  }

  .note-modal-header h3 svg {
    color: var(--accent-green);
  }

  .close-modal {
    background: none;
    border: none;
    color: var(--text-muted);
    cursor: pointer;
    padding: 4px;
    border-radius: 4px;
    transition: all 0.2s;
  }

  .close-modal:hover {
    background: var(--bg-tertiary);
    color: var(--text-primary);
  }

  .note-context {
    padding: 12px 20px;
    background: var(--bg-tertiary);
    border-bottom: 1px solid var(--border-color);
    font-size: 12px;
    color: var(--text-secondary);
    font-style: italic;
  }

  .note-input {
    width: 100%;
    padding: 16px 20px;
    background: var(--bg-primary);
    border: none;
    border-bottom: 1px solid var(--border-color);
    color: var(--text-primary);
    font-family: inherit;
    font-size: 14px;
    resize: vertical;
    min-height: 120px;
  }

  .note-input::placeholder {
    color: var(--text-muted);
  }

  .note-input:focus {
    outline: none;
    background: var(--bg-secondary);
  }

  .note-modal-footer {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 14px 20px;
  }

  .note-hint {
    font-size: 11px;
    color: var(--text-muted);
  }

  .save-note-btn {
    display: flex;
    align-items: center;
    gap: 6px;
    background: var(--accent-green);
    border: none;
    color: white;
    padding: 10px 20px;
    border-radius: 6px;
    font-size: 13px;
    font-weight: 600;
    font-family: inherit;
    cursor: pointer;
    transition: all 0.2s;
  }

  .save-note-btn:hover:not(:disabled) {
    background: #2da44e;
  }

  .save-note-btn:disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }

  .save-note-btn.success {
    background: var(--accent-green);
  }

  .save-note-btn .spinner {
    width: 14px;
    height: 14px;
    border: 2px solid transparent;
    border-top-color: white;
    border-radius: 50%;
    animation: spin 0.8s linear infinite;
  }
</style>
