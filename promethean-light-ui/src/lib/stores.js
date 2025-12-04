import { writable } from 'svelte/store';
import { getSavedSearches, getSavedSearchFolders, saveSearch, deleteSavedSearch } from './api.js';

// Connection status
export const daemonConnected = writable(false);

// Search state
export const searchQuery = writable('');
export const searchResults = writable([]);
export const isSearching = writable(false);

// Stats
export const stats = writable({
  total_documents: 0,
  total_chunks: 0,
  total_tags: 0
});

// Favorites (saved searches)
export const favorites = writable([]);

// Tags from API
export const tags = writable([]);

// Clusters from API
export const clusters = writable([]);

// Active section (default to chat/Ask)
export const activeSection = writable('chat');

// Chat state
export const chatMessages = writable([]);
export const chatInput = writable('');

// Database info
export const databaseInfo = writable({
  current_database: 'default',
  database_path: '',
  qdrant_path: '',
  available_databases: []
});

// API keys status
export const apiKeysStatus = writable({
  openai: false,
  anthropic: false
});

// View mode for data display: 'cards' | 'table' | 'sections' | 'split'
export const viewMode = writable('cards');

// Selected result for split pane detail view
export const selectedResult = writable(null);

// Expanded sections state for section view
export const expandedSections = writable({
  emails: true,
  documents: true,
  notes: true
});

// Current response (single panel layout)
export const currentResponse = writable(null); // {query, response, sources, timestamp}

// Conversation history for history drawer
export const conversationHistory = writable([]);

// History drawer open state
export const historyDrawerOpen = writable(false);

// File upload state
export const uploadProgress = writable({
  isUploading: false,
  filename: '',
  progress: 0,
  status: 'idle' // 'idle' | 'checking' | 'uploading' | 'complete' | 'error'
});

// Saved items with folder structure (now backed by database API)
export const savedFolders = writable([
  { id: 'reports', name: 'Reports', items: [] },
  { id: 'research', name: 'Research', items: [] },
  { id: 'general', name: 'General', items: [] }
]);

// Load saved folders from database API
export async function loadSavedFolders() {
  try {
    // Get all saved searches from API
    const searches = await getSavedSearches();

    // Group by folder
    const folderMap = {
      'reports': { id: 'reports', name: 'Reports', items: [] },
      'research': { id: 'research', name: 'Research', items: [] },
      'general': { id: 'general', name: 'General', items: [] }
    };

    for (const search of searches) {
      const folderId = search.folder || 'general';
      if (!folderMap[folderId]) {
        // Create new folder if doesn't exist
        folderMap[folderId] = {
          id: folderId,
          name: folderId.charAt(0).toUpperCase() + folderId.slice(1),
          items: []
        };
      }
      folderMap[folderId].items.push({
        id: search.id,
        query: search.query,
        response: search.response,
        sources: search.sources ? JSON.parse(search.sources) : [],
        savedAt: search.created_at
      });
    }

    savedFolders.set(Object.values(folderMap));
  } catch (e) {
    console.error('Failed to load saved folders from API:', e);
    // Fallback to localStorage for offline support
    if (typeof window !== 'undefined') {
      const saved = localStorage.getItem('promethean-saved-folders');
      if (saved) {
        try {
          savedFolders.set(JSON.parse(saved));
        } catch (e2) {
          console.error('Failed to load saved folders from localStorage:', e2);
        }
      }
    }
  }
}

// Save item to a folder (via database API)
export async function saveToFolder(folderId, item) {
  try {
    // Save to API
    const saved = await saveSearch(
      item.query,
      item.response,
      folderId,
      item.sources
    );

    // Update local store
    savedFolders.update(folders => {
      return folders.map(folder => {
        if (folder.id === folderId) {
          const newItem = {
            id: saved.id,
            query: item.query,
            response: item.response,
            sources: item.sources || [],
            savedAt: saved.created_at
          };
          return { ...folder, items: [newItem, ...folder.items] };
        }
        return folder;
      });
    });

    return saved;
  } catch (e) {
    console.error('Failed to save to folder via API:', e);
    // Fallback to localStorage
    savedFolders.update(folders => {
      const updated = folders.map(folder => {
        if (folder.id === folderId) {
          const newItem = {
            id: Date.now(),
            ...item,
            savedAt: new Date().toISOString()
          };
          return { ...folder, items: [newItem, ...folder.items].slice(0, 100) };
        }
        return folder;
      });
      if (typeof window !== 'undefined') {
        localStorage.setItem('promethean-saved-folders', JSON.stringify(updated));
      }
      return updated;
    });
  }
}

// Create new folder (folders are created implicitly when saving)
export function createFolder(name) {
  savedFolders.update(folders => {
    const newFolder = {
      id: name.toLowerCase().replace(/\s+/g, '-'),
      name,
      items: []
    };
    return [...folders, newFolder];
  });
}

// Remove item from folder (via database API)
export async function removeFromFolder(folderId, itemId) {
  try {
    // Delete from API
    await deleteSavedSearch(itemId);

    // Update local store
    savedFolders.update(folders => {
      return folders.map(folder => {
        if (folder.id === folderId) {
          return { ...folder, items: folder.items.filter(item => item.id !== itemId) };
        }
        return folder;
      });
    });
  } catch (e) {
    console.error('Failed to delete from API:', e);
    // Still update local store
    savedFolders.update(folders => {
      const updated = folders.map(folder => {
        if (folder.id === folderId) {
          return { ...folder, items: folder.items.filter(item => item.id !== itemId) };
        }
        return folder;
      });
      if (typeof window !== 'undefined') {
        localStorage.setItem('promethean-saved-folders', JSON.stringify(updated));
      }
      return updated;
    });
  }
}

// Save current response to history
export function saveToHistory(query, response, sources = []) {
  conversationHistory.update(history => {
    const newEntry = {
      id: Date.now(),
      query,
      response,
      sources,
      timestamp: new Date().toISOString()
    };
    const updated = [newEntry, ...history].slice(0, 100); // Max 100 entries
    if (typeof window !== 'undefined') {
      localStorage.setItem('promethean-history', JSON.stringify(updated));
    }
    return updated;
  });
}

// Load history from localStorage
export function loadHistory() {
  if (typeof window !== 'undefined') {
    const saved = localStorage.getItem('promethean-history');
    if (saved) {
      try {
        conversationHistory.set(JSON.parse(saved));
      } catch (e) {
        console.error('Failed to load history:', e);
      }
    }
  }
}

// Load favorites from localStorage on init
export function loadFavorites() {
  if (typeof window !== 'undefined') {
    const saved = localStorage.getItem('promethean-favorites');
    if (saved) {
      try {
        favorites.set(JSON.parse(saved));
      } catch (e) {
        console.error('Failed to load favorites:', e);
      }
    }
  }
}

// Save favorites to localStorage
export function saveFavorite(query, results) {
  favorites.update(f => {
    const newFavorite = {
      id: Date.now(),
      query,
      results: results.slice(0, 5), // Keep top 5 results
      savedAt: new Date().toISOString()
    };
    const updated = [newFavorite, ...f].slice(0, 50); // Max 50 favorites
    if (typeof window !== 'undefined') {
      localStorage.setItem('promethean-favorites', JSON.stringify(updated));
    }
    return updated;
  });
}

// Remove a favorite
export function removeFavorite(id) {
  favorites.update(f => {
    const updated = f.filter(fav => fav.id !== id);
    if (typeof window !== 'undefined') {
      localStorage.setItem('promethean-favorites', JSON.stringify(updated));
    }
    return updated;
  });
}
