import { defineStore } from 'pinia';
import { ref } from 'vue';

export const useThemeStore = defineStore('theme', () => {
  // Check for system dark mode preference using media query
  const getSystemPreference = () => {
    if (typeof window !== 'undefined') {
      return window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;
    }
    return false;
  };
  
  // Initialize theme from localStorage or system preference
  const storedTheme = localStorage.getItem('theme');
  const isDark = ref(storedTheme !== null 
    ? storedTheme === 'dark'
    : getSystemPreference()
  );

  // Toggle theme function
  function toggleTheme() {
    isDark.value = !isDark.value;
    localStorage.setItem('theme', isDark.value ? 'dark' : 'light');
  }

  // Set specific theme
  function setTheme(dark: boolean) {
    isDark.value = dark;
    localStorage.setItem('theme', isDark.value ? 'dark' : 'light');
  }

  // Add event listener for system preference changes if in browser environment
  if (typeof window !== 'undefined') {
    window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', (e) => {
      // Only update if user hasn't set a preference
      if (localStorage.getItem('theme') === null) {
        isDark.value = e.matches;
      }
    });
  }

  return {
    isDark,
    toggleTheme,
    setTheme
  };
}); 