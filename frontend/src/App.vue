<template>
    <v-app>
        <!-- Navigation -->
        <Navbar/>
        <!-- Main Content -->
        <v-main>
            <v-container class="py-4">
                <router-view v-slot="{ Component }">
                    <transition name="fade" mode="out-in">
                        <component :is="Component"/>
                    </transition>
                </router-view>
            </v-container>
        </v-main>
        <!-- Debug Panel - Place before footer in DOM order -->
        <DebugPanel/>
        <!-- Footer - Must be last to appear at the bottom -->
        <Footer/>
    </v-app>
</template>
<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import { useAuthStore } from './store/auth';
import Navbar from './components/layout/Navbar.vue';
import Footer from './components/layout/Footer.vue';
import DebugPanel from './components/debug/DebugPanel.vue';

// Initialize auth store
const authStore = useAuthStore();

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
    /* Ensure proper stacking context */
    position: relative;
    overflow-x: hidden;
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
