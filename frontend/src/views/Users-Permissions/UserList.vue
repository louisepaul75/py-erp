<template>
  <div class="container mx-auto py-10">
    <div class="flex justify-between items-center mb-6">
      <h1 class="text-3xl font-bold">Benutzer</h1>
      <button 
        @click="openCreateUserModal" 
        class="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700">
        Neuer Benutzer
      </button>
    </div>

    <!-- Loading state -->
    <div v-if="loading" class="bg-white rounded-lg shadow-md p-8 text-center">
      <p class="text-gray-500">Benutzer werden geladen...</p>
    </div>

    <!-- Error state -->
    <div v-else-if="error" class="bg-white rounded-lg shadow-md p-8 text-center">
      <p class="text-red-500">Fehler beim Laden der Benutzer: {{ error }}</p>
      <button 
        @click="fetchUsers" 
        class="mt-4 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700">
        Erneut versuchen
      </button>
    </div>

    <!-- User list -->
    <div v-else class="bg-white rounded-lg shadow-md overflow-hidden">
      <div class="p-6">
        <div class="flex justify-between items-center mb-4">
          <h2 class="text-xl font-semibold">Alle Benutzer</h2>
          
          <!-- Search box -->
          <div class="relative">
            <input 
              v-model="searchQuery" 
              type="text" 
              placeholder="Benutzer suchen..." 
              class="pl-10 pr-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              @input="handleSearch"
            >
            <svg 
              class="absolute left-3 top-2.5 h-5 w-5 text-gray-400" 
              xmlns="http://www.w3.org/2000/svg" 
              viewBox="0 0 24 24" 
              fill="none" 
              stroke="currentColor" 
              stroke-width="2"
            >
              <circle cx="11" cy="11" r="8"></circle>
              <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
            </svg>
          </div>
        </div>

        <div class="overflow-x-auto">
          <table class="w-full">
            <thead>
              <tr class="border-b">
                <th class="text-left py-3 px-4">Benutzername</th>
                <th class="text-left py-3 px-4">Name</th>
                <th class="text-left py-3 px-4">E-Mail</th>
                <th class="text-left py-3 px-4">Abteilung</th>
                <th class="text-left py-3 px-4">Status</th>
                <th class="text-left py-3 px-4">Gruppen</th>
                <th class="text-right py-3 px-4">Aktionen</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="user in users" :key="user.id" class="border-b hover:bg-gray-50">
                <td class="py-3 px-4 font-medium">{{ user.username }}</td>
                <td class="py-3 px-4">{{ user.first_name }} {{ user.last_name }}</td>
                <td class="py-3 px-4">{{ user.email }}</td>
                <td class="py-3 px-4">{{ user.profile?.department || '-' }}</td>
                <td class="py-3 px-4">
                  <span 
                    :class="{
                      'bg-green-100 text-green-800': user.profile?.status === 'active',
                      'bg-red-100 text-red-800': user.profile?.status === 'inactive',
                      'bg-yellow-100 text-yellow-800': user.profile?.status === 'pending',
                      'bg-orange-100 text-orange-800': user.profile?.status === 'locked',
                      'bg-gray-100 text-gray-800': !user.profile?.status
                    }" 
                    class="px-2 py-1 rounded-full text-xs font-medium"
                  >
                    {{ formatStatus(user.profile?.status) || (user.is_active ? 'Aktiv' : 'Inaktiv') }}
                  </span>
                </td>
                <td class="py-3 px-4">
                  <div class="flex flex-wrap gap-1">
                    <span
                      v-for="group in user.groups"
                      :key="group.id"
                      class="px-2 py-1 text-xs rounded-full border border-gray-200"
                    >
                      {{ group.name }}
                    </span>
                  </div>
                </td>
                <td class="py-3 px-4 text-right">
                  <div class="flex justify-end gap-2">
                    <button
                      @click="openAssignGroupsModal(user)"
                      class="p-1 rounded-md hover:bg-gray-100"
                      title="Gruppen zuweisen"
                    >
                      <svg
                        xmlns="http://www.w3.org/2000/svg"
                        class="h-4 w-4"
                        viewBox="0 0 24 24"
                        fill="none"
                        stroke="currentColor"
                        stroke-width="2"
                        stroke-linecap="round"
                        stroke-linejoin="round"
                      >
                        <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2" />
                        <circle cx="9" cy="7" r="4" />
                        <path d="M23 21v-2a4 4 0 0 0-3-3.87" />
                        <path d="M16 3.13a4 4 0 0 1 0 7.75" />
                      </svg>
                    </button>
                    <button 
                      @click="openEditUserModal(user)"
                      class="p-1 rounded-md hover:bg-gray-100" 
                      title="Bearbeiten"
                    >
                      <svg
                        xmlns="http://www.w3.org/2000/svg"
                        class="h-4 w-4"
                        viewBox="0 0 24 24"
                        fill="none"
                        stroke="currentColor"
                        stroke-width="2"
                        stroke-linecap="round"
                        stroke-linejoin="round"
                      >
                        <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7" />
                        <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z" />
                      </svg>
                    </button>
                  </div>
                </td>
              </tr>
              <tr v-if="users.length === 0" class="border-b">
                <td colspan="7" class="py-8 text-center text-gray-500">
                  Keine Benutzer gefunden
                </td>
              </tr>
            </tbody>
          </table>
        </div>
        
        <!-- Pagination controls if needed -->
        <div v-if="pagination.total_pages > 1" class="flex justify-center mt-6">
          <div class="flex space-x-1">
            <button 
              @click="changePage(pagination.current_page - 1)" 
              :disabled="pagination.current_page === 1"
              class="px-3 py-1 rounded border" 
              :class="pagination.current_page === 1 ? 'text-gray-400 cursor-not-allowed' : 'hover:bg-gray-100'"
            >
              ←
            </button>
            <button 
              v-for="page in pagesArray" 
              :key="page" 
              @click="changePage(page)"
              class="px-3 py-1 rounded border" 
              :class="page === pagination.current_page ? 'bg-blue-600 text-white' : 'hover:bg-gray-100'"
            >
              {{ page }}
            </button>
            <button 
              @click="changePage(pagination.current_page + 1)" 
              :disabled="pagination.current_page === pagination.total_pages"
              class="px-3 py-1 rounded border" 
              :class="pagination.current_page === pagination.total_pages ? 'text-gray-400 cursor-not-allowed' : 'hover:bg-gray-100'"
            >
              →
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import usersApi from '../../services/users';

