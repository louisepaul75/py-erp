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
                            {{ t('common.profile') }}
                        </v-list-item-title>
                    </v-list-item>
                    
                    <v-list-item to="/settings">
                        <v-list-item-title>
                            <v-icon class="mr-2">{{ authStore.isAdmin ? 'mdi-shield-account-outline' : 'mdi-cog' }}</v-icon>
                            {{ authStore.isAdmin ? t('common.adminDashboard') : t('common.settings') }}
                        </v-list-item-title>
                    </v-list-item>
                    
                    <!-- Theme Toggle -->
                    <v-list-item @click="themeStore.toggleTheme">
                        <v-list-item-title class="d-flex align-center">
                            <v-icon class="mr-2">{{ themeStore.isDark ? 'mdi-weather-night' : 'mdi-weather-sunny' }}</v-icon>
                            {{ themeStore.isDark ? t('common.lightMode') : t('common.darkMode') }}
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

                    <!-- Language Selection -->
                    <v-list-item>
                        <v-list-item-title class="d-flex align-center">
                            <v-icon class="mr-2">mdi-translate</v-icon>
                            {{ t('common.language') }}
                            <v-menu
                                v-model="showLanguageMenu"
                                :close-on-content-click="true"
                                location="end"
                            >
                                <template v-slot:activator="{ props }">
                                    <v-btn
                                        variant="text"
                                        v-bind="props"
                                        class="ml-auto text-none"
                                        size="small"
                                    >
                                        {{ currentLanguage }}
                                        <v-icon end>mdi-chevron-down</v-icon>
                                    </v-btn>
                                </template>
                                <v-list>
                                    <v-list-item
                                        v-for="lang in languages"
                                        :key="lang.code"
                                        :value="lang.code"
                                        @click="changeLanguage(lang.code)"
                                    >
                                        <v-list-item-title>{{ lang.name }}</v-list-item-title>
                                    </v-list-item>
                                </v-list>
                            </v-menu>
                        </v-list-item-title>
                    </v-list-item>
                    
                    <v-divider></v-divider>
                    
                    <v-list-item to="/logout">
                        <v-list-item-title>
                            <v-icon class="mr-2">mdi-logout</v-icon>
                            {{ t('common.logout') }}
                        </v-list-item-title>
                    </v-list-item>
                </v-list>
            </v-menu>
        </template>
        <template v-else>
            <v-btn to="/login" variant="text">
                <v-icon class="mr-1">mdi-login</v-icon>
                {{ t('common.login') }}
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
            
            <!-- User Account Links in Mobile Menu -->
            <v-list-item v-if="authStore.isAuthenticated" to="/profile">
                <template v-slot:prepend>
                    <v-icon>mdi-card-account-details</v-icon>
                </template>
                <v-list-item-title>{{ t('common.profile') }}</v-list-item-title>
            </v-list-item>
            
            <v-list-item v-if="authStore.isAuthenticated" to="/settings">
                <template v-slot:prepend>
                    <v-icon>{{ authStore.isAdmin ? 'mdi-shield-account-outline' : 'mdi-cog' }}</v-icon>
                </template>
                <v-list-item-title>{{ authStore.isAdmin ? t('common.adminDashboard') : t('common.settings') }}</v-list-item-title>
            </v-list-item>
            
            <!-- Theme Toggle in Mobile Menu -->
            <v-list-item @click="themeStore.toggleTheme">
                <v-list-item-title class="d-flex align-center">
                    <v-icon class="mr-2">{{ themeStore.isDark ? 'mdi-weather-night' : 'mdi-weather-sunny' }}</v-icon>
                    {{ themeStore.isDark ? t('common.lightMode') : t('common.darkMode') }}
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

            <!-- Language Selection in Mobile Menu -->
            <v-list-item>
                <v-list-item-title class="d-flex align-center">
                    <v-icon class="mr-2">mdi-translate</v-icon>
                    {{ t('common.language') }}
                    <v-menu
                        v-model="showLanguageMenu"
                        :close-on-content-click="true"
                        location="end"
                    >
                        <template v-slot:activator="{ props }">
                            <v-btn
                                variant="text"
                                v-bind="props"
                                class="ml-auto text-none"
                                size="small"
                            >
                                {{ currentLanguage }}
                                <v-icon end>mdi-chevron-down</v-icon>
                            </v-btn>
                        </template>
                        <v-list>
                            <v-list-item
                                v-for="lang in languages"
                                :key="lang.code"
                                :value="lang.code"
                                @click="changeLanguage(lang.code)"
                            >
                                <v-list-item-title>{{ lang.name }}</v-list-item-title>
                            </v-list-item>
                        </v-list>
                    </v-menu>
                </v-list-item-title>
            </v-list-item>
            
            <v-list-item v-if="authStore.isAuthenticated" to="/logout">
                <template v-slot:prepend>
                    <v-icon>mdi-logout</v-icon>
                </template>
                <v-list-item-title>{{ t('common.logout') }}</v-list-item-title>
            </v-list-item>
        </v-list>
    </v-navigation-drawer>
</template>

<script setup lang="ts">
import { useAuthStore } from '../../store/auth';
import { useThemeStore } from '../../store/theme';
import { useI18n } from 'vue-i18n';
import { ref, computed, onMounted } from 'vue';

const authStore = useAuthStore();
const themeStore = useThemeStore();
const { locale, t } = useI18n();
const drawer = ref(false);
const showLanguageMenu = ref(false);

const languages = [
    { code: 'en', name: 'English' },
    { code: 'de', name: 'Deutsch' },
    { code: 'cs', name: 'Čeština' }
];

const currentLanguage = computed(() => {
    const lang = languages.find(l => l.code === locale.value);
    return lang ? lang.name : 'English';
});

const toggleLanguageMenu = () => {
    showLanguageMenu.value = !showLanguageMenu.value;
};

const changeLanguage = (langCode: string) => {
    locale.value = langCode;
    // Store the language preference in localStorage
    localStorage.setItem('preferred-language', langCode);
};

const navItems = [
    { title: t('nav.dashboard'), to: '/' },
    { title: t('nav.dashboard_2'), to: '/dashboard_2' },
    { title: t('nav.products'), to: '/products' },
    { title: t('nav.sales'), to: '/sales' },
    { title: t('nav.inventory'), to: '/inventory' },
    { title: t('nav.production'), to: '/production' },
    { title: t('nav.test'), to: '/test' },
];

// Initialize language from localStorage or default to 'en'
onMounted(() => {
    const savedLanguage = localStorage.getItem('preferred-language');
    if (savedLanguage && languages.some(l => l.code === savedLanguage)) {
        locale.value = savedLanguage;
    }
});
</script>

<style scoped>
.v-btn {
    text-transform: none;
    font-weight: 500;
}
</style>
