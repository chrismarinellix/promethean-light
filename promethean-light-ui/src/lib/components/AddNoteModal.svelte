<script>
  import { createEventDispatcher } from 'svelte';

  export let visible = false;

  const dispatch = createEventDispatcher();

  let noteText = '';
  let noteSource = '';
  let isSubmitting = false;
  let error = '';
  let success = '';

  async function handleSubmit() {
    if (!noteText.trim()) {
      error = 'Please enter some text';
      return;
    }

    isSubmitting = true;
    error = '';
    success = '';

    try {
      const response = await fetch('http://127.0.0.1:8000/add', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          text: noteText.trim(),
          source: noteSource.trim() || 'note'
        })
      });

      if (!response.ok) {
        throw new Error('Failed to add note');
      }

      const result = await response.json();
      success = 'Note added successfully!';
      noteText = '';
      noteSource = '';

      // Close after a moment
      setTimeout(() => {
        dispatch('added');
        handleClose();
      }, 1000);

    } catch (e) {
      error = e.message || 'Failed to add note';
    } finally {
      isSubmitting = false;
    }
  }

  function handleClose() {
    visible = false;
    error = '';
    success = '';
    dispatch('close');
  }

  function handleKeydown(e) {
    if (e.key === 'Escape') {
      handleClose();
    }
    if (e.key === 'Enter' && e.ctrlKey) {
      handleSubmit();
    }
  }
</script>

{#if visible}
  <div class="modal-overlay" on:click={handleClose} on:keydown={handleKeydown}>
    <div class="modal" on:click|stopPropagation>
      <div class="modal-header">
        <h2>Add Note / Paste</h2>
        <button class="close-btn" on:click={handleClose}>
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M18 6L6 18M6 6l12 12"/>
          </svg>
        </button>
      </div>

      <div class="modal-body">
        <div class="field">
          <label for="note-text">Content</label>
          <textarea
            id="note-text"
            bind:value={noteText}
            placeholder="Paste or type your note here...

You can paste:
- Meeting notes
- Code snippets
- Ideas & reminders
- Any text you want to search later"
            rows="10"
            disabled={isSubmitting}
          ></textarea>
        </div>

        <div class="field">
          <label for="note-source">Label (optional)</label>
          <input
            id="note-source"
            type="text"
            bind:value={noteSource}
            placeholder="e.g., meeting-notes, project-ideas, research"
            disabled={isSubmitting}
          />
          <span class="hint">Helps you identify this note later</span>
        </div>

        {#if error}
          <div class="message error">{error}</div>
        {/if}
        {#if success}
          <div class="message success">{success}</div>
        {/if}
      </div>

      <div class="modal-footer">
        <span class="shortcut-hint">Ctrl+Enter to save</span>
        <div class="buttons">
          <button class="btn secondary" on:click={handleClose} disabled={isSubmitting}>
            Cancel
          </button>
          <button class="btn primary" on:click={handleSubmit} disabled={isSubmitting || !noteText.trim()}>
            {#if isSubmitting}
              Saving...
            {:else}
              Save Note
            {/if}
          </button>
        </div>
      </div>
    </div>
  </div>
{/if}

<style>
  .modal-overlay {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(0, 0, 0, 0.7);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 1000;
    backdrop-filter: blur(4px);
  }

  .modal {
    background: var(--bg-secondary);
    border: 1px solid var(--border-color);
    border-radius: 12px;
    width: 90%;
    max-width: 600px;
    max-height: 90vh;
    display: flex;
    flex-direction: column;
    box-shadow: 0 20px 40px rgba(0, 0, 0, 0.4);
  }

  .modal-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 20px 24px;
    border-bottom: 1px solid var(--border-color);
  }

  .modal-header h2 {
    margin: 0;
    font-size: 18px;
    color: var(--text-primary);
  }

  .close-btn {
    background: transparent;
    border: none;
    color: var(--text-muted);
    cursor: pointer;
    padding: 4px;
    border-radius: 4px;
    transition: all 0.2s;
  }

  .close-btn:hover {
    color: var(--text-primary);
    background: var(--bg-tertiary);
  }

  .modal-body {
    padding: 24px;
    overflow-y: auto;
  }

  .field {
    margin-bottom: 20px;
  }

  .field label {
    display: block;
    margin-bottom: 8px;
    font-size: 13px;
    font-weight: 600;
    color: var(--text-secondary);
  }

  .field textarea {
    width: 100%;
    padding: 12px;
    background: var(--bg-primary);
    border: 1px solid var(--border-color);
    border-radius: 8px;
    color: var(--text-primary);
    font-size: 14px;
    font-family: inherit;
    resize: vertical;
    min-height: 150px;
    box-sizing: border-box;
  }

  .field textarea:focus {
    outline: none;
    border-color: var(--accent-orange);
  }

  .field textarea::placeholder {
    color: var(--text-muted);
  }

  .field input {
    width: 100%;
    padding: 10px 12px;
    background: var(--bg-primary);
    border: 1px solid var(--border-color);
    border-radius: 8px;
    color: var(--text-primary);
    font-size: 14px;
    box-sizing: border-box;
  }

  .field input:focus {
    outline: none;
    border-color: var(--accent-orange);
  }

  .hint {
    display: block;
    margin-top: 6px;
    font-size: 12px;
    color: var(--text-muted);
  }

  .message {
    padding: 10px 14px;
    border-radius: 8px;
    font-size: 13px;
    margin-top: 12px;
  }

  .message.error {
    background: rgba(248, 81, 73, 0.15);
    border: 1px solid var(--accent-red);
    color: var(--accent-red);
  }

  .message.success {
    background: rgba(63, 185, 80, 0.15);
    border: 1px solid var(--accent-green);
    color: var(--accent-green);
  }

  .modal-footer {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 16px 24px;
    border-top: 1px solid var(--border-color);
  }

  .shortcut-hint {
    font-size: 12px;
    color: var(--text-muted);
  }

  .buttons {
    display: flex;
    gap: 12px;
  }

  .btn {
    padding: 10px 20px;
    border-radius: 8px;
    font-size: 14px;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.2s;
  }

  .btn.primary {
    background: var(--accent-orange);
    border: none;
    color: white;
  }

  .btn.primary:hover:not(:disabled) {
    background: #ea580c;
  }

  .btn.primary:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }

  .btn.secondary {
    background: transparent;
    border: 1px solid var(--border-color);
    color: var(--text-secondary);
  }

  .btn.secondary:hover:not(:disabled) {
    background: var(--bg-tertiary);
  }
</style>