const users = ref([]);
const loading = ref(true);
const error = ref(null);
const searchQuery = ref('');
const searchTimeout = ref(null);

// Pagination state
const pagination = ref({
  current_page: 1,
  page_size: 10,
  total_pages: 1,
  total_items: 0
});

// Compute an array of page numbers to display
const pagesArray = computed(() => {
  const pages = [];
  const totalPages = pagination.value.total_pages;
  const currentPage = pagination.value.current_page;
  
  // Always show first page, last page, current page, and pages around current
  for (let i = 1; i <= totalPages; i++) {
    if (
      i === 1 || // First page
      i === totalPages || // Last page
      (i >= currentPage - 1 && i <= currentPage + 1) // Pages around current
    ) {
      pages.push(i);
    } else if (
      (i === currentPage - 2 && currentPage > 3) ||
      (i === currentPage + 2 && currentPage < totalPages - 2)
    ) {
      // Add ellipsis (represented by 0) if there's a gap
      pages.push(0);
    }
  }
  
  // Remove duplicates and sort
  return [...new Set(pages)].sort((a, b) => a - b);
});

const emit = defineEmits(['user-action']);

// Fetch users from the API
const fetchUsers = async (page = 1, search = '') => {
  loading.value = true;
  error.value = null;
  
  try {
    const filters = {
      page,
      page_size: pagination.value.page_size,
      search
    };
    
    const response = await usersApi.getUsers(filters);
    users.value = response.data.results || response.data;
    
    // Update pagination if the API returns pagination info
    if (response.data.count !== undefined) {
      const totalItems = response.data.count;
      const pageSize = pagination.value.page_size;
      pagination.value = {
        current_page: page,
        page_size: pageSize,
        total_pages: Math.ceil(totalItems / pageSize),
        total_items: totalItems
      };
    }
  } catch (err) {
    console.error('Error fetching users:', err);
    error.value = 'Fehler beim Laden der Benutzer. Bitte versuchen Sie es später erneut.';
  } finally {
    loading.value = false;
  }
};

// Handle user search with debouncing
const handleSearch = () => {
  if (searchTimeout.value) {
    clearTimeout(searchTimeout.value);
  }
  
  searchTimeout.value = setTimeout(() => {
    pagination.value.current_page = 1; // Reset to first page when searching
    fetchUsers(1, searchQuery.value);
  }, 500); // 500ms debounce
};

// Change page
const changePage = (page) => {
  if (page < 1 || page > pagination.value.total_pages) return;
  pagination.value.current_page = page;
  fetchUsers(page, searchQuery.value);
};

// Format user status for display
const formatStatus = (status) => {
  if (!status) return '';
  
  const statusMap = {
    'active': 'Aktiv',
    'inactive': 'Inaktiv',
    'pending': 'Ausstehend',
    'locked': 'Gesperrt'
  };
  
  return statusMap[status] || status;
};

// Handle modal functions (placeholders for now)
const openCreateUserModal = () => {
  emit('user-action', 'create');
};

const openEditUserModal = (user) => {
  emit('user-action', 'edit', user.id);
};

const openAssignGroupsModal = (user) => {
  emit('user-action', 'groups', user.id);
};

// Load users when component mounts
onMounted(() => {
  fetchUsers();
});
</script>
