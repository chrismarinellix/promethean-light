<script>
  import Sidebar from '$lib/components/Sidebar.svelte';
  import ChatPanel from '$lib/components/ChatPanel.svelte';
  import AdminPanel from '$lib/components/AdminPanel.svelte';
  import { activeSection } from '$lib/stores.js';
</script>

<div class="app-container">
  <Sidebar />

  <main class="main-content">
    {#if $activeSection === 'admin'}
      <AdminPanel />
    {:else}
      <ChatPanel />
    {/if}
  </main>
</div>

<style>
  .app-container {
    display: flex;
    height: 100vh;
    overflow: hidden;
  }

  .main-content {
    flex: 1;
    display: flex;
    flex-direction: column;
    overflow: hidden;
  }
</style>
