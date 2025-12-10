<script>
  import { onMount, onDestroy } from 'svelte';
  import { daemonConnected } from '../stores.js';

  let adminInfo = null;
  let previousInfo = null;
  let loading = true;
  let error = null;
  let lastRefresh = null;
  let refreshChanges = null; // Track what changed on refresh

  // Rebuild state
  let rebuildStatus = 'idle'; // 'idle', 'running', 'complete', 'error'
  let rebuildProgress = 0;
  let rebuildStartTime = null;
  let rebuildElapsed = 0;
  let rebuildResult = null;
  let rebuildLogs = [];
  let rebuildPollInterval = null;
  let elapsedInterval = null;

  // Summaries update state
  let summariesStatus = 'idle'; // 'idle', 'updating', 'complete', 'error'
  let summariesMessage = '';

  // Clusters rebuild state
  let clustersStatus = 'idle'; // 'idle', 'running', 'complete', 'error'
  let clustersMessage = '';
  let clustersResult = null;

  async function fetchAdminInfo() {
    loading = true;
    error = null;
    try {
      const response = await fetch('http://127.0.0.1:8000/admin/info');
      if (!response.ok) throw new Error('Failed to fetch admin info');
      adminInfo = await response.json();
      lastRefresh = new Date().toLocaleTimeString();
    } catch (e) {
      error = e.message;
    } finally {
      loading = false;
    }
  }

  onMount(() => {
    if ($daemonConnected) {
      fetchAdminInfo();
    }
  });

  onDestroy(() => {
    if (rebuildPollInterval) clearInterval(rebuildPollInterval);
    if (elapsedInterval) clearInterval(elapsedInterval);
  });

  $: if ($daemonConnected && !adminInfo && !loading) {
    fetchAdminInfo();
  }

  function formatBytes(mb) {
    if (mb < 1) return `${Math.round(mb * 1024)} KB`;
    if (mb < 1024) return `${mb.toFixed(1)} MB`;
    return `${(mb / 1024).toFixed(2)} GB`;
  }

  function getStatusColor(status) {
    return status ? 'var(--accent-green)' : 'var(--accent-red)';
  }

  function getStatusText(status) {
    return status ? 'Ready' : 'Not Ready';
  }

  function formatTime(seconds) {
    if (seconds < 60) return `${Math.round(seconds)}s`;
    const mins = Math.floor(seconds / 60);
    const secs = Math.round(seconds % 60);
    return `${mins}m ${secs}s`;
  }

  function addLog(message, type = 'info') {
    const timestamp = new Date().toLocaleTimeString();
    rebuildLogs = [...rebuildLogs, { timestamp, message, type }];
  }

  async function startRebuild() {
    rebuildStatus = 'running';
    rebuildProgress = 0;
    rebuildStartTime = Date.now();
    rebuildElapsed = 0;
    rebuildResult = null;
    rebuildLogs = [];

    addLog('Starting vector database rebuild...', 'info');
    addLog(`Total chunks in SQLite: ${adminInfo?.database?.documents || '?'} documents`, 'debug');
    addLog(`Current vectors in Qdrant: ${adminInfo?.vectordb?.vectors || 0}`, 'debug');

    try {
      addLog('Sending rebuild request to daemon...', 'info');

      // Start the rebuild (returns immediately now)
      const response = await fetch('http://127.0.0.1:8000/admin/rebuild-vectors', {
        method: 'POST',
      });

      if (!response.ok) {
        const errText = await response.text();
        throw new Error(errText || 'Failed to start rebuild');
      }

      const startResult = await response.json();
      if (!startResult.success) {
        // If already running, just start polling to show progress
        if (startResult.message && startResult.message.includes('already in progress')) {
          addLog('Rebuild already running, showing progress...', 'info');
          // Keep rebuildStatus as 'running' and start polling
        } else {
          addLog(`Could not start: ${startResult.message}`, 'warning');
          rebuildStatus = 'idle';
          return;
        }
      } else {
        addLog('Rebuild started in background...', 'info');
      }

      // Start polling for progress
      rebuildPollInterval = setInterval(async () => {
        try {
          const statusRes = await fetch('http://127.0.0.1:8000/admin/rebuild-vectors/status');
          if (statusRes.ok) {
            const status = await statusRes.json();

            // Update progress from server
            rebuildProgress = status.progress || 0;
            rebuildElapsed = status.elapsed_seconds || 0;

            // Add progress log (only if changed significantly)
            if (status.status === 'running') {
              addLog(`Progress: ${status.indexed}/${status.total_chunks} (${status.progress}%) - ${status.rate_per_second}/sec`, 'progress');
            }

            // Check if complete
            if (status.status === 'complete') {
              clearInterval(rebuildPollInterval);
              rebuildStatus = 'complete';
              rebuildProgress = 100;
              rebuildResult = {
                success: true,
                indexed: status.indexed,
                skipped: status.skipped,
                errors: status.errors,
                error_messages: status.error_messages || [],
                elapsed_seconds: status.elapsed_seconds,
                rate_per_second: status.rate_per_second,
                vector_count: status.vector_count
              };

              addLog(`Rebuild complete!`, 'success');
              addLog(`Indexed: ${status.indexed} chunks`, 'success');
              addLog(`Skipped: ${status.skipped} (too short)`, 'debug');
              addLog(`Errors: ${status.errors}`, status.errors > 0 ? 'error' : 'debug');
              addLog(`Total time: ${status.elapsed_seconds}s`, 'info');
              addLog(`Rate: ${status.rate_per_second} chunks/sec`, 'info');
              addLog(`Final vector count: ${status.vector_count}`, 'success');

              if (status.error_messages && status.error_messages.length > 0) {
                addLog(`Error details:`, 'error');
                status.error_messages.forEach(msg => addLog(`  ${msg}`, 'error'));
              }

              // Refresh admin info
              fetchAdminInfo();
            }

            // Check if error
            if (status.status === 'error') {
              clearInterval(rebuildPollInterval);
              rebuildStatus = 'error';
              addLog(`Error: ${status.message}`, 'error');
            }
          }
        } catch (e) {
          // Ignore polling errors
        }
      }, 1000);  // Poll every 1 second for more responsive UI

    } catch (e) {
      clearInterval(rebuildPollInterval);
      rebuildStatus = 'error';
      addLog(`Error: ${e.message}`, 'error');
    }
  }

  function getRemainingTime() {
    if (rebuildProgress <= 0 || rebuildElapsed <= 0) return '--';
    const rate = rebuildProgress / rebuildElapsed;
    const remaining = (100 - rebuildProgress) / rate;
    return formatTime(remaining);
  }

  async function updateSummaries() {
    summariesStatus = 'updating';
    summariesMessage = 'Refreshing pre-computed summaries...';

    try {
      const response = await fetch('http://127.0.0.1:8000/admin/refresh-summaries', {
        method: 'POST',
      });

      if (!response.ok) {
        throw new Error('Failed to refresh summaries');
      }

      const result = await response.json();
      summariesStatus = 'complete';
      summariesMessage = result.message || 'Summaries refreshed successfully';

      setTimeout(() => {
        summariesStatus = 'idle';
        summariesMessage = '';
      }, 5000);
    } catch (e) {
      summariesStatus = 'error';
      summariesMessage = e.message || 'Failed to refresh summaries';
    }
  }

  async function rebuildClusters() {
    clustersStatus = 'running';
    clustersMessage = 'Generating clusters with HDBSCAN...';
    clustersResult = null;

    try {
      const response = await fetch('http://127.0.0.1:8000/clusters/rebuild?min_cluster_size=10&min_samples=5', {
        method: 'POST',
      });

      if (!response.ok) {
        const errText = await response.text();
        throw new Error(errText || 'Failed to rebuild clusters');
      }

      const result = await response.json();
      clustersStatus = 'complete';
      clustersResult = result;
      clustersMessage = result.message || `Created ${result.clusters} clusters`;

      // Refresh admin info to show new cluster count
      fetchAdminInfo();

      setTimeout(() => {
        clustersStatus = 'idle';
        clustersMessage = '';
      }, 8000);
    } catch (e) {
      clustersStatus = 'error';
      clustersMessage = e.message || 'Failed to rebuild clusters';
    }
  }
