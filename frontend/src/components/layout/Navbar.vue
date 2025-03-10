<template>
    <v-app-bar :color="themeStore.isDark ? 'surface' : 'white'" elevation="1">
        <router-link to="/">
            <img src="@/assets/wsz_logo_long.png" alt="WSZ Logo" height="40">
        </router-link>
        
        <v-spacer></v-spacer>
        
        <!-- Navigation Links - Desktop -->
        <div class="d-none d-md-flex">
            <v-btn
                v-for="item in navItems"
                :key="item.title"
                :to="item.to"
                variant="text"
                class="mx-1"
            >
                {{ item.title }}
            </v-btn>
        </div>
        
        <v-spacer></v-spacer>
        
        <!-- Authentication Links -->
        <template v-if="authStore.isAuthenticated">
            <v-menu>
                <template v-slot:activator="{ props }">
                    <v-btn
                        variant="text"
                        v-bind="props"
                    >
                        <v-icon class="mr-1">mdi-account</v-icon>
                        {{ authStore.fullName || authStore.user?.username }}
                    </v-btn>
                </template>
                <v-list>
                    <v-list-item to="/profile">
                        <v-list-item-title>
                            <v-icon class="mr-2">mdi-card-account-details</v-icon>
                            Profile
                        </v-list-item-title>
                    </v-list-item>
                    
                    <v-list-item to="/settings">
                        <v-list-item-title>
                            <v-icon class="mr-2">mdi-cog</v-icon>
                            Settings
                        </v-list-item-title>
                    </v-list-item>
                    
                    <!-- Theme Toggle -->
                    <v-list-item @click="themeStore.toggleTheme">
                        <v-list-item-title class="d-flex align-center">
                            <v-icon class="mr-2">{{ themeStore.isDark ? 'mdi-weather-night' : 'mdi-weather-sunny' }}</v-icon>
                            {{ themeStore.isDark ? 'Light Mode' : 'Dark Mode' }}
                            <v-switch
                                v-model="themeStore.isDark"
                                hide-details
                                inset
                                density="compact"
                                color="primary"
                                class="ml-auto"
                            ></v-switch>
                        </v-list-item-title>
                    </v-list-item>
                    
                    <v-divider></v-divider>
                    
                    <v-list-item to="/logout">
                        <v-list-item-title>
                            <v-icon class="mr-2">mdi-logout</v-icon>
                            Logout
                        </v-list-item-title>
                    </v-list-item>
                </v-list>
            </v-menu>
        </template>
        <template v-else>
            <v-btn to="/login" variant="text">
                <v-icon class="mr-1">mdi-login</v-icon>
                Login
            </v-btn>
        </template>
        
        <!-- Mobile Menu Button -->
        <v-app-bar-nav-icon class="d-md-none" @click="drawer = !drawer"></v-app-bar-nav-icon>
    </v-app-bar>
    
    <!-- Mobile Navigation Drawer -->
    <v-navigation-drawer v-model="drawer" temporary location="right">
        <v-list>
            <v-list-item
                v-for="item in navItems"
                :key="item.title"
                :to="item.to"
                link
            >
                <v-list-item-title>{{ item.title }}</v-list-item-title>
            </v-list-item>
            
            <v-divider class="my-2"></v-divider>
            
            <!-- Theme Toggle in Mobile Menu -->
            <v-list-item @click="themeStore.toggleTheme">
                <v-list-item-title class="d-flex align-center">
                    <v-icon class="mr-2">{{ themeStore.isDark ? 'mdi-weather-night' : 'mdi-weather-sunny' }}</v-icon>
                    {{ themeStore.isDark ? 'Light Mode' : 'Dark Mode' }}
                    <v-switch
                        v-model="themeStore.isDark"
                        hide-details
                        inset
                        density="compact"
                        color="primary"
                        class="ml-auto"
                    ></v-switch>
                </v-list-item-title>
            </v-list-item>
        </v-list>
    </v-navigation-drawer>
</template>

<script setup lang="ts">
import { useAuthStore } from '../../store/auth';
import { useThemeStore } from '../../store/theme';
import { ref } from 'vue';

const authStore = useAuthStore();
const themeStore = useThemeStore();
const drawer = ref(false);

const navItems = [
    { title: 'Dashboard', to: '/' },
    { title: 'Dashboard_2', to: '/dashboard_2' },
    { title: 'Products', to: '/products' },
    { title: 'Sales', to: '/sales' },
    { title: 'Inventory', to: '/inventory' },
    { title: 'Production', to: '/production' },
    { title: 'Test Page', to: '/test' },
];
</script>

<style scoped>
.v-btn {
    text-transform: none;
    font-weight: 500;
}
</style>
