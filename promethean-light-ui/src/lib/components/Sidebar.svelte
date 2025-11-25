<script>
  import { activeSection, favorites, stats, tags, daemonConnected, databaseInfo, apiKeysStatus } from '../stores.js';
  import { removeFavorite, searchQuery, searchResults } from '../stores.js';
  import { getStats, getTags, checkDaemon, startDaemon, getDatabaseInfo, getApiKeysStatus } from '../api.js';
  import { onMount } from 'svelte';
  import UnlockModal from './UnlockModal.svelte';
  import AddNoteModal from './AddNoteModal.svelte';

  let expandedSections = {
    favorites: true,
    sources: true
  };

  function toggleSection(section) {
    expandedSections[section] = !expandedSections[section];
  }

  async function loadFavoriteSearch(fav) {
    searchQuery.set(fav.query);
    searchResults.set(fav.results);
  }

  let isConnecting = false;
  let connectionError = '';
  let showUnlockModal = false;
  let isStartingDaemon = false;
  let unlockError = '';
  let showAddNoteModal = false;

  async function refreshStats() {
    connectionError = '';
    try {
      console.log('Checking daemon at http://127.0.0.1:8000/...');
      const connected = await checkDaemon();
      console.log('Daemon check result:', connected);
      daemonConnected.set(connected);

      if (connected) {
        console.log('Fetching stats, tags, database info, and API status...');
        const [statsData, tagsData, dbInfo, apiStatus] = await Promise.all([
          getStats(),
          getTags(),
          getDatabaseInfo().catch(() => null),
          getApiKeysStatus().catch(() => null)
        ]);
        console.log('Stats:', statsData);
        console.log('Tags:', tagsData);
        console.log('Database Info:', dbInfo);
        console.log('API Status:', apiStatus);
        stats.set(statsData);
        tags.set(tagsData);
        if (dbInfo) {
          databaseInfo.set(dbInfo);
        }
        if (apiStatus) {
          apiKeysStatus.set(apiStatus);
        }
      } else {
        connectionError = 'Daemon not running';
      }
    } catch (e) {
      console.error('Connection failed:', e);
      connectionError = e.message || 'Connection failed';
      daemonConnected.set(false);
    }
  }

  async function handleConnect() {
    isConnecting = true;
    connectionError = '';
    await refreshStats();
    isConnecting = false;

    // If not connected, show unlock modal
    if (!$daemonConnected) {
      showUnlockModal = true;
    }
  }

  async function handleUnlock(event) {
    const { passphrase } = event.detail;
    isStartingDaemon = true;
    unlockError = '';

    try {
      console.log('Starting daemon...');
      const result = await startDaemon(passphrase);
      console.log('Daemon start result:', result);

      // Wait a bit more then check connection
      await new Promise(r => setTimeout(r, 2000));
      await refreshStats();

      if ($daemonConnected) {
        showUnlockModal = false;
        unlockError = '';
      } else {
        unlockError = 'Daemon started but connection failed. Try again in a few seconds.';
      }
    } catch (e) {
      console.error('Failed to start daemon:', e);
      unlockError = e.message || 'Failed to start daemon';
    } finally {
      isStartingDaemon = false;
    }
  }

  function handleNoteAdded() {
    // Refresh stats to show updated note count
    refreshStats();
    showAddNoteModal = false;
  }

  onMount(() => {
    refreshStats();
    const interval = setInterval(refreshStats, 30000);
    return () => clearInterval(interval);
  });
</script>

