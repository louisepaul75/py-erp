<template>
  <div>
    <!-- User Stats Cards -->
    <v-row class="mb-6">
      <v-col cols="12" sm="6" md="3">
        <v-card outlined>
          <v-card-text class="d-flex flex-column align-center">
            <div class="text-h4 font-weight-bold">{{ stats.active || 0 }}</div>
            <div class="text-subtitle-1 text-medium-emphasis">Aktive Benutzer</div>
          </v-card-text>
        </v-card>
      </v-col>
      
      <v-col cols="12" sm="6" md="3">
        <v-card outlined>
          <v-card-text class="d-flex flex-column align-center">
            <div class="text-h4 font-weight-bold">{{ stats.inactive || 0 }}</div>
            <div class="text-subtitle-1 text-medium-emphasis">Inaktive Benutzer</div>
          </v-card-text>
        </v-card>
      </v-col>
      
      <v-col cols="12" sm="6" md="3">
        <v-card outlined>
          <v-card-text class="d-flex flex-column align-center">
            <div class="text-h4 font-weight-bold">{{ stats.admins || 0 }}</div>
            <div class="text-subtitle-1 text-medium-emphasis">Administratoren</div>
          </v-card-text>
        </v-card>
      </v-col>
      
      <v-col cols="12" sm="6" md="3">
        <v-card outlined>
          <v-card-text class="d-flex flex-column align-center">
            <div class="text-h4 font-weight-bold">{{ groupCount || 0 }}</div>
            <div class="text-subtitle-1 text-medium-emphasis">Benutzergruppen</div>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <!-- Management Buttons -->
    <v-row class="mb-6">
      <v-col cols="12" md="4">
        <v-card outlined height="100%">
          <v-card-title>
            <v-icon icon="mdi-account-multiple" class="mr-2"></v-icon>
            Benutzer
          </v-card-title>
          <v-card-text>
            <p class="mb-4">Verwalten Sie Benutzerkonten, Profile und Zugriffsrechte.</p>
          </v-card-text>
          <v-card-actions>
            <v-btn 
              color="primary" 
              variant="outlined" 
              block
              prepend-icon="mdi-account-cog"
              @click="activeSection = 'users'"
            >
              Benutzer verwalten
            </v-btn>
          </v-card-actions>
        </v-card>
      </v-col>
      
      <v-col cols="12" md="4">
        <v-card outlined height="100%">
          <v-card-title>
            <v-icon icon="mdi-account-group" class="mr-2"></v-icon>
            Gruppen
          </v-card-title>
          <v-card-text>
            <p class="mb-4">Erstellen und verwalten Sie Benutzergruppen und deren Rechte.</p>
          </v-card-text>
          <v-card-actions>
            <v-btn 
              color="primary" 
              variant="outlined" 
              block 
              prepend-icon="mdi-account-group"
              @click="activeSection = 'groups'"
            >
              Gruppen verwalten
            </v-btn>
          </v-card-actions>
        </v-card>
      </v-col>
      
      <v-col cols="12" md="4">
        <v-card outlined height="100%">
          <v-card-title>
            <v-icon icon="mdi-shield-account" class="mr-2"></v-icon>
            Rollen
          </v-card-title>
          <v-card-text>
            <p class="mb-4">Konfigurieren Sie Systemrollen und deren Berechtigungen.</p>
          </v-card-text>
          <v-card-actions>
            <v-btn 
              color="primary" 
              variant="outlined" 
              block
              prepend-icon="mdi-shield-account"
              @click="activeSection = 'roles'"
            >
              Rollen verwalten
            </v-btn>
          </v-card-actions>
        </v-card>
      </v-col>
    </v-row>

    <!-- Dynamic Content Section -->
    <v-card v-if="activeSection === 'users'">
      <v-card-title class="d-flex justify-space-between align-center">
        <div>
          <v-icon icon="mdi-account-multiple" class="mr-2"></v-icon>
          Benutzerverwaltung
        </div>
        <v-btn 
          color="primary" 
          prepend-icon="mdi-account-plus"
          @click="showAddUserDialog = true"
        >
          Benutzer hinzufügen
        </v-btn>
      </v-card-title>
      
      <v-card-text>
        <v-text-field
          v-model="userSearch"
          label="Benutzer suchen..."
          prepend-inner-icon="mdi-magnify"
          single-line
          hide-details
          class="mb-4"
        ></v-text-field>
        
        <v-data-table
          :headers="userHeaders"
          :items="recentUsers"
          :search="userSearch"
          :loading="loading"
          class="elevation-1"
        >
          <template v-slot:item="{ item }">
            <tr>
              <td>{{ item.username }}</td>
              <td>{{ item.full_name }}</td>
              <td>{{ item.email }}</td>
              <td>
                <v-chip
                  :color="item.is_active ? 'success' : 'error'"
                  size="small"
                  class="text-white"
                >
                  {{ item.is_active ? 'Aktiv' : 'Inaktiv' }}
                </v-chip>
              </td>
              <td>{{ item.date_joined }}</td>
              <td>
                <v-icon
                  icon="mdi-pencil"
                  size="small"
                  class="mr-2"
                  @click="editUser(item)"
                ></v-icon>
                <v-icon
                  icon="mdi-lock-reset"
                  size="small"
                  class="mr-2"
                  @click="resetUserPassword(item)"
                ></v-icon>
                <v-icon
                  icon="mdi-delete"
                  size="small"
                  color="error"
                  @click="deleteUser(item)"
                ></v-icon>
              </td>
            </tr>
          </template>
          
          <template v-slot:no-data>
            <p class="text-center my-4">Keine Benutzerdaten verfügbar</p>
          </template>
        </v-data-table>
      </v-card-text>
    </v-card>
    
    <v-card v-else-if="activeSection === 'groups'" class="mt-6">
      <v-card-title>
        <v-icon icon="mdi-account-group" class="mr-2"></v-icon>
        Gruppenverwaltung
      </v-card-title>
      <v-card-text>
        <v-alert type="info" variant="tonal">
          Gruppenmanagement wird hier implementiert.
        </v-alert>
      </v-card-text>
    </v-card>
    
    <v-card v-else-if="activeSection === 'roles'" class="mt-6">
      <v-card-title>
        <v-icon icon="mdi-shield-account" class="mr-2"></v-icon>
        Rollenverwaltung
      </v-card-title>
      <v-card-text>
        <v-alert type="info" variant="tonal">
          Rollenverwaltung wird hier implementiert.
        </v-alert>
      </v-card-text>
    </v-card>
    
    <!-- Recent Users Section (shown when no section is active) -->
    <v-card v-else class="mt-6">
      <v-card-title class="d-flex justify-space-between align-center">
        <div>
          <v-icon icon="mdi-account-clock" class="mr-2"></v-icon>
          Neueste Benutzer
        </div>
        <v-btn 
          color="primary" 
          variant="text"
          @click="activeSection = 'users'"
        >
          Alle anzeigen
        </v-btn>
      </v-card-title>
      
      <v-card-text>
        <v-data-table
          :headers="userHeaders"
          :items="recentUsers.slice(0, 5)"
          :loading="loading"
          hide-default-footer
          class="elevation-1"
        >
          <template v-slot:item="{ item }">
            <tr>
              <td>{{ item.username }}</td>
              <td>{{ item.full_name }}</td>
              <td>{{ item.email }}</td>
              <td>
                <v-chip
                  :color="item.is_active ? 'success' : 'error'"
                  size="small"
                  class="text-white"
                >
                  {{ item.is_active ? 'Aktiv' : 'Inaktiv' }}
                </v-chip>
              </td>
              <td>{{ item.date_joined }}</td>
              <td>
                <v-icon
                  icon="mdi-pencil"
                  size="small"
                  class="mr-2"
                  @click="editUser(item)"
                ></v-icon>
              </td>
            </tr>
          </template>
          
          <template v-slot:no-data>
            <p class="text-center my-4">Keine Benutzerdaten verfügbar</p>
          </template>
        </v-data-table>
      </v-card-text>
    </v-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import usersApi from '../services/users';

