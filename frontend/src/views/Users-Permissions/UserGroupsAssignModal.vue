<template>
  <div v-if="show" class="fixed inset-0 z-50 overflow-y-auto" aria-labelledby="modal-title" role="dialog" aria-modal="true">
    <div class="flex items-end justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0">
      <!-- Background overlay -->
      <div class="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity" @click="$emit('close')"></div>
      
      <!-- Modal panel -->
      <div class="inline-block align-bottom bg-white rounded-lg text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-2xl sm:w-full">
        <!-- Close button -->
        <button 
          @click="$emit('close')" 
          class="absolute top-3 right-3 text-gray-400 hover:text-gray-500"
          aria-label="Close"
        >
          <svg class="h-6 w-6" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
        
        <!-- Modal content -->
        <div class="p-6">
          <h2 class="text-xl font-semibold mb-6">Gruppen zuweisen</h2>
          
          <div v-if="!user" class="py-4 text-center">
            <p class="text-gray-500">Benutzer wurde nicht gefunden</p>
          </div>
          
          <template v-else>
            <div class="mb-6">
              <p class="text-gray-700">Benutzer: <span class="font-medium">{{ user.username }}</span></p>
              <p class="text-gray-700">Name: <span class="font-medium">{{ user.first_name }} {{ user.last_name }}</span></p>
            </div>
            
            <div v-if="loading" class="py-4 text-center">
              <p class="text-gray-500">Gruppen werden geladen...</p>
            </div>
            
            <div v-else-if="error" class="py-4 text-center">
              <p class="text-red-500">{{ error }}</p>
              <button 
                @click="loadGroups" 
                class="mt-2 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
              >
                Erneut versuchen
              </button>
            </div>
            
            <div v-else>
              <!-- Available groups -->
              <div class="bg-gray-50 p-4 rounded-md mb-6">
                <h3 class="text-lg font-medium mb-4">Verfügbare Gruppen</h3>
                
                <div v-if="groups.length === 0" class="text-center py-4">
                  <p class="text-gray-500">Keine Gruppen verfügbar</p>
                </div>
                
                <div v-else>
                  <div class="mb-3">
                    <input 
                      v-model="groupFilter" 
                      type="text" 
                      placeholder="Gruppen filtern..." 
                      class="w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    >
                  </div>
                  
                  <div class="grid grid-cols-1 sm:grid-cols-2 gap-3 max-h-60 overflow-y-auto">
                    <div 
                      v-for="group in filteredGroups" 
                      :key="group.id" 
                      class="flex items-center"
                    >
                      <input 
                        :id="`group-${group.id}`" 
                        type="checkbox"
                        :value="group.id"
                        v-model="selectedGroups"
                        class="h-4 w-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                      >
                      <label :for="`group-${group.id}`" class="ml-2 block text-sm text-gray-700">
                        {{ group.name }}
                      </label>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </template>
          
          <!-- Actions -->
          <div class="flex justify-end space-x-4">
            <button 
              type="button" 
              @click="$emit('close')" 
              class="px-4 py-2 border rounded-md hover:bg-gray-50"
            >
              Abbrechen
            </button>
            <button 
              @click="saveGroups" 
              class="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
              :disabled="saving || !user"
            >
              {{ saving ? 'Wird gespeichert...' : 'Speichern' }}
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue';
import usersApi from '../../services/users';

const props = defineProps({
  show: {
    type: Boolean,
    default: false
  },
  userId: {
    type: [Number, String],
    default: null
  }
});

const emit = defineEmits(['close', 'save']);

const user = ref(null);
const groups = ref([]);
const selectedGroups = ref([]);
const groupFilter = ref('');
const loading = ref(false);
const error = ref(null);
const saving = ref(false);

// Filtered groups based on search query
const filteredGroups = computed(() => {
  if (!groupFilter.value) return groups.value;
  
  const query = groupFilter.value.toLowerCase();
  return groups.value.filter(group => 
    group.name.toLowerCase().includes(query)
  );
});

// Load user data
const loadUser = async () => {
  if (!props.userId) {
    user.value = null;
    return;
  }
  
  loading.value = true;
  error.value = null;
  
  try {
    const response = await usersApi.getUser(props.userId);
    user.value = response.data;
    
    // Initialize selected groups
    selectedGroups.value = user.value.groups?.map(group => group.id) || [];
  } catch (err) {
    console.error('Error loading user:', err);
    error.value = 'Fehler beim Laden des Benutzers';
    user.value = null;
  } finally {
    loading.value = false;
  }
};

// Load all available groups
const loadGroups = async () => {
  loading.value = true;
  error.value = null;
  
  try {
    const response = await usersApi.getGroups();
    groups.value = response.data.results || response.data;
  } catch (err) {
    console.error('Error loading groups:', err);
    error.value = 'Fehler beim Laden der Gruppen';
  } finally {
    loading.value = false;
  }
};

// Save user group assignments
const saveGroups = async () => {
  if (!user.value) return;
  
  saving.value = true;
  
  try {
    // Assign the selected groups to the user
    await usersApi.assignGroups(user.value.id, selectedGroups.value);
    
    // Update the user object with the new groups
    const updatedUser = { ...user.value };
    updatedUser.groups = groups.value
      .filter(group => selectedGroups.value.includes(group.id))
      .map(group => ({ id: group.id, name: group.name }));
    
    // Emit save event
    emit('save', updatedUser);
  } catch (err) {
    console.error('Error saving groups:', err);
    alert('Fehler beim Speichern der Gruppen');
  } finally {
    saving.value = false;
  }
};

// Watch for modal open/close
watch(() => props.show, (newVal) => {
  if (newVal) {
    loadUser();
    loadGroups();
  }
});

// Load initial data
onMounted(() => {
  if (props.show && props.userId) {
    loadUser();
    loadGroups();
  }
});
</script> 