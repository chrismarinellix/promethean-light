<script>
  import { createEventDispatcher } from 'svelte';

  export let visible = false;
  export let isStarting = false;
  export let error = '';

  const dispatch = createEventDispatcher();

  let passphrase = '';

  function handleSubmit() {
    if (!passphrase.trim()) return;
    dispatch('unlock', { passphrase });
  }

  function handleKeydown(e) {
    if (e.key === 'Enter') {
      handleSubmit();
    }
    if (e.key === 'Escape') {
      dispatch('close');
    }
  }
</script>

{#if visible}
  <div class="modal-overlay" on:click={() => dispatch('close')} on:keydown={handleKeydown}>
    <div class="modal" on:click|stopPropagation role="dialog" aria-modal="true">
      <div class="modal-header">
        <div class="fire-icon">🔥</div>
        <h2>Unlock Promethean Light</h2>
        <p>Enter your master passphrase to start the daemon</p>
      </div>

      <div class="modal-body">
        {#if error}
          <div class="error-banner">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <circle cx="12" cy="12" r="10"/>
              <line x1="12" y1="8" x2="12" y2="12"/>
              <line x1="12" y1="16" x2="12.01" y2="16"/>
            </svg>
            {error}
          </div>
        {/if}

        <div class="input-group">
          <label for="passphrase">Master Passphrase</label>
          <div class="input-wrapper">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <rect x="3" y="11" width="18" height="11" rx="2" ry="2"/>
              <path d="M7 11V7a5 5 0 0 1 10 0v4"/>
            </svg>
            <input
              id="passphrase"
              type="password"
              bind:value={passphrase}
              on:keydown={handleKeydown}
              placeholder="Enter your passphrase..."
              disabled={isStarting}
              autofocus
            />
          </div>
        </div>

        <div class="info-box">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="12" cy="12" r="10"/>
            <path d="M12 16v-4"/>
            <path d="M12 8h.01"/>
          </svg>
          <span>Your data is encrypted locally. The passphrase never leaves your machine.</span>
        </div>
      </div>

      <div class="modal-footer">
        <button class="btn-secondary" on:click={() => dispatch('close')} disabled={isStarting}>
          Cancel
        </button>
        <button class="btn-primary" on:click={handleSubmit} disabled={isStarting || !passphrase.trim()}>
          {#if isStarting}
            <span class="spinner"></span>
            Starting...
          {:else}
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M5 12h14"/>
              <path d="m12 5 7 7-7 7"/>
            </svg>
            Unlock & Start
          {/if}
        </button>
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
    backdrop-filter: blur(4px);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 1000;
    animation: fadeIn 0.2s ease;
  }

  @keyframes fadeIn {
    from { opacity: 0; }
    to { opacity: 1; }
  }

  .modal {
    background: var(--bg-secondary);
    border: 1px solid var(--border-color);
    border-radius: var(--radius-lg);
    width: 100%;
    max-width: 420px;
    box-shadow: var(--shadow);
    animation: slideUp 0.3s ease;
  }

  @keyframes slideUp {
    from {
      opacity: 0;
      transform: translateY(20px);
    }
    to {
      opacity: 1;
      transform: translateY(0);
    }
  }

  .modal-header {
    text-align: center;
    padding: 32px 24px 16px;
  }

  .fire-icon {
    font-size: 48px;
    margin-bottom: 16px;
  }

  .modal-header h2 {
    font-size: 20px;
    font-weight: 700;
    color: var(--text-primary);
    margin-bottom: 8px;
  }

  .modal-header p {
    font-size: 14px;
    color: var(--text-secondary);
  }

  .modal-body {
    padding: 16px 24px;
  }

  .error-banner {
    display: flex;
    align-items: center;
    gap: 10px;
    background: rgba(248, 81, 73, 0.15);
    border: 1px solid var(--accent-red);
    color: var(--accent-red);
    padding: 12px 16px;
    border-radius: var(--radius);
    margin-bottom: 16px;
    font-size: 13px;
  }

  .input-group {
    margin-bottom: 16px;
  }

  .input-group label {
    display: block;
    font-size: 13px;
    font-weight: 600;
    color: var(--text-secondary);
    margin-bottom: 8px;
  }

  .input-wrapper {
    display: flex;
    align-items: center;
    gap: 12px;
    background: var(--bg-tertiary);
    border: 1px solid var(--border-color);
    border-radius: var(--radius);
    padding: 12px 16px;
    transition: border-color 0.2s;
  }

  .input-wrapper:focus-within {
    border-color: var(--accent-orange);
  }

  .input-wrapper svg {
    color: var(--text-muted);
    flex-shrink: 0;
  }

  .input-wrapper input {
    flex: 1;
    background: transparent;
    border: none;
    color: var(--text-primary);
    font-size: 15px;
    outline: none;
  }

  .input-wrapper input::placeholder {
    color: var(--text-muted);
  }

  .input-wrapper input:disabled {
    opacity: 0.6;
  }

  .info-box {
    display: flex;
    align-items: flex-start;
    gap: 10px;
    background: var(--bg-tertiary);
    padding: 12px 16px;
    border-radius: var(--radius);
    font-size: 12px;
    color: var(--text-muted);
  }

  .info-box svg {
    flex-shrink: 0;
    margin-top: 1px;
  }

  .modal-footer {
    display: flex;
    gap: 12px;
    padding: 16px 24px 24px;
    justify-content: flex-end;
  }

  .btn-secondary, .btn-primary {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 8px;
    padding: 10px 20px;
    border-radius: var(--radius);
    font-size: 14px;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.2s;
  }

  .btn-secondary {
    background: var(--bg-tertiary);
    border: 1px solid var(--border-color);
    color: var(--text-secondary);
  }

  .btn-secondary:hover:not(:disabled) {
    background: var(--bg-hover);
    color: var(--text-primary);
  }

  .btn-primary {
    background: var(--accent-orange);
    border: 1px solid var(--accent-orange);
    color: white;
    min-width: 140px;
  }

  .btn-primary:hover:not(:disabled) {
    background: #ea580c;
    transform: translateY(-1px);
  }

  .btn-secondary:disabled, .btn-primary:disabled {
    opacity: 0.6;
    cursor: not-allowed;
    transform: none;
  }

  .spinner {
    width: 14px;
    height: 14px;
    border: 2px solid transparent;
    border-top-color: white;
    border-radius: 50%;
    animation: spin 0.8s linear infinite;
  }

  @keyframes spin {
    to { transform: rotate(360deg); }
  }
</style>
