// API helpers - works with Tauri invoke or direct HTTP fetch
// Enhanced with comprehensive debugging, error handling, and retry logic

const API_BASE = 'http://127.0.0.1:8000';
const DEBUG = true; // Enable debug logging
const MAX_RETRIES = 3;
const RETRY_DELAY = 1000; // ms
const DEFAULT_TIMEOUT = 120000; // 2 minutes for chat requests

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

// Sleep helper for retry delays
function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

// Generic fetch wrapper with enhanced error handling, debugging, and retry logic
async function apiFetch(endpoint, options = {}) {
  const url = `${API_BASE}${endpoint}`;
  const method = options.method || 'GET';
  const timeout = options.timeout || (method === 'POST' && endpoint === '/chat' ? DEFAULT_TIMEOUT : 30000);
  const maxRetries = options.retries !== undefined ? options.retries : (method === 'GET' ? MAX_RETRIES : 1);

  debugLog('API', `${method} ${endpoint}`, options.body ? JSON.parse(options.body) : null);

  let lastError = null;

  for (let attempt = 1; attempt <= maxRetries; attempt++) {
    const startTime = performance.now();

    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), timeout);

      const response = await fetch(url, {
        headers: {
          'Content-Type': 'application/json',
          ...options.headers
        },
        signal: controller.signal,
        ...options
      });

      clearTimeout(timeoutId);

      const elapsed = Math.round(performance.now() - startTime);

      if (!response.ok) {
        const errorText = await response.text().catch(() => 'No error body');
        debugLog('API', `ERROR ${response.status} after ${elapsed}ms (attempt ${attempt}/${maxRetries}): ${errorText}`);
        lastError = new Error(`API error ${response.status}: ${errorText}`);

        // Don't retry client errors (4xx)
        if (response.status >= 400 && response.status < 500) {
          throw lastError;
        }

        // Retry server errors (5xx)
        if (attempt < maxRetries) {
          debugLog('API', `Retrying in ${RETRY_DELAY}ms...`);
          await sleep(RETRY_DELAY * attempt);
          continue;
        }
        throw lastError;
      }

      const data = await response.json();
      debugLog('API', `SUCCESS ${response.status} in ${elapsed}ms`,
        typeof data === 'object' ? { keys: Object.keys(data), length: Array.isArray(data) ? data.length : undefined } : data);

      return data;
    } catch (error) {
      const elapsed = Math.round(performance.now() - startTime);

      if (error.name === 'AbortError') {
        debugLog('API', `TIMEOUT after ${elapsed}ms (attempt ${attempt}/${maxRetries})`);
        lastError = new Error(`Request timed out after ${timeout / 1000}s. The daemon may be processing a large request.`);
      } else if (error.name === 'TypeError' && error.message.includes('Failed to fetch')) {
        debugLog('API', `NETWORK ERROR after ${elapsed}ms (attempt ${attempt}/${maxRetries}) - daemon may not be running`);
        lastError = new Error('Cannot connect to Promethean Light daemon. Is it running?');
      } else {
        debugLog('API', `EXCEPTION after ${elapsed}ms (attempt ${attempt}/${maxRetries}): ${error.message}`);
        lastError = error;
      }

      // Retry on network/timeout errors
      if (attempt < maxRetries && (error.name === 'AbortError' || error.name === 'TypeError')) {
        debugLog('API', `Retrying in ${RETRY_DELAY}ms...`);
        await sleep(RETRY_DELAY * attempt);
        continue;
      }
    }
  }

  throw lastError || new Error('Request failed after retries');
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

