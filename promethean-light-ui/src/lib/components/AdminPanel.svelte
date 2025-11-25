<script>
  import { onMount } from 'svelte';
  import { daemonConnected } from '../stores.js';

  let adminInfo = null;
  let loading = true;
  let error = null;
  let lastRefresh = null;

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
</style>