<aside class="sidebar">
  <div class="sidebar-header">
    <div class="logo">
      <span class="fire">🔥</span>
      <div class="logo-text">
        <span class="title">Promethean Light</span>
        <span class="subtitle">God Mode</span>
      </div>
    </div>
    <div class="status-row">
      <div class="status" class:connected={$daemonConnected}>
        <span class="status-dot"></span>
        {$daemonConnected ? 'Connected' : 'Disconnected'}
      </div>
      <button class="connect-btn" on:click={handleConnect} disabled={isConnecting}>
        {#if isConnecting}
          <span class="spinner"></span>
        {:else}
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M21 12a9 9 0 0 1-9 9m9-9a9 9 0 0 0-9-9m9 9H3m9 9a9 9 0 0 1-9-9m9 9c1.66 0 3-4.03 3-9s-1.34-9-3-9m0 18c-1.66 0-3-4.03-3-9s1.34-9 3-9"/>
          </svg>
          {$daemonConnected ? 'Refresh' : 'Connect'}
        {/if}
      </button>
    </div>
    {#if connectionError}
      <div class="error-msg">{connectionError}</div>
    {/if}
    {#if $daemonConnected && $databaseInfo.current_database}
      <div class="database-info" title={$databaseInfo.database_path}>
        <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <ellipse cx="12" cy="5" rx="9" ry="3"/>
          <path d="M21 12c0 1.66-4 3-9 3s-9-1.34-9-3"/>
          <path d="M3 5v14c0 1.66 4 3 9 3s9-1.34 9-3V5"/>
        </svg>
        <span class="db-name">{$databaseInfo.current_database}</span>
        {#if $databaseInfo.available_databases.length > 1}
          <span class="db-count">({$databaseInfo.available_databases.length} available)</span>
        {/if}
      </div>
    {/if}
    {#if $daemonConnected}
      <div class="api-status">
        <span class="api-label">LLM:</span>
        {#if $apiKeysStatus.openai}
          <span class="api-badge active" title="OpenAI API key configured">OpenAI</span>
        {/if}
        {#if $apiKeysStatus.anthropic}
          <span class="api-badge active" title="Anthropic API key configured">Claude</span>
        {/if}
        {#if !$apiKeysStatus.openai && !$apiKeysStatus.anthropic}
          <span class="api-badge inactive" title="No API keys configured">None</span>
        {/if}
      </div>
    {/if}
  </div>

  <nav class="nav-sections">
    <button
      class="nav-item"
      class:active={$activeSection === 'chat'}
      on:click={() => activeSection.set('chat')}
    >
      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>
      </svg>
      Ask
    </button>
    <button
      class="nav-item"
      class:active={$activeSection === 'admin'}
      on:click={() => activeSection.set('admin')}
    >
      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <path d="M12.22 2h-.44a2 2 0 0 0-2 2v.18a2 2 0 0 1-1 1.73l-.43.25a2 2 0 0 1-2 0l-.15-.08a2 2 0 0 0-2.73.73l-.22.38a2 2 0 0 0 .73 2.73l.15.1a2 2 0 0 1 1 1.72v.51a2 2 0 0 1-1 1.74l-.15.09a2 2 0 0 0-.73 2.73l.22.38a2 2 0 0 0 2.73.73l.15-.08a2 2 0 0 1 2 0l.43.25a2 2 0 0 1 1 1.73V20a2 2 0 0 0 2 2h.44a2 2 0 0 0 2-2v-.18a2 2 0 0 1 1-1.73l.43-.25a2 2 0 0 1 2 0l.15.08a2 2 0 0 0 2.73-.73l.22-.39a2 2 0 0 0-.73-2.73l-.15-.08a2 2 0 0 1-1-1.74v-.5a2 2 0 0 1 1-1.74l.15-.09a2 2 0 0 0 .73-2.73l-.22-.38a2 2 0 0 0-2.73-.73l-.15.08a2 2 0 0 1-2 0l-.43-.25a2 2 0 0 1-1-1.73V4a2 2 0 0 0-2-2z"/>
        <circle cx="12" cy="12" r="3"/>
      </svg>
      Admin
    </button>
    <button
      class="nav-item add-note"
      on:click={() => showAddNoteModal = true}
      disabled={!$daemonConnected}
    >
      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <path d="M12 5v14M5 12h14"/>
      </svg>
      Add Note
    </button>
  </nav>

  <div class="stats-panel">
    <div class="stat">
      <span class="stat-value">{$stats.total_documents || 0}</span>
      <span class="stat-label">Indexed</span>
    </div>
    <div class="stat">
      <span class="stat-value">{$tags.length || 0}</span>
      <span class="stat-label">Topics</span>
    </div>
  </div>

  <div class="collapsible-sections">
    <!-- Favorites Section -->
    <div class="section">
      <button class="section-header" on:click={() => toggleSection('favorites')}>
        <svg class="chevron" class:expanded={expandedSections.favorites} width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="m9 18 6-6-6-6"/>
        </svg>
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M19 21l-7-5-7 5V5a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2z"/>
        </svg>
        <span>Saved</span>
        <span class="count">{$favorites.length}</span>
      </button>
      {#if expandedSections.favorites}
        <div class="section-content">
          {#if $favorites.length === 0}
            <p class="empty-hint">No saved items yet</p>
          {:else}
            {#each $favorites as fav}
              <div class="favorite-item">
                <button class="favorite-query" on:click={() => loadFavoriteSearch(fav)}>
                  {fav.query}
                </button>
                <button class="remove-btn" on:click={() => removeFavorite(fav.id)} title="Remove">
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M18 6L6 18M6 6l12 12"/>
                  </svg>
                </button>
              </div>
            {/each}
          {/if}
        </div>
      {/if}
    </div>

    <!-- Data Sources Section -->
    <div class="section">
      <button class="section-header" on:click={() => toggleSection('sources')}>
        <svg class="chevron" class:expanded={expandedSections.sources} width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="m9 18 6-6-6-6"/>
        </svg>
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"/>
        </svg>
        <span>Data Sources</span>
      </button>
      {#if expandedSections.sources}
        <div class="section-content sources">
          <div class="source-item">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="var(--accent-blue)" stroke-width="2">
              <rect x="2" y="4" width="20" height="16" rx="2"/>
              <path d="m22 7-8.97 5.7a1.94 1.94 0 0 1-2.06 0L2 7"/>
            </svg>
            <span>Outlook Emails</span>
            <span class="source-count">{$stats.sources?.emails || 0}</span>
          </div>
          <div class="source-item">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="var(--accent-green)" stroke-width="2">
              <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
              <path d="M14 2v6h6"/>
            </svg>
            <span>Documents</span>
            <span class="source-count">{$stats.sources?.documents || 0}</span>
          </div>
          <div class="source-item">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="var(--accent-purple)" stroke-width="2">
              <path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"/>
              <path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"/>
            </svg>
            <span>Notes & Pastes</span>
            <span class="source-count">{$stats.sources?.notes || 0}</span>
          </div>
        </div>
      {/if}
    </div>

  </div>
</aside>

<UnlockModal
  visible={showUnlockModal}
  isStarting={isStartingDaemon}
  error={unlockError}
  on:unlock={handleUnlock}
  on:close={() => { showUnlockModal = false; unlockError = ''; }}
/>

<AddNoteModal
  visible={showAddNoteModal}
  on:added={handleNoteAdded}
  on:close={() => showAddNoteModal = false}
/>

<style>
  .sidebar {
    width: 280px;
    background: var(--bg-secondary);
    border-right: 1px solid var(--border-color);
    display: flex;
    flex-direction: column;
    height: 100vh;
  }

  .sidebar-header {
    padding: 20px 16px;
    border-bottom: 1px solid var(--border-color);
  }

  .logo {
    display: flex;
    align-items: center;
    gap: 12px;
    margin-bottom: 12px;
  }

  .fire {
    font-size: 28px;
  }

  .logo-text {
    display: flex;
    flex-direction: column;
  }

  .title {
    font-weight: 700;
    font-size: 16px;
    color: var(--text-primary);
  }

  .subtitle {
    font-size: 12px;
    color: var(--accent-orange);
    font-weight: 600;
  }

  .status-row {
    display: flex;
    align-items: center;
    justify-content: space-between;
  }

  .status {
    display: flex;
    align-items: center;
    gap: 6px;
    font-size: 12px;
    color: var(--accent-red);
  }

  .status.connected {
    color: var(--accent-green);
  }

  .status-dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background: currentColor;
  }

  .connect-btn {
    display: flex;
    align-items: center;
    gap: 6px;
    background: var(--bg-tertiary);
    border: 1px solid var(--border-color);
    color: var(--text-secondary);
    padding: 5px 10px;
    border-radius: var(--radius);
    font-size: 11px;
    cursor: pointer;
    transition: all 0.2s;
  }

  .connect-btn:hover:not(:disabled) {
    background: var(--accent-orange);
    border-color: var(--accent-orange);
    color: white;
  }

  .connect-btn:disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }

  .spinner {
    width: 12px;
    height: 12px;
    border: 2px solid transparent;
    border-top-color: currentColor;
    border-radius: 50%;
    animation: spin 0.8s linear infinite;
  }

  @keyframes spin {
    to { transform: rotate(360deg); }
  }

  .error-msg {
    margin-top: 8px;
    padding: 6px 10px;
    background: rgba(248, 81, 73, 0.15);
    border: 1px solid var(--accent-red);
    border-radius: var(--radius);
    font-size: 11px;
    color: var(--accent-red);
  }

  .database-info {
    display: flex;
    align-items: center;
    gap: 6px;
    margin-top: 10px;
    padding: 6px 10px;
    background: var(--bg-tertiary);
    border-radius: var(--radius);
    font-size: 11px;
    color: var(--text-secondary);
    cursor: help;
  }

  .database-info .db-name {
    font-weight: 600;
    color: var(--text-primary);
  }

  .database-info .db-count {
    color: var(--text-muted);
  }

  .api-status {
    display: flex;
    align-items: center;
    gap: 6px;
    margin-top: 8px;
    font-size: 11px;
  }

  .api-label {
    color: var(--text-muted);
  }

  .api-badge {
    padding: 2px 8px;
    border-radius: 10px;
    font-size: 10px;
    font-weight: 600;
  }

  .api-badge.active {
    background: rgba(63, 185, 80, 0.2);
    color: var(--accent-green);
  }

  .api-badge.inactive {
    background: rgba(248, 81, 73, 0.15);
    color: var(--accent-red);
  }

  .nav-sections {
    padding: 16px 12px;
    display: flex;
    flex-direction: column;
    gap: 4px;
  }

  .nav-item {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 10px 12px;
    background: transparent;
    border: none;
    border-radius: var(--radius);
    color: var(--text-secondary);
    font-size: 14px;
    text-align: left;
    transition: all 0.2s;
  }

  .nav-item:hover {
    background: var(--bg-tertiary);
    color: var(--text-primary);
  }

  .nav-item.active {
    background: var(--accent-orange-dim);
    color: var(--accent-orange);
  }

  .nav-item.add-note {
    border: 1px dashed var(--border-color);
    margin-top: 8px;
  }

  .nav-item.add-note:hover:not(:disabled) {
    border-color: var(--accent-green);
    color: var(--accent-green);
    background: rgba(63, 185, 80, 0.1);
  }

  .nav-item.add-note:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }

  .stats-panel {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 8px;
    padding: 12px;
    margin: 0 12px;
    background: var(--bg-tertiary);
    border-radius: var(--radius);
  }

  .stat {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 2px;
  }

  .stat-value {
    font-size: 18px;
    font-weight: 700;
    color: var(--text-primary);
  }

  .stat-label {
    font-size: 10px;
    color: var(--text-muted);
    text-transform: uppercase;
  }

  .collapsible-sections {
    flex: 1;
    overflow-y: auto;
    padding: 16px 12px;
  }

  .section {
    margin-bottom: 8px;
  }

  .section-header {
    display: flex;
    align-items: center;
    gap: 8px;
    width: 100%;
    padding: 8px 10px;
    background: transparent;
    border: none;
    border-radius: var(--radius);
    color: var(--text-secondary);
    font-size: 13px;
    text-align: left;
    cursor: pointer;
    transition: all 0.2s;
  }

  .section-header:hover {
    background: var(--bg-tertiary);
    color: var(--text-primary);
  }

  .section-header span:not(.count) {
    flex: 1;
  }

  .count {
    background: var(--bg-tertiary);
    padding: 2px 8px;
    border-radius: 10px;
    font-size: 11px;
  }

  .chevron {
    transition: transform 0.2s;
  }

  .chevron.expanded {
    transform: rotate(90deg);
  }

  .section-content {
    padding: 8px 8px 8px 32px;
  }

  .empty-hint {
    font-size: 12px;
    color: var(--text-muted);
    font-style: italic;
  }

  .favorite-item {
    display: flex;
    align-items: center;
    gap: 6px;
    margin-bottom: 6px;
  }

  .favorite-query {
    flex: 1;
    background: transparent;
    border: none;
    color: var(--text-secondary);
    font-size: 13px;
    text-align: left;
    padding: 4px 0;
    cursor: pointer;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }

  .favorite-query:hover {
    color: var(--accent-orange);
  }

  .remove-btn {
    background: transparent;
    border: none;
    color: var(--text-muted);
    padding: 4px;
    opacity: 0;
    transition: all 0.2s;
  }

  .favorite-item:hover .remove-btn {
    opacity: 1;
  }

  .remove-btn:hover {
    color: var(--accent-red);
  }

  .sources {
    display: flex;
    flex-direction: column;
    gap: 8px;
  }

  .source-item {
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 13px;
    color: var(--text-secondary);
  }

  .source-item span:first-of-type {
    flex: 1;
  }

  .source-count {
    background: var(--bg-tertiary);
    padding: 2px 8px;
    border-radius: 10px;
    font-size: 11px;
    font-weight: 600;
    color: var(--text-muted);
  }

</style>
