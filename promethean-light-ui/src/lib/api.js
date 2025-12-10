// API helpers - works with Tauri invoke or direct HTTP fetch
// Enhanced with comprehensive debugging and error handling

const API_BASE = 'http://127.0.0.1:8000';
const DEBUG = true; // Enable debug logging

// Debug logger
function debugLog(context, message, data = null) {
  if (!DEBUG) return;
  const timestamp = new Date().toISOString().split('T')[1].slice(0, 12);
  const prefix = `[PL ${timestamp}] [${context}]`;
  if (data !== null) {
    console.log(prefix, message, data);
  } else {
    console.log(prefix, message);
  }
}

// Check if running in Tauri (v2 compatible)
function isTauri() {
  const inTauri = typeof window !== 'undefined' && (window.__TAURI__ || window.__TAURI_INTERNALS__);
  debugLog('ENV', `isTauri check: ${inTauri}`);
  return inTauri;
}

// Generic fetch wrapper with enhanced error handling and debugging
async function apiFetch(endpoint, options = {}) {
  const url = `${API_BASE}${endpoint}`;
  const method = options.method || 'GET';

  debugLog('API', `${method} ${endpoint}`, options.body ? JSON.parse(options.body) : null);

  const startTime = performance.now();

  try {
    const response = await fetch(url, {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers
      },
      ...options
    });

    const elapsed = Math.round(performance.now() - startTime);

    if (!response.ok) {
      const errorText = await response.text().catch(() => 'No error body');
      debugLog('API', `ERROR ${response.status} after ${elapsed}ms: ${errorText}`);
      throw new Error(`API error ${response.status}: ${errorText}`);
    }

    const data = await response.json();
    debugLog('API', `SUCCESS ${response.status} in ${elapsed}ms`,
      typeof data === 'object' ? { keys: Object.keys(data), length: Array.isArray(data) ? data.length : undefined } : data);

    return data;
  } catch (error) {
    const elapsed = Math.round(performance.now() - startTime);
    if (error.name === 'TypeError' && error.message.includes('Failed to fetch')) {
      debugLog('API', `NETWORK ERROR after ${elapsed}ms - daemon may not be running`);
      throw new Error('Cannot connect to Promethean Light daemon. Is it running?');
    }
    debugLog('API', `EXCEPTION after ${elapsed}ms: ${error.message}`);
    throw error;
  }
}

// Check daemon health with retry logic for stability
let lastCheckResult = false;
let consecutiveFailures = 0;
const MAX_FAILURES_BEFORE_DISCONNECT = 3; // Require 3 consecutive failures before showing disconnected

export async function checkDaemon() {
  debugLog('DAEMON', 'Checking daemon health...');
  try {
    if (isTauri()) {
      debugLog('DAEMON', 'Using Tauri invoke for daemon check');
      const { invoke } = await import('@tauri-apps/api/core');
      const result = await invoke('check_daemon');
      debugLog('DAEMON', `Tauri check result: ${result}`);
      if (result) {
        consecutiveFailures = 0;
        lastCheckResult = true;
      } else {
        consecutiveFailures++;
      }
      // Only report disconnected after consecutive failures
      if (consecutiveFailures >= MAX_FAILURES_BEFORE_DISCONNECT) {
        lastCheckResult = false;
      }
      return lastCheckResult;
    }
    // Browser fallback - use root endpoint for faster check
    debugLog('DAEMON', 'Using HTTP fallback for daemon check');
    const response = await fetch(`${API_BASE}/`, {
      method: 'GET',
      signal: AbortSignal.timeout(5000) // 5 second timeout
    });
    const connected = response.ok;
    debugLog('DAEMON', `HTTP check result: ${connected}`);
    if (connected) {
      consecutiveFailures = 0;
      lastCheckResult = true;
    } else {
      consecutiveFailures++;
    }
    // Only report disconnected after consecutive failures
    if (consecutiveFailures >= MAX_FAILURES_BEFORE_DISCONNECT) {
      lastCheckResult = false;
    }
    return lastCheckResult;
  } catch (e) {
    debugLog('DAEMON', `Check failed: ${e.message}`);
    consecutiveFailures++;
    // Only report disconnected after consecutive failures
    if (consecutiveFailures >= MAX_FAILURES_BEFORE_DISCONNECT) {
      lastCheckResult = false;
    }
    return lastCheckResult;
  }
}

