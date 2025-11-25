<script>
  import { searchQuery, searchResults, isSearching } from '../stores.js';
  import { searchDocuments } from '../api.js';

  let inputValue = '';

  async function handleSearch() {
    if (!inputValue.trim()) return;

    searchQuery.set(inputValue);
    isSearching.set(true);

    try {
      const results = await searchDocuments(inputValue, 20);
      searchResults.set(results);
    } catch (e) {
      console.error('Search failed:', e);
      searchResults.set([]);
    } finally {
      isSearching.set(false);
    }
  }

  function handleKeydown(e) {
    if (e.key === 'Enter') {
      handleSearch();
    }
  }
</script>

<div class="search-bar">
  <div class="search-icon">
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
      <circle cx="11" cy="11" r="8"/>
      <path d="m21 21-4.35-4.35"/>
    </svg>
  </div>
  <input
    type="text"
    bind:value={inputValue}
    on:keydown={handleKeydown}
    placeholder="Search your knowledge base... (contracts, emails, projects)"
    class="search-input"
  />
  <button class="search-btn" on:click={handleSearch} disabled={$isSearching}>
    {#if $isSearching}
      <span class="spinner"></span>
    {:else}
      Search
    {/if}
  </button>
  <div class="shortcut-hint">Press Enter to search</div>
</div>

<style>
  .search-bar {
    display: flex;
    align-items: center;
    gap: 12px;
    background: var(--bg-secondary);
    border: 1px solid var(--border-color);
    border-radius: var(--radius-lg);
    padding: 8px 16px;
    position: relative;
  }

  .search-icon {
    color: var(--text-muted);
    flex-shrink: 0;
  }

  .search-input {
    flex: 1;
    background: transparent;
    border: none;
    color: var(--text-primary);
    font-size: 15px;
    outline: none;
  }

  .search-input::placeholder {
    color: var(--text-muted);
  }

  .search-btn {
    background: var(--accent-orange);
    color: white;
    border: none;
    padding: 8px 20px;
    border-radius: var(--radius);
    font-weight: 600;
    font-size: 14px;
    min-width: 90px;
    transition: all 0.2s;
  }

  .search-btn:hover:not(:disabled) {
    background: #ea580c;
    transform: translateY(-1px);
  }

  .search-btn:disabled {
    opacity: 0.7;
    cursor: not-allowed;
  }

  .shortcut-hint {
    position: absolute;
    right: 120px;
    color: var(--text-muted);
    font-size: 12px;
    opacity: 0.7;
  }

  .spinner {
    display: inline-block;
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
