import { writable } from 'svelte/store';

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