// Search documents
export async function searchDocuments(query, limit = 10) {
  debugLog('SEARCH', `Searching for: "${query.substring(0, 50)}..." limit=${limit}`);
  if (isTauri()) {
    const { invoke } = await import('@tauri-apps/api/core');
    const result = await invoke('search_documents', { query, limit });
    debugLog('SEARCH', `Found ${result.length} results via Tauri`);
    return result;
  }
  const result = await apiFetch('/search', {
    method: 'POST',
    body: JSON.stringify({ query, limit })
  });
  debugLog('SEARCH', `Found ${result.length} results via HTTP`);
  return result;
}

// Get stats
export async function getStats() {
  debugLog('STATS', 'Fetching daemon stats...');
  if (isTauri()) {
    const { invoke } = await import('@tauri-apps/api/core');
    const result = await invoke('get_stats');
    debugLog('STATS', 'Stats via Tauri:', result);
    return result;
  }
  const result = await apiFetch('/stats');
  debugLog('STATS', 'Stats via HTTP:', result);
  return result;
}

// Get tags
export async function getTags() {
  debugLog('TAGS', 'Fetching tags...');
  if (isTauri()) {
    const { invoke } = await import('@tauri-apps/api/core');
    const result = await invoke('get_tags');
    debugLog('TAGS', `Got ${result.length} tags via Tauri`);
    return result;
  }
  const result = await apiFetch('/tags');
  debugLog('TAGS', `Got ${result.length} tags via HTTP`);
  return result;
}

// Get dashboard stats
export async function getDashboardStats() {
  debugLog('DASHBOARD', 'Fetching dashboard stats...');
  const result = await apiFetch('/dashboard/stats');
  debugLog('DASHBOARD', 'Dashboard stats:', result);
  return result;
}

// Chat with the system (RAG)
export async function chat(message, conversationId = null) {
  debugLog('CHAT', `Sending message: "${message.substring(0, 50)}..."`, { conversationId });
  const startTime = performance.now();
  const result = await apiFetch('/chat', {
    method: 'POST',
    body: JSON.stringify({
      message,
      conversation_id: conversationId
    })
  });
  const elapsed = Math.round(performance.now() - startTime);
  debugLog('CHAT', `Response received in ${elapsed}ms, ${result.sources?.length || 0} sources`);
  return result;
}

// Start daemon with passphrase
export async function startDaemon(passphrase) {
  debugLog('DAEMON', 'Starting daemon...');
  if (isTauri()) {
    const { invoke } = await import('@tauri-apps/api/core');
    const result = await invoke('start_daemon', { passphrase });
    debugLog('DAEMON', `Start result: ${result}`);
    return result;
  }
  throw new Error('Daemon start only available in Tauri app');
}

// Stop daemon
export async function stopDaemon() {
  debugLog('DAEMON', 'Stopping daemon...');
  if (isTauri()) {
    const { invoke } = await import('@tauri-apps/api/core');
    const result = await invoke('stop_daemon');
    debugLog('DAEMON', `Stop result: ${result}`);
    return result;
  }
  throw new Error('Daemon stop only available in Tauri app');
}

// Get database info
export async function getDatabaseInfo() {
  debugLog('DB', 'Fetching database info...');
  const result = await apiFetch('/database/info');
  debugLog('DB', 'Database info:', result);
  return result;
}

// Get API keys status
export async function getApiKeysStatus() {
  debugLog('API_KEYS', 'Fetching API keys status...');
  const result = await apiFetch('/api-keys/status');
  debugLog('API_KEYS', 'API keys status:', result);
  return result;
}

