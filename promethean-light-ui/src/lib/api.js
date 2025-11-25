// API helpers - works with Tauri invoke or direct HTTP fetch

const API_BASE = 'http://127.0.0.1:8000';

// Check if running in Tauri
function isTauri() {
  return typeof window !== 'undefined' && window.__TAURI__;
}

// Generic fetch wrapper
async function apiFetch(endpoint, options = {}) {
  const url = `${API_BASE}${endpoint}`;
  const response = await fetch(url, {
    headers: {
      'Content-Type': 'application/json',
      ...options.headers
    },
    ...options
  });

  if (!response.ok) {
    throw new Error(`API error: ${response.status}`);
  }

  return response.json();
}

// Check daemon health
export async function checkDaemon() {
  try {
    if (isTauri()) {
      const { invoke } = await import('@tauri-apps/api/core');
      return await invoke('check_daemon');
    }
    // Browser fallback - check /stats endpoint
    const data = await apiFetch('/stats');
    return data && data.total_documents !== undefined;
  } catch (e) {
    return false;
  }
}

// Search documents
export async function searchDocuments(query, limit = 10) {
  if (isTauri()) {
    const { invoke } = await import('@tauri-apps/api/core');
    return await invoke('search_documents', { query, limit });
  }
  return apiFetch('/search', {
    method: 'POST',
    body: JSON.stringify({ query, limit })
  });
}

// Get stats
export async function getStats() {
  if (isTauri()) {
    const { invoke } = await import('@tauri-apps/api/core');
    return await invoke('get_stats');
  }
  return apiFetch('/stats');
}

// Get tags
export async function getTags() {
  if (isTauri()) {
    const { invoke } = await import('@tauri-apps/api/core');
    return await invoke('get_tags');
  }
  return apiFetch('/tags');
}

// Get dashboard stats
export async function getDashboardStats() {
  return apiFetch('/dashboard/stats');
}

// Chat with the system (RAG)
export async function chat(message, conversationId = null) {
  return apiFetch('/chat', {
    method: 'POST',
    body: JSON.stringify({
      message,
      conversation_id: conversationId
    })
  });
}

// Start daemon with passphrase
export async function startDaemon(passphrase) {
  if (isTauri()) {
    const { invoke } = await import('@tauri-apps/api/core');
    return await invoke('start_daemon', { passphrase });
  }
  throw new Error('Daemon start only available in Tauri app');
}

// Stop daemon
export async function stopDaemon() {
  if (isTauri()) {
    const { invoke } = await import('@tauri-apps/api/core');
    return await invoke('stop_daemon');
  }
  throw new Error('Daemon stop only available in Tauri app');
}

// Get database info
export async function getDatabaseInfo() {
  return apiFetch('/database/info');
}

// Get API keys status
export async function getApiKeysStatus() {
  return apiFetch('/api-keys/status');
}