const userCount = ref(0);
const groupCount = ref(0);
const roleCount = ref(0);
const recentUsers = ref([]);
const loading = ref(true);
const userSearch = ref('');
const activeSection = ref('');
const showAddUserDialog = ref(false);

const stats = ref({
  active: 0,
  inactive: 0,
  admins: 0,
  twoFactor: 0
});

const userHeaders = [
  { title: 'Benutzername', key: 'username' },
  { title: 'Name', key: 'full_name', value: item => `${item.first_name} ${item.last_name}` },
  { title: 'E-Mail', key: 'email' },
  { title: 'Status', key: 'is_active' },
  { title: 'Erstellt am', key: 'date_joined' },
  { title: 'Aktionen', key: 'actions', sortable: false }
];

// User management functions
const editUser = (user) => {
  console.log('Edit user:', user);
  // Implement edit functionality
};

const resetUserPassword = (user) => {
  console.log('Reset password for user:', user);
  // Implement password reset functionality
};

const deleteUser = (user) => {
  console.log('Delete user:', user);
  // Implement delete functionality
};

// Load dashboard data
const loadDashboardData = async () => {
  loading.value = true;
  
  try {
    // Get user count and recent users
    const usersResponse = await usersApi.getUsers({
      page: 1,
      page_size: 10,
      ordering: '-date_joined'
    });
    
    recentUsers.value = usersResponse.data.results || [];
    userCount.value = usersResponse.data.count || recentUsers.value.length;
    
    // Map user data for display
    recentUsers.value = recentUsers.value.map(user => ({
      ...user,
      full_name: `${user.first_name || ''} ${user.last_name || ''}`.trim() || '-',
      date_joined: new Date(user.date_joined).toLocaleDateString('de-DE')
    }));
    
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

<style scoped>
.v-card {
  margin-bottom: 16px;
}
</style> 