// Get clusters
export async function getClusters() {
  debugLog('CLUSTERS', 'Fetching clusters...');
  const result = await apiFetch('/clusters');
  debugLog('CLUSTERS', `Got ${result.length} clusters`);
  return result;
}

// Get documents in a cluster
export async function getClusterDocuments(clusterId, limit = 20) {
  debugLog('CLUSTERS', `Fetching documents for cluster ${clusterId}...`);
  const result = await apiFetch(`/clusters/${clusterId}/documents?limit=${limit}`);
  debugLog('CLUSTERS', `Got ${result.length} documents for cluster ${clusterId}`);
  return result;
}

// Rebuild clusters
export async function rebuildClusters(minClusterSize = 10, minSamples = 5) {
  debugLog('CLUSTERS', `Rebuilding clusters (minSize=${minClusterSize}, minSamples=${minSamples})...`);
  const result = await apiFetch(`/clusters/rebuild?min_cluster_size=${minClusterSize}&min_samples=${minSamples}`, {
    method: 'POST'
  });
  debugLog('CLUSTERS', 'Rebuild result:', result);
  return result;
}

// Check for duplicate content before uploading
export async function checkDuplicate(content, threshold = 0.92) {
  debugLog('UPLOAD', `Checking for duplicates (threshold=${threshold})...`);
  const result = await apiFetch('/check-duplicate', {
    method: 'POST',
    body: JSON.stringify({ content, threshold })
  });
  debugLog('UPLOAD', 'Duplicate check result:', result);
  return result;
}

// Upload a file for ingestion
export async function uploadFile(file, onProgress = null) {
  const formData = new FormData();
  formData.append('file', file);

  const url = `${API_BASE}/add/file`;

  // Use XMLHttpRequest for progress tracking
  return new Promise((resolve, reject) => {
    const xhr = new XMLHttpRequest();

    xhr.upload.addEventListener('progress', (event) => {
      if (event.lengthComputable && onProgress) {
        const percentComplete = (event.loaded / event.total) * 100;
        onProgress(percentComplete);
      }
    });

    xhr.addEventListener('load', () => {
      if (xhr.status >= 200 && xhr.status < 300) {
        try {
          resolve(JSON.parse(xhr.responseText));
        } catch (e) {
          resolve({ success: true });
        }
      } else {
        reject(new Error(`Upload failed: ${xhr.status}`));
      }
    });

    xhr.addEventListener('error', () => {
      reject(new Error('Upload failed: Network error'));
    });

    xhr.open('POST', url);
    xhr.send(formData);
  });
}

// Read file content as text (for duplicate check)
export function readFileAsText(file, maxBytes = 500) {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();

    reader.onload = (e) => {
      const content = e.target.result;
      // Return first maxBytes characters for duplicate check
      resolve(content.slice(0, maxBytes));
    };

    reader.onerror = () => {
      reject(new Error('Failed to read file'));
    };

    // Read as text
    reader.readAsText(file);
  });
}

// Get saved searches (optionally filtered by folder)
export async function getSavedSearches(folder = null) {
  const endpoint = folder ? `/saved-searches?folder=${encodeURIComponent(folder)}` : '/saved-searches';
  return apiFetch(endpoint);
}

// Get saved search folders with counts
export async function getSavedSearchFolders() {
  return apiFetch('/saved-searches/folders');
}

// Save a search (query + response)
export async function saveSearch(query, response, folder = 'general', sources = null) {
  return apiFetch('/saved-searches', {
    method: 'POST',
    body: JSON.stringify({
      folder,
      query,
      response,
      sources: sources ? JSON.stringify(sources) : null
    })
  });
}

// Delete a saved search
export async function deleteSavedSearch(searchId) {
  return apiFetch(`/saved-searches/${searchId}`, {
    method: 'DELETE'
  });
}
