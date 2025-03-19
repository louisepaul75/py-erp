<template>
  <div>
    <div class="container mx-auto py-10">
      <h1 class="text-3xl font-bold mb-8">Benutzer & Berechtigungen</h1>
      
      <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-10">
        <!-- Users Card -->
        <div class="bg-white rounded-lg shadow-md p-6 flex flex-col">
          <div class="flex justify-between items-center mb-6">
            <h2 class="text-xl font-semibold">Benutzer</h2>
            <span class="text-sm bg-blue-100 text-blue-800 py-1 px-2 rounded-full">{{ userCount || 0 }}</span>
          </div>
          <p class="text-gray-600 mb-4">Benutzerverwaltung und Profildetails</p>
          <router-link 
            to="/users-permissions/users" 
            class="mt-auto px-4 py-2 text-center bg-blue-600 text-white rounded-md hover:bg-blue-700"
          >
            Benutzer verwalten
          </router-link>
        </div>
        
        <!-- Groups Card -->
        <div class="bg-white rounded-lg shadow-md p-6 flex flex-col">
          <div class="flex justify-between items-center mb-6">
            <h2 class="text-xl font-semibold">Gruppen</h2>
            <span class="text-sm bg-green-100 text-green-800 py-1 px-2 rounded-full">{{ groupCount || 0 }}</span>
          </div>
          <p class="text-gray-600 mb-4">Verwalten von Benutzergruppen und Berechtigungen</p>
          <router-link 
            to="/users-permissions/groups" 
            class="mt-auto px-4 py-2 text-center bg-blue-600 text-white rounded-md hover:bg-blue-700"
          >
            Gruppen verwalten
          </router-link>
        </div>
        
        <!-- Roles Card -->
        <div class="bg-white rounded-lg shadow-md p-6 flex flex-col">
          <div class="flex justify-between items-center mb-6">
            <h2 class="text-xl font-semibold">Rollen</h2>
            <span class="text-sm bg-purple-100 text-purple-800 py-1 px-2 rounded-full">{{ roleCount || 0 }}</span>
          </div>
          <p class="text-gray-600 mb-4">Systemrollen für erweiterte Berechtigungen</p>
          <router-link 
            to="/users-permissions/roles" 
            class="mt-auto px-4 py-2 text-center bg-blue-600 text-white rounded-md hover:bg-blue-700"
          >
            Rollen verwalten
          </router-link>
        </div>
      </div>
      
      <!-- Stats Row -->
      <div class="bg-white rounded-lg shadow-md p-6 mb-10">
        <h2 class="text-xl font-semibold mb-6">Benutzerstatistiken</h2>
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <div class="p-4 border rounded-lg">
            <p class="text-sm text-gray-500">Aktive Benutzer</p>
            <p class="text-2xl font-bold">{{ stats.active || 0 }}</p>
          </div>
          
          <div class="p-4 border rounded-lg">
            <p class="text-sm text-gray-500">Inaktive Benutzer</p>
            <p class="text-2xl font-bold">{{ stats.inactive || 0 }}</p>
          </div>
          
          <div class="p-4 border rounded-lg">
            <p class="text-sm text-gray-500">Administratoren</p>
            <p class="text-2xl font-bold">{{ stats.admins || 0 }}</p>
          </div>
          
          <div class="p-4 border rounded-lg">
            <p class="text-sm text-gray-500">Benutzer mit 2FA</p>
            <p class="text-2xl font-bold">{{ stats.twoFactor || 0 }}</p>
          </div>
        </div>
      </div>
      
      <!-- Recent Users Table -->
      <div class="bg-white rounded-lg shadow-md p-6">
        <div class="flex justify-between items-center mb-6">
          <h2 class="text-xl font-semibold">Neueste Benutzer</h2>
          <router-link 
            to="/users-permissions/users" 
            class="text-blue-600 hover:text-blue-800"
          >
            Alle anzeigen
          </router-link>
        </div>
        
        <div v-if="loading" class="py-10 text-center">
          <p class="text-gray-500">Benutzer werden geladen...</p>
        </div>
        
        <div v-else-if="recentUsers.length === 0" class="py-10 text-center">
          <p class="text-gray-500">Keine Benutzer gefunden</p>
        </div>
        
        <div v-else class="overflow-x-auto">
          <table class="w-full">
            <thead>
              <tr class="border-b">
                <th class="text-left py-3 px-4">Benutzername</th>
                <th class="text-left py-3 px-4">Name</th>
                <th class="text-left py-3 px-4">E-Mail</th>
                <th class="text-left py-3 px-4">Abteilung</th>
                <th class="text-left py-3 px-4">Status</th>
                <th class="text-left py-3 px-4">Erstellt am</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="user in recentUsers" :key="user.id" class="border-b hover:bg-gray-50">
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
                <td class="py-3 px-4">{{ formatDate(user.date_joined) }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import usersApi from '../../services/users';

const userCount = ref(0);
const groupCount = ref(0);
const roleCount = ref(0);
const recentUsers = ref([]);
const loading = ref(true);
const stats = ref({
  active: 0,
  inactive: 0,
  admins: 0,
  twoFactor: 0
});

// Format status for display
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

// Format date for display
const formatDate = (dateString) => {
  if (!dateString) return '-';
  
  const date = new Date(dateString);
  return new Intl.DateTimeFormat('de-DE', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit'
  }).format(date);
};

// Load dashboard data
const loadDashboardData = async () => {
  loading.value = true;
  
  try {
    // Get user count and recent users
    const usersResponse = await usersApi.getUsers({
      page: 1,
      page_size: 5,
      ordering: '-date_joined'
    });
    
    recentUsers.value = usersResponse.data.results || [];
    userCount.value = usersResponse.data.count || recentUsers.value.length;
    
    // Get group count
    const groupsResponse = await usersApi.getGroups();
    groupCount.value = groupsResponse.data.count || groupsResponse.data.length;
    
    // Get role count
    const rolesResponse = await usersApi.getRoles();
    roleCount.value = rolesResponse.data.count || rolesResponse.data.length;
    
    // Get user stats
    // Count users by status
    const users = usersResponse.data.results || [];
    stats.value = {
      active: users.filter(u => u.is_active).length,
      inactive: users.filter(u => !u.is_active).length,
      admins: users.filter(u => u.is_superuser).length,
      twoFactor: users.filter(u => u.profile?.two_factor_enabled).length
    };
    
    // If we have pagination data, get actual counts for stats
    if (usersResponse.data.count) {
      // Get count of users with is_active=true
      const activeResponse = await usersApi.getUsers({ is_active: true, page_size: 1 });
      stats.value.active = activeResponse.data.count;
      
      // Get count of users with is_active=false
      const inactiveResponse = await usersApi.getUsers({ is_active: false, page_size: 1 });
      stats.value.inactive = inactiveResponse.data.count;
      
      // Get count of users with is_superuser=true
      const adminsResponse = await usersApi.getUsers({ is_superuser: true, page_size: 1 });
      stats.value.admins = adminsResponse.data.count;
      
      // For two-factor, we don't make another request as it would be too expensive
    }
  } catch (error) {
    console.error('Error loading dashboard data:', error);
  } finally {
    loading.value = false;
  }
};

// Load data when component mounts
onMounted(() => {
  loadDashboardData();
});
</script>
