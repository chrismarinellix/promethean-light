<script>
  import { activeSection, favorites, stats, tags, clusters, daemonConnected, databaseInfo, apiKeysStatus, chatMessages, savedFolders } from '../stores.js';
  import { removeFavorite, searchQuery, searchResults, loadSavedFolders, saveToFolder, createFolder, removeFromFolder } from '../stores.js';
  import { getStats, getTags, checkDaemon, startDaemon, getDatabaseInfo, getApiKeysStatus, getClusters, rebuildClusters } from '../api.js';
  import { onMount } from 'svelte';
  import UnlockModal from './UnlockModal.svelte';
  import AddNoteModal from './AddNoteModal.svelte';
  import FileUploadModal from './FileUploadModal.svelte';

  // Debug logger
  function debugLog(context, message, data = null) {
    const timestamp = new Date().toISOString().split('T')[1].slice(0, 12);
    const prefix = `[PL ${timestamp}] [Sidebar:${context}]`;
    if (data !== null) {
      console.log(prefix, message, data);
    } else {
      console.log(prefix, message);
    }
  }

  // Format ISO timestamp as relative time (e.g., "2 hours ago", "Dec 4, 10:30")
  function formatRelativeTime(isoString) {
    if (!isoString) return '';
    const date = new Date(isoString);
    const now = new Date();
    const diffMs = now - date;
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffMins < 1) return 'just now';
    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffHours < 24) return `${diffHours}h ago`;
    if (diffDays < 7) return `${diffDays}d ago`;

    // For older dates, show formatted date
    const options = { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' };
    return date.toLocaleDateString('en-US', options);
  }

  let expandedSections = {
    favorites: true,
    sources: true,
    clusters: true,
    saved: false
  };

  let expandedFolders = {};
  let showNewFolderInput = false;
  let newFolderName = '';

  function toggleSection(section) {
    expandedSections[section] = !expandedSections[section];
  }

  function toggleFolder(folderId) {
    expandedFolders[folderId] = !expandedFolders[folderId];
    expandedFolders = expandedFolders; // Trigger reactivity
  }

  function handleAddFolder() {
    if (newFolderName.trim()) {
      createFolder(newFolderName.trim());
      newFolderName = '';
      showNewFolderInput = false;
    }
  }

  function handleFolderKeydown(e) {
    if (e.key === 'Enter') {
      handleAddFolder();
    } else if (e.key === 'Escape') {
      showNewFolderInput = false;
      newFolderName = '';
    }
  }

  function loadSavedItem(item) {
    // Load a saved item into the chat
    chatMessages.set([
      {
        role: 'user',
        content: item.query || 'Saved item',
        timestamp: item.savedAt
      },
      {
        role: 'assistant',
        content: item.response || item.content || 'No content',
        sources: item.sources || [],
        timestamp: item.savedAt
      }
    ]);
    activeSection.set('chat');
  }

  function getTotalSavedCount(folders) {
    return folders.reduce((sum, f) => sum + (f.items?.length || 0), 0);
  }

  // Click on data source to get a summary
  async function exploreDataSource(sourceType) {
    let query = '';
    switch (sourceType) {
      case 'emails':
        query = 'Give me a summary of my recent emails. What are the key themes, who are the main people communicating, and what urgent items need attention?';
        break;
      case 'documents':
        query = 'What documents have been indexed? Give me a summary of the key topics and types of documents in my collection.';
        break;
      case 'notes':
        query = 'What notes and pastes have I saved? Summarize the main topics and any actionable items from my notes.';
        break;
      default:
        return;
    }

    // Add to chat and trigger search
    chatMessages.set([
      {
        role: 'user',
        content: query,
        timestamp: new Date().toISOString()
      }
    ]);

    activeSection.set('chat');

    // Make the API call
    try {
      const response = await fetch('http://127.0.0.1:8000/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: query })
      });

      if (response.ok) {
        const data = await response.json();
        chatMessages.update(msgs => [...msgs, {
          role: 'assistant',
          content: data.response || data.message || 'No response',
          sources: data.sources || [],
          timestamp: new Date().toISOString()
        }]);
      } else {
        chatMessages.update(msgs => [...msgs, {
          role: 'assistant',
          content: 'Error: Could not fetch summary.',
          isError: true,
          timestamp: new Date().toISOString()
        }]);
      }
    } catch (e) {
      chatMessages.update(msgs => [...msgs, {
        role: 'assistant',
        content: 'Error: Could not connect to daemon.',
        isError: true,
        timestamp: new Date().toISOString()
      }]);
    }
  }

  // Click on a cluster to explore its documents
  async function exploreCluster(cluster) {
    const query = `Tell me about documents in the "${cluster.label}" topic. What are the key themes, who are the main people involved, and what are the important details?`;

    // Add to chat and trigger search
    chatMessages.set([
      {
        role: 'user',
        content: query,
        timestamp: new Date().toISOString()
      }
    ]);

    activeSection.set('chat');

    // Make the API call
    try {
      const response = await fetch('http://127.0.0.1:8000/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: query })
      });

      if (response.ok) {
        const data = await response.json();
        chatMessages.update(msgs => [...msgs, {
          role: 'assistant',
          content: data.response || data.message || 'No response',
          sources: data.sources || [],
          timestamp: new Date().toISOString()
        }]);
      } else {
        chatMessages.update(msgs => [...msgs, {
          role: 'assistant',
          content: 'Error: Could not fetch cluster summary.',
          isError: true,
          timestamp: new Date().toISOString()
        }]);
      }
    } catch (e) {
      chatMessages.update(msgs => [...msgs, {
        role: 'assistant',
        content: 'Error: Could not connect to daemon.',
        isError: true,
        timestamp: new Date().toISOString()
      }]);
    }
  }

  async function loadFavoriteSearch(fav) {
    // Set the search stores (for backwards compatibility)
    searchQuery.set(fav.query);
    searchResults.set(fav.results);

    // Also load into chat as a saved conversation
    if (fav.results && fav.results.length > 0) {
      // Clear existing chat and add the saved conversation
      chatMessages.set([
        {
          role: 'user',
          content: fav.query,
          timestamp: fav.savedAt
        },
        {
          role: 'assistant',
          content: fav.results[0].content || fav.results[0].text || 'No content',
          sources: fav.results.slice(1),
          timestamp: fav.savedAt
        }
      ]);
    }

    // Switch to chat view if not already there
    activeSection.set('chat');
  }

  let isConnecting = false;
  let isRestarting = false;
  let connectionError = '';
  let showUnlockModal = false;
  let isStartingDaemon = false;
  let unlockError = '';
  let showAddNoteModal = false;
  let showFileUploadModal = false;
  let isRebuildingClusters = false;

  async function handleRebuildClusters() {
    isRebuildingClusters = true;
    try {
      debugLog('CLUSTERS', 'Rebuilding clusters...');
      const result = await rebuildClusters(10, 5);
      debugLog('CLUSTERS', 'Rebuild result:', result);

      // Refresh clusters after rebuild
      const clustersData = await getClusters();
      if (clustersData) {
        clusters.set(clustersData);
      }
    } catch (e) {
      debugLog('CLUSTERS', `Rebuild failed: ${e.message}`);
      console.error('Failed to rebuild clusters:', e);
    } finally {
      isRebuildingClusters = false;
    }
  }

  async function refreshStats() {
    connectionError = '';
    debugLog('REFRESH', 'Starting daemon check and stats refresh...');
    const startTime = performance.now();

    try {
      debugLog('DAEMON', 'Checking daemon connection...');
      const connected = await checkDaemon();
      debugLog('DAEMON', `Connection check result: ${connected}`);
      daemonConnected.set(connected);

      if (connected) {
        debugLog('FETCH', 'Fetching all data in parallel...');
        const [statsData, tagsData, dbInfo, apiStatus, clustersData] = await Promise.all([
          getStats().catch(e => { debugLog('ERROR', `Stats fetch failed: ${e.message}`); return null; }),
          getTags().catch(e => { debugLog('ERROR', `Tags fetch failed: ${e.message}`); return []; }),
          getDatabaseInfo().catch(e => { debugLog('ERROR', `DB info fetch failed: ${e.message}`); return null; }),
          getApiKeysStatus().catch(e => { debugLog('ERROR', `API keys fetch failed: ${e.message}`); return null; }),
          getClusters().catch(e => { debugLog('ERROR', `Clusters fetch failed: ${e.message}`); return []; })
        ]);

        const elapsed = Math.round(performance.now() - startTime);
        debugLog('FETCH', `All data fetched in ${elapsed}ms`, {
          stats: !!statsData,
          tags: tagsData?.length || 0,
          clusters: clustersData?.length || 0,
          dbInfo: !!dbInfo,
          apiStatus: apiStatus
        });

        if (statsData) stats.set(statsData);
        if (tagsData) tags.set(tagsData);
        if (clustersData) clusters.set(clustersData);
        if (dbInfo) databaseInfo.set(dbInfo);
        if (apiStatus) {
          debugLog('API_STATUS', 'Setting API keys status:', apiStatus);
          apiKeysStatus.set(apiStatus);
        } else {
          debugLog('API_STATUS', 'WARNING: No API status received, keeping default');
        }
      } else {
        debugLog('DAEMON', 'Daemon not running or not responding');
        connectionError = 'Daemon not running';
      }
    } catch (e) {
      const elapsed = Math.round(performance.now() - startTime);
      debugLog('ERROR', `Connection failed after ${elapsed}ms: ${e.message}`);
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

  async function handleRestartDaemon() {
    isRestarting = true;
    connectionError = '';

    try {
      debugLog('RESTART', 'Stopping daemon...');

      // Call the stop endpoint
      await fetch('http://127.0.0.1:8000/admin/stop', {
        method: 'POST'
      }).catch(() => {}); // Ignore error if daemon already stopped

      // Wait for daemon to stop
      await new Promise(r => setTimeout(r, 1500));

      // Mark as disconnected
      daemonConnected.set(false);

      // Show unlock modal to restart
      showUnlockModal = true;
      debugLog('RESTART', 'Daemon stopped, showing unlock modal');
    } catch (e) {
      debugLog('RESTART', `Error: ${e.message}`);
      connectionError = e.message || 'Failed to restart daemon';
    } finally {
      isRestarting = false;
    }
  }

  async function handleUnlock(event) {
    const { passphrase } = event.detail;
    isStartingDaemon = true;
    unlockError = '';

    try {
      debugLog('UNLOCK', 'Starting daemon...');
      const result = await startDaemon(passphrase);
      debugLog('UNLOCK', 'Daemon start result:', result);

      // Poll for connection with retries (daemon may take time to load ML models)
      let connected = false;
      const maxRetries = 15;  // 15 retries * 2 seconds = 30 seconds max wait

      for (let i = 1; i <= maxRetries; i++) {
        debugLog('UNLOCK', `Connection attempt ${i}/${maxRetries}...`);
        unlockError = `Starting daemon... (attempt ${i}/${maxRetries})`;

        await new Promise(r => setTimeout(r, 2000));
        await refreshStats();

        if ($daemonConnected) {
          connected = true;
          debugLog('UNLOCK', 'Connected successfully!');
          break;
        }
      }

      if (connected) {
        showUnlockModal = false;
        unlockError = '';
      } else {
        unlockError = 'Daemon started but not responding. Check the daemon terminal window for errors, then click Retry Connection.';
      }
    } catch (e) {
      debugLog('UNLOCK', `Failed to start daemon: ${e.message}`);
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

  function handleFileUploaded(event) {
    // Refresh stats to show updated document count
    refreshStats();
    showFileUploadModal = false;
  }

  onMount(async () => {
    debugLog('INIT', 'Checking daemon connection on mount...');

    // First check if daemon is already running
    await refreshStats();

    if ($daemonConnected) {
      debugLog('INIT', 'Daemon already connected!');
    } else {
      debugLog('INIT', 'Daemon not connected, showing unlock modal');
      showUnlockModal = true;
    }

    loadSavedFolders();

    // Periodic refresh every 30 seconds
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
      <div class="control-buttons">
        <button class="connect-btn" on:click={handleConnect} disabled={isConnecting} title="Refresh data">
          {#if isConnecting}
            <span class="spinner"></span>
          {:else}
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M21.5 2v6h-6M2.5 22v-6h6M2 11.5a10 10 0 0 1 18.8-4.3M22 12.5a10 10 0 0 1-18.8 4.2"/>
            </svg>
          {/if}
        </button>
        {#if $daemonConnected}
          <button class="restart-btn" on:click={handleRestartDaemon} disabled={isRestarting} title="Restart daemon">
            {#if isRestarting}
              <span class="spinner"></span>
            {:else}
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M18.36 6.64A9 9 0 1 1 5.64 6.64"/>
                <line x1="12" y1="2" x2="12" y2="12"/>
              </svg>
            {/if}
          </button>
        {/if}
      </div>
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
      <div class="database-path" title={$databaseInfo.database_path}>
        {$databaseInfo.database_path ? $databaseInfo.database_path.replace(/\\/g, '/').split('/').slice(-2).join('/') : ''}
      </div>
    {/if}
    {#if $daemonConnected}
      <div class="api-status">
        <span class="api-label">LLM:</span>
        {#if $apiKeysStatus.anthropic}
          <span class="api-badge active" title="Anthropic Claude (primary)">Claude</span>
        {:else if $apiKeysStatus.openai}
          <span class="api-badge active" title="OpenAI GPT-4o (fallback)">OpenAI</span>
        {:else}
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
    <button
      class="nav-item add-doc"
      on:click={() => showFileUploadModal = true}
      disabled={!$daemonConnected}
    >
      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
        <polyline points="17 8 12 3 7 8"/>
        <line x1="12" y1="3" x2="12" y2="15"/>
      </svg>
      Add Document
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

  {#if $daemonConnected && $stats.last_email_at}
    <div class="last-sync-banner" title="Last email ingested: {$stats.last_email_at}">
      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <rect x="2" y="4" width="20" height="16" rx="2"/>
        <path d="m22 7-8.97 5.7a1.94 1.94 0 0 1-2.06 0L2 7"/>
      </svg>
      <span class="sync-text">Last email: <strong>{formatRelativeTime($stats.last_email_at)}</strong></span>
    </div>
  {/if}

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
          <button
            class="source-item clickable"
            on:click={() => exploreDataSource('emails')}
            disabled={!$daemonConnected || ($stats.sources?.emails || 0) === 0}
            title="Click for email summary"
          >
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="var(--accent-blue)" stroke-width="2">
              <rect x="2" y="4" width="20" height="16" rx="2"/>
              <path d="m22 7-8.97 5.7a1.94 1.94 0 0 1-2.06 0L2 7"/>
            </svg>
            <span>Outlook Emails</span>
            <span class="source-count">{$stats.sources?.emails || 0}</span>
            <svg class="explore-icon" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="m9 18 6-6-6-6"/>
            </svg>
          </button>
          {#if $stats.last_email_at}
            <div class="last-sync-info" title="Last email ingested: {$stats.last_email_at}">
              <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <circle cx="12" cy="12" r="10"/>
                <polyline points="12 6 12 12 16 14"/>
              </svg>
              <span>Last: {formatRelativeTime($stats.last_email_at)}</span>
            </div>
          {/if}
          <button
            class="source-item clickable"
            on:click={() => exploreDataSource('documents')}
            disabled={!$daemonConnected || ($stats.sources?.documents || 0) === 0}
            title="Click for document summary"
          >
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="var(--accent-green)" stroke-width="2">
              <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
              <path d="M14 2v6h6"/>
            </svg>
            <span>Documents</span>
            <span class="source-count">{$stats.sources?.documents || 0}</span>
            <svg class="explore-icon" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="m9 18 6-6-6-6"/>
            </svg>
          </button>
          <button
            class="source-item clickable"
            on:click={() => exploreDataSource('notes')}
            disabled={!$daemonConnected || ($stats.sources?.notes || 0) === 0}
            title="Click for notes summary"
          >
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="var(--accent-purple)" stroke-width="2">
              <path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"/>
              <path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"/>
            </svg>
            <span>Notes & Pastes</span>
            <span class="source-count">{$stats.sources?.notes || 0}</span>
            <svg class="explore-icon" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="m9 18 6-6-6-6"/>
            </svg>
          </button>
        </div>
      {/if}
    </div>

    <!-- Clusters Section -->
    <div class="section">
      <button class="section-header" on:click={() => toggleSection('clusters')}>
        <svg class="chevron" class:expanded={expandedSections.clusters} width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="m9 18 6-6-6-6"/>
        </svg>
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <circle cx="12" cy="12" r="3"/>
          <circle cx="19" cy="5" r="2"/>
          <circle cx="5" cy="5" r="2"/>
          <circle cx="19" cy="19" r="2"/>
          <circle cx="5" cy="19" r="2"/>
          <line x1="12" y1="9" x2="12" y2="3"/>
          <line x1="9.5" y1="14" x2="5" y2="17"/>
          <line x1="14.5" y1="14" x2="19" y2="17"/>
        </svg>
        <span>Topics</span>
        <span class="count">{$clusters.length}</span>
      </button>
      {#if expandedSections.clusters}
        <div class="section-content clusters">
          {#if $clusters.length === 0}
            <div class="empty-clusters">
              <p class="empty-hint">No topic clusters yet</p>
              <button
                class="rebuild-clusters-btn"
                on:click={handleRebuildClusters}
                disabled={!$daemonConnected || isRebuildingClusters}
                title="Generate topic clusters from your documents"
              >
                {#if isRebuildingClusters}
                  <span class="spinner"></span>
                  Analyzing...
                {:else}
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M21.5 2v6h-6M2.5 22v-6h6M2 11.5a10 10 0 0 1 18.8-4.3M22 12.5a10 10 0 0 1-18.8 4.2"/>
                  </svg>
                  Generate Topics
                {/if}
              </button>
              <p class="cluster-help">Requires 10+ documents</p>
            </div>
          {:else}
            {#each $clusters.slice(0, 10) as cluster}
              <button
                class="cluster-item"
                on:click={() => exploreCluster(cluster)}
                title="{cluster.document_count} documents"
              >
                <span class="cluster-label">{cluster.label}</span>
                <span class="cluster-count">{cluster.document_count}</span>
              </button>
            {/each}
            {#if $clusters.length > 10}
              <div class="more-hint">+{$clusters.length - 10} more topics</div>
            {/if}
          {/if}
        </div>
      {/if}
    </div>

    <!-- Saved Folders Section -->
    <div class="section">
      <button class="section-header" on:click={() => toggleSection('saved')}>
        <svg class="chevron" class:expanded={expandedSections.saved} width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="m9 18 6-6-6-6"/>
        </svg>
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M4 20h16a2 2 0 0 0 2-2V8a2 2 0 0 0-2-2h-7.93a2 2 0 0 1-1.66-.9l-.82-1.2A2 2 0 0 0 7.93 3H4a2 2 0 0 0-2 2v13c0 1.1.9 2 2 2Z"/>
        </svg>
        <span>Folders</span>
        <span class="count">{getTotalSavedCount($savedFolders)}</span>
      </button>
      {#if expandedSections.saved}
        <div class="section-content folders">
          {#each $savedFolders as folder}
            <div class="folder">
              <button class="folder-header" on:click={() => toggleFolder(folder.id)}>
                <svg class="chevron small" class:expanded={expandedFolders[folder.id]} width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="m9 18 6-6-6-6"/>
                </svg>
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="var(--accent-orange)" stroke-width="2">
                  <path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"/>
                </svg>
                <span class="folder-name">{folder.name}</span>
                <span class="folder-count">{folder.items?.length || 0}</span>
              </button>
              {#if expandedFolders[folder.id] && folder.items?.length > 0}
                <div class="folder-items">
                  {#each folder.items as item}
                    <div class="saved-item">
                      <button class="saved-query" on:click={() => loadSavedItem(item)} title={item.query}>
                        {item.query || 'Untitled'}
                      </button>
                      <button class="remove-btn" on:click={() => removeFromFolder(folder.id, item.id)} title="Remove">
                        <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                          <path d="M18 6L6 18M6 6l12 12"/>
                        </svg>
                      </button>
                    </div>
                  {/each}
                </div>
              {/if}
            </div>
          {/each}

          {#if showNewFolderInput}
            <div class="new-folder-input">
              <input
                type="text"
                bind:value={newFolderName}
                on:keydown={handleFolderKeydown}
                placeholder="Folder name..."
                autofocus
              />
              <button class="add-folder-btn" on:click={handleAddFolder}>
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M5 12h14"/>
                  <path d="M12 5v14"/>
                </svg>
              </button>
            </div>
          {:else}
            <button class="add-folder-link" on:click={() => showNewFolderInput = true}>
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M12 5v14M5 12h14"/>
              </svg>
              New folder
            </button>
          {/if}
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
  on:retry={async () => {
    debugLog('UNLOCK', 'Manual retry requested...');
    unlockError = 'Checking connection...';
    await refreshStats();
    if ($daemonConnected) {
      showUnlockModal = false;
      unlockError = '';
    } else {
      unlockError = 'Still not connected. Check daemon terminal for errors.';
    }
  }}
  on:close={() => { showUnlockModal = false; unlockError = ''; }}
/>

<AddNoteModal
  visible={showAddNoteModal}
  on:added={handleNoteAdded}
  on:close={() => showAddNoteModal = false}
/>

<FileUploadModal
  visible={showFileUploadModal}
  on:uploaded={handleFileUploaded}
  on:close={() => showFileUploadModal = false}
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
    font-size: 18px;
    color: var(--text-primary);
  }

  .subtitle {
    font-size: 13px;
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

  .control-buttons {
    display: flex;
    gap: 4px;
  }

  .connect-btn {
    display: flex;
    align-items: center;
    justify-content: center;
    background: var(--bg-tertiary);
    border: 1px solid var(--border-color);
    color: var(--text-secondary);
    padding: 6px 8px;
    border-radius: var(--radius);
    cursor: pointer;
    transition: all 0.2s;
  }

  .connect-btn:hover:not(:disabled) {
    background: var(--accent-orange);
    border-color: var(--accent-orange);
    color: white;
  }

  .restart-btn {
    display: flex;
    align-items: center;
    justify-content: center;
    background: var(--bg-tertiary);
    border: 1px solid var(--border-color);
    color: var(--text-secondary);
    padding: 6px 8px;
    border-radius: var(--radius);
    cursor: pointer;
    transition: all 0.2s;
  }

  .restart-btn:hover:not(:disabled) {
    background: var(--accent-red);
    border-color: var(--accent-red);
    color: white;
  }

  .restart-btn:disabled,
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

  .database-path {
    margin-top: 4px;
    padding: 4px 10px;
    font-size: 10px;
    color: var(--text-muted);
    font-family: 'Consolas', 'Monaco', monospace;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
    cursor: help;
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
    padding: 12px 14px;
    background: transparent;
    border: none;
    border-radius: var(--radius);
    color: var(--text-secondary);
    font-size: 15px;
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

  .nav-item.add-doc {
    border: 1px dashed var(--border-color);
    margin-top: 4px;
  }

  .nav-item.add-doc:hover:not(:disabled) {
    border-color: var(--accent-blue);
    color: var(--accent-blue);
    background: rgba(59, 130, 246, 0.1);
  }

  .nav-item.add-doc:disabled {
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
    font-size: 22px;
    font-weight: 700;
    color: var(--text-primary);
  }

  .stat-label {
    font-size: 12px;
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
    padding: 10px 12px;
    background: transparent;
    border: none;
    border-radius: var(--radius);
    color: var(--text-secondary);
    font-size: 14px;
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
    font-size: 14px;
    color: var(--text-secondary);
    width: 100%;
    background: transparent;
    border: none;
    text-align: left;
    font-family: inherit;
  }

  .source-item.clickable {
    padding: 8px 10px;
    border-radius: var(--radius);
    cursor: pointer;
    transition: all 0.2s;
  }

  .source-item.clickable:hover:not(:disabled) {
    background: var(--bg-tertiary);
    color: var(--text-primary);
  }

  .source-item.clickable:hover:not(:disabled) .explore-icon {
    opacity: 1;
    color: var(--accent-orange);
  }

  .source-item.clickable:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }

  .source-item span:first-of-type {
    flex: 1;
  }

  .explore-icon {
    opacity: 0;
    transition: opacity 0.2s;
    margin-left: auto;
  }

  .source-count {
    background: var(--bg-tertiary);
    padding: 2px 8px;
    border-radius: 10px;
    font-size: 11px;
    font-weight: 600;
    color: var(--text-muted);
  }

  .last-sync-info {
    display: flex;
    align-items: center;
    gap: 6px;
    padding: 4px 10px 4px 24px;
    font-size: 11px;
    color: var(--text-muted);
  }

  .last-sync-info svg {
    opacity: 0.6;
  }

  .last-sync-info span {
    opacity: 0.8;
  }

  .last-sync-banner {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 8px 12px;
    margin: 0 10px 10px 10px;
    background: rgba(59, 130, 246, 0.1);
    border: 1px solid rgba(59, 130, 246, 0.3);
    border-radius: 6px;
    font-size: 12px;
    color: var(--accent-blue);
  }

  .last-sync-banner svg {
    flex-shrink: 0;
  }

  .last-sync-banner .sync-text {
    color: var(--text-secondary);
  }

  .last-sync-banner .sync-text strong {
    color: var(--accent-blue);
  }

  /* Cluster Styles */
  .section-content.clusters {
    display: flex;
    flex-direction: column;
    gap: 4px;
  }

  .cluster-item {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 10px 14px;
    background: transparent;
    border: 1px solid var(--border-color);
    border-radius: var(--radius);
    font-size: 14px;
    color: var(--text-secondary);
    cursor: pointer;
    transition: all 0.2s;
    text-align: left;
    font-family: inherit;
  }

  .cluster-item:hover {
    background: var(--bg-tertiary);
    border-color: var(--accent-orange);
    color: var(--text-primary);
  }

  .cluster-label {
    flex: 1;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }

  .cluster-count {
    background: rgba(249, 115, 22, 0.15);
    color: var(--accent-orange);
    padding: 2px 8px;
    border-radius: 10px;
    font-size: 10px;
    font-weight: 600;
    margin-left: 8px;
  }

  .more-hint {
    text-align: center;
    font-size: 11px;
    color: var(--text-muted);
    padding: 4px 0;
    font-style: italic;
  }

  /* Folder Styles */
  .folders {
    padding: 4px 8px 8px 24px;
  }

  .folder {
    margin-bottom: 4px;
  }

  .folder-header {
    display: flex;
    align-items: center;
    gap: 6px;
    width: 100%;
    padding: 6px 8px;
    background: transparent;
    border: none;
    border-radius: var(--radius);
    color: var(--text-secondary);
    font-size: 12px;
    text-align: left;
    cursor: pointer;
    transition: all 0.2s;
  }

  .folder-header:hover {
    background: var(--bg-tertiary);
    color: var(--text-primary);
  }

  .chevron.small {
    width: 12px;
    height: 12px;
  }

  .folder-name {
    flex: 1;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }

  .folder-count {
    background: var(--bg-tertiary);
    padding: 1px 6px;
    border-radius: 8px;
    font-size: 10px;
    color: var(--text-muted);
  }

  .folder-items {
    padding-left: 20px;
    margin-top: 4px;
  }

  .saved-item {
    display: flex;
    align-items: center;
    gap: 4px;
    margin-bottom: 2px;
  }

  .saved-query {
    flex: 1;
    background: transparent;
    border: none;
    color: var(--text-secondary);
    font-size: 11px;
    text-align: left;
    padding: 4px 6px;
    cursor: pointer;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
    border-radius: var(--radius);
    transition: all 0.15s;
  }

  .saved-query:hover {
    background: var(--bg-tertiary);
    color: var(--accent-orange);
  }

  .saved-item .remove-btn {
    background: transparent;
    border: none;
    color: var(--text-muted);
    padding: 2px;
    cursor: pointer;
    opacity: 0;
    transition: all 0.15s;
    flex-shrink: 0;
  }

  .saved-item:hover .remove-btn {
    opacity: 1;
  }

  .saved-item .remove-btn:hover {
    color: var(--accent-red);
  }

  .new-folder-input {
    display: flex;
    align-items: center;
    gap: 6px;
    margin-top: 8px;
  }

  .new-folder-input input {
    flex: 1;
    background: var(--bg-primary);
    border: 1px solid var(--border-color);
    border-radius: var(--radius);
    padding: 6px 10px;
    font-size: 12px;
    color: var(--text-primary);
    outline: none;
  }

  .new-folder-input input:focus {
    border-color: var(--accent-orange);
  }

  .add-folder-btn {
    background: var(--accent-orange);
    border: none;
    border-radius: var(--radius);
    padding: 6px 8px;
    color: white;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .add-folder-btn:hover {
    background: #ea580c;
  }

  .add-folder-link {
    display: flex;
    align-items: center;
    gap: 6px;
    background: transparent;
    border: 1px dashed var(--border-color);
    border-radius: var(--radius);
    padding: 6px 10px;
    font-size: 11px;
    color: var(--text-muted);
    cursor: pointer;
    margin-top: 8px;
    width: 100%;
    transition: all 0.2s;
  }

  .add-folder-link:hover {
    border-color: var(--accent-orange);
    color: var(--accent-orange);
  }

  /* Empty clusters section */
  .empty-clusters {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 8px;
    padding: 8px 0;
  }

  .rebuild-clusters-btn {
    display: flex;
    align-items: center;
    gap: 6px;
    padding: 8px 14px;
    background: var(--accent-orange);
    border: none;
    border-radius: var(--radius);
    color: white;
    font-size: 12px;
    font-weight: 500;
    font-family: inherit;
    cursor: pointer;
    transition: all 0.2s;
  }

  .rebuild-clusters-btn:hover:not(:disabled) {
    background: #ea580c;
  }

  .rebuild-clusters-btn:disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }

  .cluster-help {
    font-size: 10px;
    color: var(--text-muted);
    margin: 0;
  }

</style>
