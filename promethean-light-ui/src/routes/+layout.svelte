<script>
  import '../app.css';
  import { onMount } from 'svelte';
  import { loadFavorites, daemonConnected } from '$lib/stores.js';
  import { checkDaemon, startDaemon } from '$lib/api.js';

  let initialCheckDone = false;
  let starting = false;
  let passphrase = '';
  let error = '';

  async function checkConnection() {
    try {
      const connected = await checkDaemon();
      daemonConnected.set(connected);
    } catch (e) {
      daemonConnected.set(false);
    }
    initialCheckDone = true;
  }

  async function handleStart() {
    if (!passphrase.trim()) {
      error = 'Please enter your passphrase';
      return;
    }
    starting = true;
    error = '';
    try {
      await startDaemon(passphrase);
      // Wait a moment then check connection
      await new Promise(r => setTimeout(r, 2000));
      await checkConnection();
      if (!$daemonConnected) {
        error = 'Daemon started but not responding yet. Click "Retry Connection" in a few seconds.';
      }
    } catch (e) {
      error = e.message || 'Failed to start daemon';
    }
    starting = false;
  }

  onMount(() => {
    loadFavorites();
    checkConnection();
  });
</script>

{#if !initialCheckDone}
  <div class="startup-screen">
    <div class="startup-content">
      <div class="logo">🔥</div>
      <h1>Promethean Light</h1>
      <p class="status">Checking daemon connection...</p>
      <div class="spinner"></div>
    </div>
  </div>
{:else if !$daemonConnected}
  <div class="startup-screen">
    <div class="startup-content">
      <div class="logo">🔥</div>
      <h1>Promethean Light</h1>
      <p class="subtitle">God Mode</p>

      <div class="connection-status">
        <span class="status-dot offline"></span>
        Daemon not connected
      </div>

      <div class="start-form">
        <p>Enter your passphrase to start the daemon:</p>
        <input
          type="password"
          bind:value={passphrase}
          placeholder="Master passphrase"
          on:keydown={(e) => e.key === 'Enter' && handleStart()}
          disabled={starting}
        />
        <div class="button-row">
          <button on:click={handleStart} disabled={starting} class="primary">
            {#if starting}
              Starting...
            {:else}
              Start Daemon
            {/if}
          </button>
          <button on:click={checkConnection} disabled={starting} class="secondary">
            Retry Connection
          </button>
        </div>
        {#if error}
          <p class="error">{error}</p>
        {/if}
      </div>

      <p class="hint">
        If daemon is already running, click "Retry Connection"
      </p>
    </div>
  </div>
{:else}
  <slot />
{/if}

<style>
  .startup-screen {
    height: 100vh;
    display: flex;
    align-items: center;
    justify-content: center;
    background: var(--bg-primary, #0f0f0f);
  }

  .startup-content {
    text-align: center;
    max-width: 400px;
    padding: 40px;
  }

  .logo {
    font-size: 64px;
    margin-bottom: 16px;
  }

  h1 {
    color: var(--text-primary, #fff);
    margin: 0 0 8px 0;
    font-size: 28px;
  }

  .subtitle {
    color: var(--accent-orange, #f97316);
    font-size: 14px;
    text-transform: uppercase;
    letter-spacing: 3px;
    margin: 0 0 32px 0;
  }

  .status {
    color: var(--text-muted, #888);
    margin-bottom: 16px;
  }

  .connection-status {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 8px;
    color: var(--text-muted, #888);
    margin-bottom: 24px;
  }

  .status-dot {
    width: 10px;
    height: 10px;
    border-radius: 50%;
  }

  .status-dot.offline {
    background: #ef4444;
  }

  .start-form {
    background: var(--bg-secondary, #1a1a1a);
    border-radius: 12px;
    padding: 24px;
    margin-bottom: 24px;
  }

  .start-form p {
    color: var(--text-secondary, #aaa);
    margin: 0 0 16px 0;
    font-size: 14px;
  }

  .start-form input {
    width: 100%;
    padding: 12px 16px;
    background: var(--bg-primary, #0f0f0f);
    border: 1px solid var(--border-color, #333);
    border-radius: 8px;
    color: var(--text-primary, #fff);
    font-size: 14px;
    margin-bottom: 16px;
    box-sizing: border-box;
  }

  .start-form input:focus {
    outline: none;
    border-color: var(--accent-orange, #f97316);
  }

  .button-row {
    display: flex;
    gap: 12px;
  }

  button {
    flex: 1;
    padding: 12px 20px;
    border-radius: 8px;
    font-weight: 600;
    font-size: 14px;
    cursor: pointer;
    transition: all 0.2s;
  }

  button.primary {
    background: var(--accent-orange, #f97316);
    color: white;
    border: none;
  }

  button.primary:hover:not(:disabled) {
    background: #ea580c;
  }

  button.secondary {
    background: transparent;
    color: var(--text-secondary, #aaa);
    border: 1px solid var(--border-color, #333);
  }

  button.secondary:hover:not(:disabled) {
    background: var(--bg-secondary, #1a1a1a);
  }

  button:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }

  .error {
    color: #ef4444 !important;
    margin-top: 12px !important;
  }

  .hint {
    color: var(--text-muted, #666);
    font-size: 12px;
  }

  .spinner {
    width: 32px;
    height: 32px;
    border: 3px solid var(--bg-secondary, #1a1a1a);
    border-top-color: var(--accent-orange, #f97316);
    border-radius: 50%;
    animation: spin 1s linear infinite;
    margin: 0 auto;
  }

  @keyframes spin {
    to { transform: rotate(360deg); }
  }
</style>
