<template>
    <div class="app-container">
        <!-- Navigation -->
        <Navbar/>
        <!-- Main Content -->
        <main class="container py-4">
            <router-view v-slot="{ Component }">
                <transition name="fade" mode="out-in">
                    <component :is="Component"/>
                </transition>
            </router-view>
        </main>
        <!-- Footer -->
        <footer class="footer mt-auto py-3 bg-light border-top">
            <div class="container">
                <div class="row">
                    <div class="col-md-6">
                        <p class="mb-0 text-muted">&copy; {{ currentYear }} pyERP. All rights reserved.</p>
                    </div>
                    <div class="col-md-6 text-md-end">
                        <p class="mb-0 text-muted">Version {{ appVersion }}</p>
                    </div>
                </div>
            </div>
        </footer>
        <!-- Debug Panel -->
        <DebugPanel />
    </div>
</template>
<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import { useAuthStore } from './store/auth';
import Navbar from './components/layout/Navbar.vue';
import DebugPanel from './components/debug/DebugPanel.vue';

// Initialize auth store
const authStore = useAuthStore();

// Get current year for copyright
const currentYear = new Date().getFullYear();

// App version
const appVersion = import.meta.env.VITE_APP_VERSION || '1.0.0';

// Initialize auth state when app is mounted
onMounted(async () => {
    await authStore.init();
});
</script>
<style>
/* Global styles */
:root {
    --primary-color: #d2bc9b;
    --primary-hover: #c0aa89;
    --text-color: #343a40;
    --light-bg: #f8f9fa;
    --border-color: #e9ecef;
}

html, body {
    height: 100%;
    color: var(--text-color);
}

body {
    display: flex;
    flex-direction: column;
    font-family: 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
}

.app-container {
    display: flex;
    flex-direction: column;
    min-height: 100vh;
}

main {
    flex: 1 0 auto;
}

.footer {
    flex-shrink: 0;
}

/* Override Bootstrap primary color */
.btn-primary {
    background-color: var(--primary-color);
    border-color: var(--primary-color);
}

.btn-primary:hover, .btn-primary:focus {
    background-color: var(--primary-hover);
    border-color: var(--primary-hover);
}

.text-primary {
    color: var(--primary-color) !important;
}

.bg-primary {
    background-color: var(--primary-color) !important;
}

/* Transition animations */
.fade-enter-active,
.fade-leave-active {
    transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
    opacity: 0;
}
</style>