// Chat with the system (RAG) - enhanced with options and better error handling
export async function chat(message, conversationId = null, options = {}) {
  debugLog('CHAT', `Sending message: "${message.substring(0, 50)}..."`, { conversationId, options });
  const startTime = performance.now();

  try {
    const result = await apiFetch('/chat', {
      method: 'POST',
      timeout: options.timeout || DEFAULT_TIMEOUT,
      retries: 1, // Don't retry chat requests automatically
      body: JSON.stringify({
        message,
        conversation_id: conversationId,
        ...options.params
      })
    });

    const elapsed = Math.round(performance.now() - startTime);
    debugLog('CHAT', `Response received in ${elapsed}ms, ${result.sources?.length || 0} sources`);

    // Add metadata for UI
    result._meta = {
      elapsed_ms: elapsed,
      timestamp: new Date().toISOString()
    };

    return result;
  } catch (error) {
    const elapsed = Math.round(performance.now() - startTime);
    debugLog('CHAT', `FAILED after ${elapsed}ms: ${error.message}`);

    // Wrap error with more context
    const enhancedError = new Error(error.message);
    enhancedError.elapsed_ms = elapsed;
    enhancedError.isTimeout = error.message.includes('timed out');
    enhancedError.isNetwork = error.message.includes('Cannot connect');
    throw enhancedError;
  }
}

// Deep search - performs multiple related searches for comprehensive results
export async function deepSearch(query, options = {}) {
  debugLog('DEEP_SEARCH', `Starting deep search for: "${query.substring(0, 50)}..."`);

  const limit = options.limit || 30;
  const results = [];
  const seen = new Set();

  // Primary search
  const primary = await searchDocuments(query, limit);
  for (const r of primary) {
    if (!seen.has(r.id)) {
      seen.add(r.id);
      results.push({ ...r, search_type: 'primary' });
    }
  }

  // Extract potential entities for secondary searches
  const entities = extractEntities(query);
  debugLog('DEEP_SEARCH', `Extracted ${entities.length} entities for secondary search`);

  // Secondary searches on entities (parallel)
  if (entities.length > 0) {
    const secondaryPromises = entities.slice(0, 3).map(async (entity) => {
      try {
        return await searchDocuments(entity, Math.floor(limit / 2));
      } catch {
        return [];
      }
    });

    const secondaryResults = await Promise.all(secondaryPromises);
    for (const batch of secondaryResults) {
      for (const r of batch) {
        if (!seen.has(r.id)) {
          seen.add(r.id);
          results.push({ ...r, search_type: 'secondary' });
        }
      }
    }
  }

  debugLog('DEEP_SEARCH', `Deep search complete: ${results.length} total results`);
  return results;
}

// Extract entities from query for secondary searches
function extractEntities(text) {
  const entities = [];

  // Extract capitalized words (potential names/organizations)
  const namePattern = /\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b/g;
  const names = text.match(namePattern) || [];
  entities.push(...names.filter(n => n.length > 2 && !['The', 'From', 'This', 'That', 'What', 'When', 'Where', 'Which'].includes(n)));

  // Extract email patterns
  const emailPattern = /[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}/g;
  const emails = text.match(emailPattern) || [];
  entities.push(...emails);

  // Extract project-like patterns
  const projectPattern = /\b(?:project|Q\d+)\s*[:\s]?\s*\w+/gi;
  const projects = text.match(projectPattern) || [];
  entities.push(...projects);

  return [...new Set(entities)];
}

// Get structured email list with metadata
export async function listEmails(options = {}) {
  debugLog('EMAILS', 'Listing emails', options);
  const result = await apiFetch('/emails/list', {
    method: 'POST',
    body: JSON.stringify({
      days: options.days || 7,
      limit: options.limit || 50,
      sender: options.sender || null
    })
  });
  debugLog('EMAILS', `Found ${result.count} emails`);
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

// Trigger immediate email sync from Outlook
export async function syncEmails() {
  debugLog('EMAIL', 'Triggering email sync...');
  const result = await apiFetch('/email/sync', {
    method: 'POST'
  });
  debugLog('EMAIL', 'Sync result:', result);
  return result;
}

// Get email sync status
export async function getEmailStatus() {
  debugLog('EMAIL', 'Fetching email status...');
  const result = await apiFetch('/email/status');
  debugLog('EMAIL', 'Email status:', result);
  return result;
}
