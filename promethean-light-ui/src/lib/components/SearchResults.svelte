<script>
  import { searchResults, searchQuery, isSearching } from '../stores.js';
  import { saveFavorite } from '../stores.js';

  let viewMode = 'cards'; // 'cards' or 'table'
  let expandedCards = new Set();
  let saveMessage = '';

  function getSourceIcon(source) {
    if (source.includes('@') || source.toLowerCase().includes('email')) return 'email';
    if (source.includes('.pdf')) return 'pdf';
    if (source.includes('.xlsx') || source.includes('.csv')) return 'spreadsheet';
    if (source.includes('.docx') || source.includes('.doc')) return 'doc';
    return 'file';
  }

  function formatDate(dateStr) {
    if (!dateStr) return '';
    const date = new Date(dateStr);
    return date.toLocaleDateString('en-AU', {
      day: 'numeric',
      month: 'short',
      year: 'numeric'
    });
  }

  function truncateText(text, maxLen = 200) {
    if (!text || text.length <= maxLen) return text;
    return text.substring(0, maxLen) + '...';
  }

  function handleSaveFavorite() {
    if ($searchQuery && $searchResults.length > 0) {
      saveFavorite($searchQuery, $searchResults);
      saveMessage = 'Search saved!';
      setTimeout(() => saveMessage = '', 2000);
    }
  }

  function getScoreColor(score) {
    if (score >= 0.8) return 'var(--accent-green)';
    if (score >= 0.6) return 'var(--accent-yellow)';
    return 'var(--accent-orange)';
  }

  function getScoreLabel(score) {
    if (score >= 0.8) return 'Excellent';
    if (score >= 0.6) return 'Good';
    if (score >= 0.4) return 'Fair';
    return 'Partial';
  }

  function toggleExpand(id) {
    if (expandedCards.has(id)) {
      expandedCards.delete(id);
    } else {
      expandedCards.add(id);
    }
    expandedCards = expandedCards; // trigger reactivity
  }

  function copyToClipboard(text) {
    navigator.clipboard.writeText(text);
  }

  function getSourceType(source) {
    const icon = getSourceIcon(source);
    const types = {
      'email': 'Email',
      'pdf': 'PDF',
      'spreadsheet': 'Spreadsheet',
      'doc': 'Document',
      'file': 'File'
    };
    return types[icon] || 'File';
  }

  $: sortedResults = [...$searchResults].sort((a, b) => b.score - a.score);
</script>