</script>

<div class="admin-panel">
  <div class="admin-header">
    <div class="admin-title">
      <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <path d="M12.22 2h-.44a2 2 0 0 0-2 2v.18a2 2 0 0 1-1 1.73l-.43.25a2 2 0 0 1-2 0l-.15-.08a2 2 0 0 0-2.73.73l-.22.38a2 2 0 0 0 .73 2.73l.15.1a2 2 0 0 1 1 1.72v.51a2 2 0 0 1-1 1.74l-.15.09a2 2 0 0 0-.73 2.73l.22.38a2 2 0 0 0 2.73.73l.15-.08a2 2 0 0 1 2 0l.43.25a2 2 0 0 1 1 1.73V20a2 2 0 0 0 2 2h.44a2 2 0 0 0 2-2v-.18a2 2 0 0 1 1-1.73l.43-.25a2 2 0 0 1 2 0l.15.08a2 2 0 0 0 2.73-.73l.22-.39a2 2 0 0 0-.73-2.73l-.15-.08a2 2 0 0 1-1-1.74v-.5a2 2 0 0 1 1-1.74l.15-.09a2 2 0 0 0 .73-2.73l-.22-.38a2 2 0 0 0-2.73-.73l-.15.08a2 2 0 0 1-2 0l-.43-.25a2 2 0 0 1-1-1.73V4a2 2 0 0 0-2-2z"/>
        <circle cx="12" cy="12" r="3"/>
      </svg>
      <span>System Administration</span>
    </div>
    <button class="refresh-btn" on:click={fetchAdminInfo} disabled={loading}>
      {#if loading}
        <span class="spinner"></span>
      {:else}
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M21 12a9 9 0 0 1-9 9m9-9a9 9 0 0 0-9-9m9 9H3m9 9a9 9 0 0 1-9-9m9 9c1.66 0 3-4.03 3-9s-1.34-9-3-9m0 18c-1.66 0-3-4.03-3-9s1.34-9 3-9"/>
        </svg>
        Refresh
      {/if}
    </button>
  </div>

  {#if error}
    <div class="error-box">
      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <circle cx="12" cy="12" r="10"/>
        <line x1="12" y1="8" x2="12" y2="12"/>
        <line x1="12" y1="16" x2="12.01" y2="16"/>
      </svg>
      {error}
    </div>
  {:else if loading && !adminInfo}
    <div class="loading-box">
      <span class="spinner large"></span>
      <span>Loading system information...</span>
    </div>
  {:else if adminInfo}
    <div class="admin-content">
      <!-- Status Overview -->
      <section class="section">
        <h3 class="section-title">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M22 12h-4l-3 9L9 3l-3 9H2"/>
          </svg>
          Component Status
        </h3>
        <div class="status-grid">
          {#each Object.entries(adminInfo.status) as [key, value]}
            <div class="status-item">
              <span class="status-dot" style="background: {getStatusColor(value)}"></span>
              <span class="status-label">{key.replace(/_/g, ' ')}</span>
              <span class="status-value" style="color: {getStatusColor(value)}">{getStatusText(value)}</span>
            </div>
          {/each}
        </div>
      </section>

      <!-- System Architecture -->
      <section class="section architecture-section">
        <h3 class="section-title">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <rect x="3" y="3" width="18" height="18" rx="2"/>
            <path d="M3 9h18"/>
            <path d="M9 21V9"/>
          </svg>
          System Architecture
        </h3>
        <div class="architecture-diagram">
          <div class="arch-flow">
            <!-- Data Sources -->
            <div class="arch-column sources">
              <div class="arch-header">Data Sources</div>
              <div class="arch-box source-box">
                <span class="arch-icon">📧</span>
                <span>Outlook Emails</span>
              </div>
              <div class="arch-box source-box">
                <span class="arch-icon">📄</span>
                <span>Documents</span>
              </div>
              <div class="arch-box source-box">
                <span class="arch-icon">📝</span>
                <span>Notes</span>
              </div>
            </div>

            <div class="arch-arrow">→</div>

            <!-- Storage -->
            <div class="arch-column storage">
              <div class="arch-header">Storage Layer</div>
              <div class="arch-box storage-box">
                <span class="arch-icon">🗄️</span>
                <span>SQLite</span>
                <span class="arch-detail">{adminInfo?.database?.documents || 0} docs</span>
              </div>
              <div class="arch-box storage-box">
                <span class="arch-icon">🔷</span>
                <span>Qdrant</span>
                <span class="arch-detail">{adminInfo?.vectordb?.vectors || 0} vectors</span>
              </div>
            </div>

            <div class="arch-arrow">→</div>

            <!-- Processing -->
            <div class="arch-column processing">
              <div class="arch-header">Query Processing</div>
              <div class="arch-box process-box">
                <span class="arch-icon">🔍</span>
                <span>Semantic Search</span>
                <span class="arch-detail">BGE embeddings</span>
              </div>
              <div class="arch-box process-box">
                <span class="arch-icon">📊</span>
                <span>Context Builder</span>
                <span class="arch-detail">Top 50 chunks</span>
              </div>
            </div>

            <div class="arch-arrow">→</div>

            <!-- LLM -->
            <div class="arch-column llm">
              <div class="arch-header">LLM Response</div>
              <div class="arch-box llm-box">
                <span class="arch-icon">🤖</span>
                <span>GPT-4o</span>
                <span class="arch-detail">Summarizes</span>
              </div>
              <div class="arch-box summary-box">
                <span class="arch-icon">⚡</span>
                <span>Pre-computed</span>
                <span class="arch-detail">0 tokens</span>
              </div>
            </div>
          </div>

          <div class="arch-legend">
            <div class="legend-item">
              <span class="legend-flow">Your Query → Semantic Search → Relevant Chunks → LLM → Answer</span>
            </div>
          </div>
        </div>
      </section>

      <!-- Pre-computed Summaries -->
      <section class="section summaries-section">
        <h3 class="section-title">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M13 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V9z"/>
            <polyline points="13 2 13 9 20 9"/>
          </svg>
          Pre-computed Summaries
        </h3>
        <div class="summaries-info">
          <p class="summaries-description">
            Pre-computed summaries provide instant answers (0 tokens, 0 cost) for common queries like team pay,
            retention bonuses, and Project Sentinel status. Click Update to refresh with latest data.
          </p>
          <div class="summaries-list">
            <span class="summary-tag">Team Pay</span>
            <span class="summary-tag">Australia Staff</span>
            <span class="summary-tag">India Staff</span>
            <span class="summary-tag">Malaysia Staff</span>
            <span class="summary-tag">Retention Bonuses</span>
            <span class="summary-tag">Project Sentinel</span>
          </div>
        </div>

        {#if summariesStatus === 'updating'}
          <div class="summaries-progress">
            <span class="spinner"></span>
            <span>{summariesMessage}</span>
          </div>
        {:else if summariesStatus === 'complete'}
          <div class="summaries-result success">
            <span>✓</span>
            <span>{summariesMessage}</span>
          </div>
        {:else if summariesStatus === 'error'}
          <div class="summaries-result error">
            <span>✗</span>
            <span>{summariesMessage}</span>
          </div>
        {:else}
          <button class="summaries-btn" on:click={updateSummaries}>
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M21.5 2v6h-6M2.5 22v-6h6M2 11.5a10 10 0 0 1 18.8-4.3M22 12.5a10 10 0 0 1-18.8 4.2"/>
            </svg>
            Update Pre-computed Summaries
          </button>
        {/if}
      </section>

      <!-- Database Stats -->
      <section class="section">
        <h3 class="section-title">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <ellipse cx="12" cy="5" rx="9" ry="3"/>
            <path d="M21 12c0 1.66-4 3-9 3s-9-1.34-9-3"/>
            <path d="M3 5v14c0 1.66 4 3 9 3s9-1.34 9-3V5"/>
          </svg>
          Database
        </h3>
        <div class="stats-row">
          <div class="stat-box">
            <span class="stat-value">{adminInfo.database.documents || 0}</span>
            <span class="stat-label">Documents</span>
          </div>
          <div class="stat-box">
            <span class="stat-value">{adminInfo.database.tags || 0}</span>
            <span class="stat-label">Tags</span>
          </div>
          <div class="stat-box">
            <span class="stat-value">{adminInfo.database.clusters || 0}</span>
            <span class="stat-label">Clusters</span>
          </div>
          <div class="stat-box">
            <span class="stat-value">{formatBytes(adminInfo.database.file_size_mb || 0)}</span>
            <span class="stat-label">DB Size</span>
          </div>
        </div>
      </section>

      <!-- Rebuild Clusters -->
      <section class="section clusters-section">
        <h3 class="section-title">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="12" cy="12" r="3"/>
            <circle cx="19" cy="5" r="2"/>
            <circle cx="5" cy="5" r="2"/>
            <circle cx="19" cy="19" r="2"/>
            <circle cx="5" cy="19" r="2"/>
            <line x1="12" y1="9" x2="12" y2="3"/>
            <line x1="14.5" y1="13.5" x2="17.5" y2="17.5"/>
            <line x1="9.5" y1="13.5" x2="6.5" y2="17.5"/>
          </svg>
          ML Clustering
        </h3>
        <div class="clusters-info">
          <p class="clusters-description">
            Groups similar documents using HDBSCAN clustering algorithm.
            Creates topic clusters for easier browsing. Currently: <strong>{adminInfo?.database?.clusters || 0}</strong> clusters.
          </p>
        </div>

        {#if clustersStatus === 'running'}
          <div class="clusters-progress">
            <span class="spinner"></span>
            <span>{clustersMessage}</span>
          </div>
        {:else if clustersStatus === 'complete'}
          <div class="clusters-result success">
            <span>✓</span>
            <span>{clustersMessage}</span>
          </div>
        {:else if clustersStatus === 'error'}
          <div class="clusters-result error">
            <span>✗</span>
            <span>{clustersMessage}</span>
          </div>
        {:else}
          <button class="clusters-btn" on:click={rebuildClusters}>
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <circle cx="12" cy="12" r="3"/>
              <path d="M12 2v4M12 18v4M4.93 4.93l2.83 2.83M16.24 16.24l2.83 2.83M2 12h4M18 12h4M4.93 19.07l2.83-2.83M16.24 7.76l2.83-2.83"/>
            </svg>
            Rebuild Clusters
          </button>
        {/if}
      </section>

      <!-- Vector DB -->
      <section class="section">
        <h3 class="section-title">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <polygon points="12 2 2 7 12 12 22 7 12 2"/>
            <polyline points="2 17 12 22 22 17"/>
            <polyline points="2 12 12 17 22 12"/>
          </svg>
          Vector Database (Qdrant)
        </h3>
        <div class="stats-row">
          <div class="stat-box">
            <span class="stat-value">{adminInfo.vectordb.vectors || 0}</span>
            <span class="stat-label">Vectors</span>
          </div>
          <div class="stat-box">
            <span class="stat-value">{adminInfo.vectordb.dimension || 0}</span>
            <span class="stat-label">Dimensions</span>
          </div>
          <div class="stat-box">
            <span class="stat-value">{formatBytes(adminInfo.vectordb.folder_size_mb || 0)}</span>
            <span class="stat-label">Storage</span>
          </div>
        </div>
      </section>

      <!-- Rebuild Vector DB -->
      <section class="section rebuild-section">
        <h3 class="section-title">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M21.5 2v6h-6M2.5 22v-6h6M2 11.5a10 10 0 0 1 18.8-4.3M22 12.5a10 10 0 0 1-18.8 4.2"/>
          </svg>
          Rebuild Vector Database
        </h3>

        <div class="rebuild-info">
          <p class="rebuild-description">
            Syncs all chunks from SQLite to the Qdrant vector database.
            Use this if search isn't finding documents or if vectors are out of sync.
          </p>

          {#if adminInfo?.vectordb && adminInfo?.database}
            <div class="sync-status" class:synced={adminInfo.vectordb.vectors >= adminInfo.database.documents * 0.95} class:unsynced={adminInfo.vectordb.vectors < adminInfo.database.documents * 0.95}>
              <span class="sync-icon">{adminInfo.vectordb.vectors >= adminInfo.database.documents * 0.95 ? '✓' : '⚠'}</span>
              <span>
                {#if adminInfo.vectordb.vectors >= adminInfo.database.documents * 0.95}
                  Vectors appear to be in sync
                {:else}
                  Vectors may be out of sync ({adminInfo.vectordb.vectors} vectors vs {adminInfo.database.documents} documents)
                {/if}
              </span>
            </div>
          {/if}
        </div>

        {#if rebuildStatus === 'running'}
          <!-- Progress bar and timer -->
          <div class="rebuild-progress">
            <div class="progress-header">
              <span class="progress-label">Rebuilding...</span>
              <span class="progress-percent">{rebuildProgress.toFixed(1)}%</span>
            </div>
            <div class="progress-bar">
              <div class="progress-fill" style="width: {rebuildProgress}%"></div>
            </div>
            <div class="progress-stats">
              <div class="stat">
                <span class="stat-name">Elapsed</span>
                <span class="stat-val">{formatTime(rebuildElapsed)}</span>
              </div>
              <div class="stat">
                <span class="stat-name">Remaining</span>
                <span class="stat-val">{getRemainingTime()}</span>
              </div>
              <div class="stat">
                <span class="stat-name">Rate</span>
                <span class="stat-val">{rebuildElapsed > 0 ? (rebuildProgress / rebuildElapsed * 100).toFixed(1) : '--'}%/s</span>
              </div>
            </div>
          </div>
        {:else}
          <button
            class="rebuild-btn"
            on:click={startRebuild}
            disabled={rebuildStatus === 'running'}
          >
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M21.5 2v6h-6M2.5 22v-6h6M2 11.5a10 10 0 0 1 18.8-4.3M22 12.5a10 10 0 0 1-18.8 4.2"/>
            </svg>
            {rebuildStatus === 'complete' ? 'Rebuild Again' : 'Start Rebuild'}
          </button>
        {/if}

        {#if rebuildResult}
          <div class="rebuild-result" class:success={rebuildResult.success && rebuildResult.errors === 0} class:warning={rebuildResult.success && rebuildResult.errors > 0} class:error={!rebuildResult.success}>
            <div class="result-header">
              {#if rebuildResult.success && rebuildResult.errors === 0}
                <span class="result-icon">✓</span>
                <span>Rebuild Successful</span>
              {:else if rebuildResult.success && rebuildResult.errors > 0}
                <span class="result-icon">⚠</span>
                <span>Rebuild Complete with Warnings</span>
              {:else}
                <span class="result-icon">✗</span>
                <span>Rebuild Failed</span>
              {/if}
            </div>
            <div class="result-stats">
              <span>Indexed: <strong>{rebuildResult.indexed}</strong></span>
              <span>Skipped: <strong>{rebuildResult.skipped}</strong></span>
              <span>Errors: <strong>{rebuildResult.errors}</strong></span>
              <span>Time: <strong>{rebuildResult.elapsed_seconds}s</strong></span>
              <span>Rate: <strong>{rebuildResult.rate_per_second}/s</strong></span>
            </div>
          </div>
        {/if}

        <!-- Debug logs -->
        {#if rebuildLogs.length > 0}
          <div class="rebuild-logs">
            <div class="logs-header">
              <span>Debug Log</span>
              <button class="clear-logs" on:click={() => rebuildLogs = []}>Clear</button>
            </div>
            <div class="logs-content">
              {#each rebuildLogs as log}
                <div class="log-line {log.type}">
                  <span class="log-time">[{log.timestamp}]</span>
                  <span class="log-msg">{log.message}</span>
                </div>
              {/each}
            </div>
          </div>
        {/if}
      </section>

      <!-- Embedder -->
      {#if adminInfo.embedder}
        <section class="section">
          <h3 class="section-title">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"/>
            </svg>
            Embedding Model
          </h3>
          <div class="info-row">
            <span class="info-label">Model:</span>
            <span class="info-value mono">{adminInfo.embedder.model}</span>
          </div>
          <div class="info-row">
            <span class="info-label">Dimension:</span>
            <span class="info-value">{adminInfo.embedder.dimension}</span>
          </div>
        </section>
      {/if}

      <!-- Configuration -->
      <section class="section">
        <h3 class="section-title">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M4 22h14a2 2 0 0 0 2-2V7.5L14.5 2H6a2 2 0 0 0-2 2v4"/>
            <polyline points="14 2 14 8 20 8"/>
            <path d="m3 15 2 2 4-4"/>
          </svg>
          Configuration
        </h3>
        <div class="config-grid">
          <div class="info-row">
            <span class="info-label">API Server:</span>
            <span class="info-value mono">{adminInfo.config.api_host}:{adminInfo.config.api_port}</span>
          </div>
          <div class="info-row">
            <span class="info-label">Chunk Size:</span>
            <span class="info-value">{adminInfo.config.chunk_size} tokens</span>
          </div>
          <div class="info-row">
            <span class="info-label">Chunk Overlap:</span>
            <span class="info-value">{adminInfo.config.chunk_overlap} tokens</span>
          </div>
          <div class="info-row">
            <span class="info-label">Cache TTL:</span>
            <span class="info-value">{adminInfo.config.cache_ttl_seconds}s</span>
          </div>
          <div class="info-row">
            <span class="info-label">Semantic Threshold:</span>
            <span class="info-value">{adminInfo.config.semantic_threshold}</span>
          </div>
          <div class="info-row">
            <span class="info-label">Hybrid Weights:</span>
            <span class="info-value">Vector {adminInfo.config.hybrid_vector_weight} / BM25 {adminInfo.config.hybrid_bm25_weight}</span>
          </div>
        </div>
      </section>

      <!-- Paths -->
      <section class="section">
        <h3 class="section-title">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"/>
          </svg>
          File Paths
        </h3>
        <div class="paths-list">
          {#each Object.entries(adminInfo.paths) as [key, value]}
            <div class="path-row">
              <span class="path-label">{key.replace(/_/g, ' ')}:</span>
              <span class="path-value" title={value}>{value}</span>
            </div>
          {/each}
        </div>
      </section>

      <!-- System Info -->
      <section class="section">
        <h3 class="section-title">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <rect x="2" y="3" width="20" height="14" rx="2" ry="2"/>
            <line x1="8" y1="21" x2="16" y2="21"/>
            <line x1="12" y1="17" x2="12" y2="21"/>
          </svg>
          System
        </h3>
        <div class="info-row">
          <span class="info-label">Platform:</span>
          <span class="info-value">{adminInfo.system.platform} {adminInfo.system.platform_release}</span>
        </div>
        <div class="info-row">
          <span class="info-label">Architecture:</span>
          <span class="info-value">{adminInfo.system.architecture}</span>
        </div>
        <div class="info-row">
          <span class="info-label">Python:</span>
          <span class="info-value mono">{adminInfo.system.python_version.split(' ')[0]}</span>
        </div>
      </section>

      <!-- Available Databases -->
      {#if adminInfo.available_databases && adminInfo.available_databases.length > 0}
        <section class="section">
          <h3 class="section-title">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M4 7V4h16v3"/>
              <path d="M9 20h6"/>
              <path d="M12 4v16"/>
            </svg>
            Available Databases
          </h3>
          <div class="db-list">
            {#each adminInfo.available_databases as db}
              <span class="db-badge" class:active={db === 'default'}>{db}</span>
            {/each}
          </div>
        </section>
      {/if}

      <div class="footer">
        Last updated: {lastRefresh || 'Never'}
      </div>
    </div>
  {/if}
</div>

<style>
  .admin-panel {
    height: 100%;
    display: flex;
    flex-direction: column;
    background: var(--bg-primary);
    font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
  }

  .admin-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 16px 20px;
    background: var(--bg-secondary);
    border-bottom: 1px solid var(--border-color);
  }

  .admin-title {
    display: flex;
    align-items: center;
    gap: 10px;
    font-size: 15px;
    font-weight: 600;
    color: var(--text-primary);
  }

  .admin-title svg {
    color: var(--accent-orange);
  }

  .refresh-btn {
    display: flex;
    align-items: center;
    gap: 6px;
    background: var(--bg-tertiary);
    border: 1px solid var(--border-color);
    color: var(--text-secondary);
    padding: 6px 12px;
    border-radius: 4px;
    font-size: 12px;
    cursor: pointer;
    font-family: inherit;
  }

  .refresh-btn:hover:not(:disabled) {
    background: var(--accent-orange);
    border-color: var(--accent-orange);
    color: white;
  }

  .refresh-btn:disabled {
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

  .spinner.large {
    width: 24px;
    height: 24px;
  }

  @keyframes spin {
    to { transform: rotate(360deg); }
  }

  .admin-content {
    flex: 1;
    overflow-y: auto;
    padding: 20px;
  }

  .error-box {
    display: flex;
    align-items: center;
    gap: 10px;
    margin: 20px;
    padding: 16px;
    background: rgba(248, 81, 73, 0.15);
    border: 1px solid var(--accent-red);
    border-radius: 6px;
    color: var(--accent-red);
    font-size: 13px;
  }

  .loading-box {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 12px;
    padding: 60px 20px;
    color: var(--text-muted);
    font-size: 13px;
  }

  .section {
    background: var(--bg-secondary);
    border: 1px solid var(--border-color);
    border-radius: 8px;
    padding: 16px;
    margin-bottom: 16px;
  }

  .section-title {
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 13px;
    font-weight: 600;
    color: var(--text-primary);
    margin: 0 0 14px 0;
    padding-bottom: 10px;
    border-bottom: 1px solid var(--border-color);
  }

  .section-title svg {
    color: var(--accent-orange);
  }

  .status-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
    gap: 10px;
  }

  .status-item {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 8px 12px;
    background: var(--bg-tertiary);
    border-radius: 4px;
    font-size: 12px;
  }

  .status-dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
  }

  .status-label {
    flex: 1;
    color: var(--text-secondary);
    text-transform: capitalize;
  }

  .status-value {
    font-weight: 600;
  }

  .stats-row {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
    gap: 12px;
  }

  .stat-box {
    display: flex;
    flex-direction: column;
    align-items: center;
    padding: 14px;
    background: var(--bg-tertiary);
    border-radius: 6px;
  }

  .stat-value {
    font-size: 20px;
    font-weight: 700;
    color: var(--text-primary);
  }

  .stat-label {
    font-size: 11px;
    color: var(--text-muted);
    text-transform: uppercase;
    margin-top: 4px;
  }

  .info-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 8px 0;
    border-bottom: 1px solid var(--border-color);
    font-size: 12px;
  }

  .info-row:last-child {
    border-bottom: none;
  }

  .info-label {
    color: var(--text-secondary);
  }

  .info-value {
    color: var(--text-primary);
    font-weight: 500;
  }

  .info-value.mono {
    font-family: 'Consolas', 'Monaco', monospace;
    font-size: 11px;
  }

  .config-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
    gap: 0 20px;
  }

  .paths-list {
    display: flex;
    flex-direction: column;
    gap: 8px;
  }

  .path-row {
    display: flex;
    flex-direction: column;
    gap: 2px;
    padding: 8px;
    background: var(--bg-tertiary);
    border-radius: 4px;
  }

  .path-label {
    font-size: 11px;
    color: var(--text-muted);
    text-transform: capitalize;
  }

  .path-value {
    font-size: 11px;
    color: var(--text-secondary);
    font-family: 'Consolas', 'Monaco', monospace;
    word-break: break-all;
  }

  .db-list {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
  }

  .db-badge {
    padding: 6px 12px;
    background: var(--bg-tertiary);
    border: 1px solid var(--border-color);
    border-radius: 4px;
    font-size: 12px;
    color: var(--text-secondary);
  }

  .db-badge.active {
    background: var(--accent-orange-dim);
    border-color: var(--accent-orange);
    color: var(--accent-orange);
    font-weight: 600;
  }

  .footer {
    padding: 12px 0;
    text-align: center;
    font-size: 11px;
    color: var(--text-muted);
  }

  /* Rebuild Section Styles */
  .rebuild-section {
    border-color: var(--accent-orange);
  }

  .rebuild-info {
    margin-bottom: 16px;
  }

  .rebuild-description {
    font-size: 12px;
    color: var(--text-secondary);
    margin: 0 0 12px 0;
    line-height: 1.5;
  }

  .sync-status {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 10px 14px;
    border-radius: 4px;
    font-size: 12px;
  }

  .sync-status.synced {
    background: rgba(63, 185, 80, 0.15);
    border: 1px solid var(--accent-green);
    color: var(--accent-green);
  }

  .sync-status.unsynced {
    background: rgba(255, 166, 87, 0.15);
    border: 1px solid var(--accent-orange);
    color: var(--accent-orange);
  }

  .sync-icon {
    font-size: 14px;
    font-weight: bold;
  }

  .rebuild-btn {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 8px;
    width: 100%;
    padding: 12px 20px;
    background: var(--accent-orange);
    border: none;
    border-radius: 6px;
    color: white;
    font-size: 13px;
    font-weight: 600;
    font-family: inherit;
    cursor: pointer;
    transition: background 0.2s;
  }

  .rebuild-btn:hover:not(:disabled) {
    background: #e5a040;
  }

  .rebuild-btn:disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }

  .rebuild-progress {
    background: var(--bg-tertiary);
    border-radius: 6px;
    padding: 16px;
    margin-bottom: 12px;
  }

  .progress-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 10px;
  }

  .progress-label {
    font-size: 12px;
    color: var(--text-secondary);
  }

  .progress-percent {
    font-size: 14px;
    font-weight: 700;
    color: var(--accent-orange);
  }

  .progress-bar {
    height: 8px;
    background: var(--bg-primary);
    border-radius: 4px;
    overflow: hidden;
    margin-bottom: 12px;
  }

  .progress-fill {
    height: 100%;
    background: linear-gradient(90deg, var(--accent-orange), #ffc107);
    border-radius: 4px;
    transition: width 0.3s ease;
  }

  .progress-stats {
    display: flex;
    justify-content: space-between;
    gap: 12px;
  }

  .progress-stats .stat {
    display: flex;
    flex-direction: column;
    align-items: center;
    flex: 1;
  }

  .progress-stats .stat-name {
    font-size: 10px;
    color: var(--text-muted);
    text-transform: uppercase;
  }

  .progress-stats .stat-val {
    font-size: 13px;
    font-weight: 600;
    color: var(--text-primary);
  }

  .rebuild-result {
    padding: 14px;
    border-radius: 6px;
    margin-top: 12px;
  }

  .rebuild-result.success {
    background: rgba(63, 185, 80, 0.15);
    border: 1px solid var(--accent-green);
  }

  .rebuild-result.warning {
    background: rgba(255, 166, 87, 0.15);
    border: 1px solid var(--accent-orange);
  }

  .rebuild-result.error {
    background: rgba(248, 81, 73, 0.15);
    border: 1px solid var(--accent-red);
  }

  .result-header {
    display: flex;
    align-items: center;
    gap: 8px;
    margin-bottom: 10px;
    font-size: 13px;
    font-weight: 600;
  }

  .rebuild-result.success .result-header {
    color: var(--accent-green);
  }

  .rebuild-result.warning .result-header {
    color: var(--accent-orange);
  }

  .rebuild-result.error .result-header {
    color: var(--accent-red);
  }

  .result-icon {
    font-size: 16px;
  }

  .result-stats {
    display: flex;
    flex-wrap: wrap;
    gap: 12px 20px;
    font-size: 11px;
    color: var(--text-secondary);
  }

  .result-stats strong {
    color: var(--text-primary);
  }

  .rebuild-logs {
    margin-top: 16px;
    background: var(--bg-tertiary);
    border-radius: 6px;
    overflow: hidden;
  }

  .logs-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 10px 14px;
    background: var(--bg-primary);
    border-bottom: 1px solid var(--border-color);
    font-size: 11px;
    color: var(--text-secondary);
    text-transform: uppercase;
    font-weight: 600;
  }

  .clear-logs {
    background: none;
    border: none;
    color: var(--text-muted);
    font-size: 10px;
    cursor: pointer;
    padding: 2px 6px;
    border-radius: 3px;
    font-family: inherit;
  }

  .clear-logs:hover {
    background: var(--bg-secondary);
    color: var(--text-primary);
  }

  .logs-content {
    max-height: 200px;
    overflow-y: auto;
    padding: 8px;
    font-family: 'Consolas', 'Monaco', monospace;
  }

  .log-line {
    display: flex;
    gap: 8px;
    padding: 3px 6px;
    font-size: 11px;
    border-radius: 2px;
  }

  .log-line:nth-child(odd) {
    background: var(--bg-primary);
  }

  .log-time {
    color: var(--text-muted);
    flex-shrink: 0;
  }

  .log-msg {
    color: var(--text-secondary);
    word-break: break-all;
  }

  .log-line.info .log-msg {
    color: var(--text-primary);
  }

  .log-line.debug .log-msg {
    color: var(--text-muted);
  }

  .log-line.progress .log-msg {
    color: var(--accent-blue);
  }

  .log-line.success .log-msg {
    color: var(--accent-green);
  }

  .log-line.error .log-msg {
    color: var(--accent-red);
  }

  .log-line.warning .log-msg {
    color: var(--accent-orange);
  }

  /* Architecture Diagram Styles */
  .architecture-section {
    border-color: var(--accent-blue);
  }

  .architecture-diagram {
    padding: 12px;
    background: var(--bg-tertiary);
    border-radius: 8px;
  }

  .arch-flow {
    display: flex;
    align-items: flex-start;
    justify-content: space-between;
    gap: 8px;
    overflow-x: auto;
    padding-bottom: 12px;
  }

  .arch-column {
    display: flex;
    flex-direction: column;
    gap: 8px;
    min-width: 110px;
    flex: 1;
  }

  .arch-header {
    font-size: 10px;
    font-weight: 600;
    text-transform: uppercase;
    color: var(--text-muted);
    text-align: center;
    padding-bottom: 6px;
    border-bottom: 1px solid var(--border-color);
  }

  .arch-box {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 2px;
    padding: 10px 8px;
    border-radius: 6px;
    font-size: 11px;
    text-align: center;
    border: 1px solid var(--border-color);
  }

  .arch-icon {
    font-size: 18px;
    margin-bottom: 2px;
  }

  .arch-detail {
    font-size: 9px;
    color: var(--text-muted);
  }

  .source-box {
    background: rgba(59, 130, 246, 0.1);
    border-color: rgba(59, 130, 246, 0.3);
    color: #60a5fa;
  }

  .storage-box {
    background: rgba(139, 92, 246, 0.1);
    border-color: rgba(139, 92, 246, 0.3);
    color: #a78bfa;
  }

  .process-box {
    background: rgba(34, 197, 94, 0.1);
    border-color: rgba(34, 197, 94, 0.3);
    color: #4ade80;
  }

  .llm-box {
    background: rgba(249, 115, 22, 0.1);
    border-color: rgba(249, 115, 22, 0.3);
    color: #fb923c;
  }

  .summary-box {
    background: rgba(236, 72, 153, 0.1);
    border-color: rgba(236, 72, 153, 0.3);
    color: #f472b6;
  }

  .arch-arrow {
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 20px;
    color: var(--text-muted);
    padding-top: 60px;
    font-weight: bold;
  }

  .arch-legend {
    margin-top: 12px;
    padding-top: 12px;
    border-top: 1px solid var(--border-color);
    text-align: center;
  }

  .legend-flow {
    font-size: 11px;
    color: var(--text-secondary);
    font-family: 'Consolas', 'Monaco', monospace;
    background: var(--bg-primary);
    padding: 6px 12px;
    border-radius: 4px;
  }

  /* Summaries Section Styles */
  .summaries-section {
    border-color: var(--accent-purple);
  }

  .summaries-info {
    margin-bottom: 16px;
  }

  .summaries-description {
    font-size: 12px;
    color: var(--text-secondary);
    margin: 0 0 12px 0;
    line-height: 1.5;
  }

  .summaries-list {
    display: flex;
    flex-wrap: wrap;
    gap: 6px;
  }

  .summary-tag {
    display: inline-flex;
    align-items: center;
    padding: 4px 10px;
    background: rgba(139, 92, 246, 0.15);
    border: 1px solid rgba(139, 92, 246, 0.3);
    border-radius: 12px;
    font-size: 11px;
    color: #a78bfa;
  }

  .summaries-btn {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 8px;
    width: 100%;
    padding: 12px 20px;
    background: var(--accent-purple);
    border: none;
    border-radius: 6px;
    color: white;
    font-size: 13px;
    font-weight: 600;
    font-family: inherit;
    cursor: pointer;
    transition: background 0.2s;
  }

  .summaries-btn:hover {
    background: #7c3aed;
  }

  .summaries-progress {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 10px;
    padding: 14px;
    background: var(--bg-tertiary);
    border-radius: 6px;
    font-size: 12px;
    color: var(--text-secondary);
  }

  .summaries-result {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 8px;
    padding: 14px;
    border-radius: 6px;
    font-size: 13px;
    font-weight: 500;
  }

  .summaries-result.success {
    background: rgba(63, 185, 80, 0.15);
    border: 1px solid var(--accent-green);
    color: var(--accent-green);
  }

  .summaries-result.error {
    background: rgba(248, 81, 73, 0.15);
    border: 1px solid var(--accent-red);
    color: var(--accent-red);
  }

  /* Clusters Section Styles */
  .clusters-section {
    border-color: var(--accent-green);
  }

  .clusters-info {
    margin-bottom: 16px;
  }

  .clusters-description {
    font-size: 12px;
    color: var(--text-secondary);
    margin: 0;
    line-height: 1.5;
  }

  .clusters-btn {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 8px;
    width: 100%;
    padding: 12px 20px;
    background: var(--accent-green);
    border: none;
    border-radius: 6px;
    color: white;
    font-size: 13px;
    font-weight: 600;
    font-family: inherit;
    cursor: pointer;
    transition: background 0.2s;
  }

  .clusters-btn:hover {
    background: #2da44e;
  }

  .clusters-progress {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 10px;
    padding: 14px;
    background: var(--bg-tertiary);
    border-radius: 6px;
    font-size: 12px;
    color: var(--text-secondary);
  }

  .clusters-result {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 8px;
    padding: 14px;
    border-radius: 6px;
    font-size: 13px;
    font-weight: 500;
  }

  .clusters-result.success {
    background: rgba(63, 185, 80, 0.15);
    border: 1px solid var(--accent-green);
    color: var(--accent-green);
  }

  .clusters-result.error {
    background: rgba(248, 81, 73, 0.15);
    border: 1px solid var(--accent-red);
    color: var(--accent-red);
  }
</style>