<div class="results-container">
  {#if $isSearching}
    <div class="loading">
      <div class="loading-spinner"></div>
      <span>Searching your knowledge base...</span>
    </div>
  {:else if $searchResults.length > 0}
    <div class="results-header">
      <div class="results-info">
        <span class="results-count">{$searchResults.length} results</span>
        <span class="results-query">for "{$searchQuery}"</span>
      </div>
      <div class="results-actions">
        <div class="view-toggle">
          <button
            class:active={viewMode === 'cards'}
            on:click={() => viewMode = 'cards'}
            title="Card view"
          >
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <rect x="3" y="3" width="7" height="7"/>
              <rect x="14" y="3" width="7" height="7"/>
              <rect x="3" y="14" width="7" height="7"/>
              <rect x="14" y="14" width="7" height="7"/>
            </svg>
          </button>
          <button
            class:active={viewMode === 'table'}
            on:click={() => viewMode = 'table'}
            title="Table view"
          >
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M3 3h18v18H3zM3 9h18M3 15h18M9 3v18"/>
            </svg>
          </button>
        </div>
        <button class="save-btn" on:click={handleSaveFavorite} title="Save this search">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M19 21l-7-5-7 5V5a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2z"/>
          </svg>
          {saveMessage || 'Save'}
        </button>
      </div>
    </div>

    {#if viewMode === 'table'}
      <div class="table-container">
        <table class="results-table">
          <thead>
            <tr>
              <th class="th-rank">#</th>
              <th class="th-score">Match</th>
              <th class="th-type">Type</th>
              <th class="th-source">Source</th>
              <th class="th-content">Content</th>
              <th class="th-date">Date</th>
              <th class="th-actions">Actions</th>
            </tr>
          </thead>
          <tbody>
            {#each sortedResults as result, i}
              <tr>
                <td class="td-rank">{i + 1}</td>
                <td class="td-score">
                  <span class="score-badge" style="background: {getScoreColor(result.score)}20; color: {getScoreColor(result.score)}">
                    {Math.round(result.score * 100)}%
                  </span>
                </td>
                <td class="td-type">
                  <span class="type-badge" class:email={getSourceIcon(result.source) === 'email'}>
                    {getSourceType(result.source)}
                  </span>
                </td>
                <td class="td-source" title={result.source}>
                  {result.source.split(/[/\\]/).pop()}
                </td>
                <td class="td-content">
                  <div class="content-preview" class:expanded={expandedCards.has(result.id)}>
                    {expandedCards.has(result.id) ? result.text : truncateText(result.text, 150)}
                  </div>
                  {#if result.text.length > 150}
                    <button class="expand-btn" on:click={() => toggleExpand(result.id)}>
                      {expandedCards.has(result.id) ? 'Less' : 'More'}
                    </button>
                  {/if}
                </td>
                <td class="td-date">{formatDate(result.created_at)}</td>
                <td class="td-actions">
                  <button class="icon-btn" on:click={() => copyToClipboard(result.text)} title="Copy">
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                      <rect x="9" y="9" width="13" height="13" rx="2"/>
                      <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/>
                    </svg>
                  </button>
                </td>
              </tr>
            {/each}
          </tbody>
        </table>
      </div>
    {:else}
      <div class="results-list">
        {#each sortedResults as result, i}
          <div class="result-card" class:expanded={expandedCards.has(result.id)}>
            <div class="card-rank">#{i + 1}</div>
            <div class="card-content">
              <div class="result-header">
                <div class="source-info">
                  <div class="source-badge" class:email={getSourceIcon(result.source) === 'email'}>
                    {#if getSourceIcon(result.source) === 'email'}
                      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <rect x="2" y="4" width="20" height="16" rx="2"/>
                        <path d="m22 7-8.97 5.7a1.94 1.94 0 0 1-2.06 0L2 7"/>
                      </svg>
                    {:else if getSourceIcon(result.source) === 'pdf'}
                      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
                        <path d="M14 2v6h6"/>
                        <path d="M10 9v6M14 9v6"/>
                      </svg>
                    {:else if getSourceIcon(result.source) === 'spreadsheet'}
                      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
                        <path d="M14 2v6h6"/>
                        <path d="M8 13h2M8 17h2M12 13h4M12 17h4"/>
                      </svg>
                    {:else}
                      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
                        <path d="M14 2v6h6"/>
                      </svg>
                    {/if}
                    <span class="source-name" title={result.source}>{result.source.split(/[/\\]/).pop()}</span>
                  </div>
                </div>
                <div class="result-meta">
                  <span class="score-pill" style="background: {getScoreColor(result.score)}20; color: {getScoreColor(result.score)}; border-color: {getScoreColor(result.score)}40">
                    <span class="score-value">{Math.round(result.score * 100)}%</span>
                    <span class="score-label">{getScoreLabel(result.score)}</span>
                  </span>
                  {#if result.created_at}
                    <span class="date">{formatDate(result.created_at)}</span>
                  {/if}
                </div>
              </div>

              <div class="result-text" class:expanded={expandedCards.has(result.id)}>
                {expandedCards.has(result.id) ? result.text : truncateText(result.text, 250)}
              </div>

              <div class="card-actions">
                {#if result.text.length > 250}
                  <button class="action-btn" on:click={() => toggleExpand(result.id)}>
                    {#if expandedCards.has(result.id)}
                      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="m18 15-6-6-6 6"/>
                      </svg>
                      Show less
                    {:else}
                      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="m6 9 6 6 6-6"/>
                      </svg>
                      Show more
                    {/if}
                  </button>
                {/if}
                <button class="action-btn" on:click={() => copyToClipboard(result.text)}>
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <rect x="9" y="9" width="13" height="13" rx="2"/>
                    <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/>
                  </svg>
                  Copy
                </button>
              </div>
            </div>
          </div>
        {/each}
      </div>
    {/if}
  {:else if $searchQuery}
    <div class="no-results">
      <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="var(--text-muted)" stroke-width="1.5">
        <circle cx="11" cy="11" r="8"/>
        <path d="m21 21-4.35-4.35"/>
        <path d="M8 8l6 6M14 8l-6 6"/>
      </svg>
      <p>No results found for "{$searchQuery}"</p>
      <span>Try different keywords or check your data sources</span>
    </div>
  {:else}
    <div class="empty-state">
      <div class="fire-icon">🔥</div>
      <h3>Welcome to God Mode</h3>
      <p>Search across all your indexed data - emails, documents, notes, and more.</p>
      <div class="quick-tips">
        <div class="tip">
          <span class="tip-icon">💡</span>
          <span>Try: "latest contract with Acme Corp"</span>
        </div>
        <div class="tip">
          <span class="tip-icon">📧</span>
          <span>Try: "emails about budget approval"</span>
        </div>
        <div class="tip">
          <span class="tip-icon">📊</span>
          <span>Try: "salary review spreadsheet"</span>
        </div>
      </div>
    </div>
  {/if}
</div>

<style>
  .results-container {
    flex: 1;
    overflow-y: auto;
    padding: 16px 0;
  }

  .loading {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 12px;
    padding: 40px;
    color: var(--text-secondary);
  }

  .loading-spinner {
    width: 32px;
    height: 32px;
    border: 3px solid var(--bg-tertiary);
    border-top-color: var(--accent-orange);
    border-radius: 50%;
    animation: spin 0.8s linear infinite;
  }

  @keyframes spin {
    to { transform: rotate(360deg); }
  }

  /* Header */
  .results-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;
    padding: 0 4px;
  }

  .results-info {
    display: flex;
    align-items: baseline;
    gap: 8px;
  }

  .results-count {
    font-size: 18px;
    font-weight: 600;
    color: var(--text-primary);
  }

  .results-query {
    font-size: 14px;
    color: var(--text-muted);
  }

  .results-actions {
    display: flex;
    align-items: center;
    gap: 12px;
  }

  .view-toggle {
    display: flex;
    background: var(--bg-secondary);
    border-radius: var(--radius);
    padding: 2px;
    border: 1px solid var(--border-color);
  }

  .view-toggle button {
    background: transparent;
    border: none;
    padding: 6px 10px;
    border-radius: calc(var(--radius) - 2px);
    color: var(--text-muted);
    cursor: pointer;
    transition: all 0.2s;
  }

  .view-toggle button:hover {
    color: var(--text-primary);
  }

  .view-toggle button.active {
    background: var(--accent-orange);
    color: white;
  }

  .save-btn {
    display: flex;
    align-items: center;
    gap: 6px;
    background: var(--bg-secondary);
    border: 1px solid var(--border-color);
    color: var(--text-primary);
    padding: 6px 12px;
    border-radius: var(--radius);
    font-size: 13px;
    transition: all 0.2s;
    cursor: pointer;
  }

  .save-btn:hover {
    background: var(--bg-hover);
    border-color: var(--accent-orange);
    color: var(--accent-orange);
  }

  /* Table View */
  .table-container {
    overflow-x: auto;
    border: 1px solid var(--border-color);
    border-radius: var(--radius);
  }

  .results-table {
    width: 100%;
    border-collapse: collapse;
    font-size: 13px;
  }

  .results-table th {
    background: var(--bg-secondary);
    padding: 12px 16px;
    text-align: left;
    font-weight: 600;
    color: var(--text-secondary);
    border-bottom: 1px solid var(--border-color);
    white-space: nowrap;
  }

  .results-table td {
    padding: 12px 16px;
    border-bottom: 1px solid var(--border-color);
    vertical-align: top;
  }

  .results-table tr:last-child td {
    border-bottom: none;
  }

  .results-table tr:hover {
    background: var(--bg-secondary);
  }

  .th-rank { width: 40px; }
  .th-score { width: 80px; }
  .th-type { width: 100px; }
  .th-source { width: 150px; }
  .th-content { min-width: 300px; }
  .th-date { width: 100px; }
  .th-actions { width: 60px; }

  .td-rank {
    color: var(--text-muted);
    font-weight: 600;
  }

  .score-badge {
    display: inline-block;
    padding: 4px 8px;
    border-radius: 12px;
    font-weight: 600;
    font-size: 12px;
  }

  .type-badge {
    display: inline-block;
    padding: 4px 8px;
    background: var(--bg-tertiary);
    border-radius: 4px;
    font-size: 11px;
    color: var(--text-secondary);
  }

  .type-badge.email {
    background: rgba(88, 166, 255, 0.15);
    color: var(--accent-blue);
  }

  .td-source {
    max-width: 150px;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
    color: var(--text-secondary);
  }

  .content-preview {
    color: var(--text-primary);
    line-height: 1.5;
  }

  .content-preview.expanded {
    white-space: pre-wrap;
  }

  .expand-btn {
    background: none;
    border: none;
    color: var(--accent-orange);
    font-size: 12px;
    cursor: pointer;
    padding: 4px 0;
  }

  .expand-btn:hover {
    text-decoration: underline;
  }

  .td-date {
    color: var(--text-muted);
    white-space: nowrap;
  }

  .icon-btn {
    background: var(--bg-tertiary);
    border: none;
    padding: 6px;
    border-radius: 4px;
    color: var(--text-secondary);
    cursor: pointer;
    transition: all 0.2s;
  }

  .icon-btn:hover {
    background: var(--accent-orange);
    color: white;
  }

  /* Card View */
  .results-list {
    display: flex;
    flex-direction: column;
    gap: 12px;
  }

  .result-card {
    display: flex;
    background: var(--bg-secondary);
    border: 1px solid var(--border-color);
    border-radius: var(--radius-lg);
    overflow: hidden;
    transition: all 0.2s;
  }

  .result-card:hover {
    border-color: var(--accent-orange-dim);
    box-shadow: 0 4px 12px rgba(249, 115, 22, 0.1);
  }

  .card-rank {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 48px;
    background: var(--bg-tertiary);
    color: var(--text-muted);
    font-weight: 700;
    font-size: 14px;
    flex-shrink: 0;
  }

  .card-content {
    flex: 1;
    padding: 16px;
    min-width: 0;
  }

  .result-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: 12px;
    gap: 12px;
    flex-wrap: wrap;
  }

  .source-info {
    display: flex;
    align-items: center;
    gap: 8px;
  }

  .source-badge {
    display: flex;
    align-items: center;
    gap: 6px;
    background: var(--bg-tertiary);
    padding: 6px 12px;
    border-radius: 20px;
    font-size: 12px;
    color: var(--text-secondary);
  }

  .source-badge.email {
    background: rgba(88, 166, 255, 0.15);
    color: var(--accent-blue);
  }

  .source-name {
    max-width: 200px;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }

  .result-meta {
    display: flex;
    align-items: center;
    gap: 12px;
  }

  .score-pill {
    display: flex;
    align-items: center;
    gap: 6px;
    padding: 4px 10px;
    border-radius: 20px;
    font-size: 12px;
    border: 1px solid;
  }

  .score-value {
    font-weight: 700;
  }

  .score-label {
    font-weight: 500;
    opacity: 0.9;
  }

  .date {
    color: var(--text-muted);
    font-size: 12px;
  }

  .result-text {
    font-size: 14px;
    line-height: 1.7;
    color: var(--text-secondary);
    white-space: pre-wrap;
    word-break: break-word;
  }

  .result-text.expanded {
    background: var(--bg-tertiary);
    padding: 12px;
    border-radius: var(--radius);
    margin-top: 8px;
  }

  .card-actions {
    display: flex;
    gap: 8px;
    margin-top: 12px;
    padding-top: 12px;
    border-top: 1px solid var(--border-color);
  }

  .action-btn {
    display: flex;
    align-items: center;
    gap: 4px;
    background: transparent;
    border: 1px solid var(--border-color);
    padding: 6px 12px;
    border-radius: var(--radius);
    font-size: 12px;
    color: var(--text-secondary);
    cursor: pointer;
    transition: all 0.2s;
  }

  .action-btn:hover {
    background: var(--bg-tertiary);
    border-color: var(--accent-orange);
    color: var(--accent-orange);
  }

  /* Empty/No Results */
  .no-results {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 12px;
    padding: 60px 20px;
    text-align: center;
  }

  .no-results p {
    color: var(--text-primary);
    font-size: 16px;
  }

  .no-results span {
    color: var(--text-muted);
    font-size: 14px;
  }

  .empty-state {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 16px;
    padding: 60px 20px;
    text-align: center;
  }

  .fire-icon {
    font-size: 48px;
  }

  .empty-state h3 {
    color: var(--text-primary);
    font-size: 20px;
  }

  .empty-state p {
    color: var(--text-secondary);
    max-width: 400px;
  }

  .quick-tips {
    display: flex;
    flex-direction: column;
    gap: 8px;
    margin-top: 16px;
  }

  .tip {
    display: flex;
    align-items: center;
    gap: 8px;
    background: var(--bg-secondary);
    padding: 10px 16px;
    border-radius: var(--radius);
    font-size: 14px;
    color: var(--text-secondary);
  }

  .tip-icon {
    font-size: 16px;
  }
</style>
