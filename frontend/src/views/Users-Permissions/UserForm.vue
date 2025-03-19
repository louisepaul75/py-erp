<template>
  <div class="p-6">
    <h2 class="text-xl font-semibold mb-6">{{ isEditing ? 'Benutzer bearbeiten' : 'Neuer Benutzer' }}</h2>
    
    <form @submit.prevent="submitForm" class="space-y-6">
      <!-- Basic Information Section -->
      <div class="bg-gray-50 p-4 rounded-md">
        <h3 class="text-lg font-medium mb-4">Benutzerdaten</h3>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div class="col-span-2 md:col-span-1">
            <label class="block text-sm font-medium text-gray-700 mb-1">Benutzername*</label>
            <input 
              v-model="formData.username" 
              type="text" 
              class="w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              :disabled="isEditing"
              required
            >
            <p v-if="errors.username" class="mt-1 text-sm text-red-600">{{ errors.username }}</p>
          </div>
          
          <div class="col-span-2 md:col-span-1">
            <label class="block text-sm font-medium text-gray-700 mb-1">E-Mail*</label>
            <input 
              v-model="formData.email" 
              type="email" 
              class="w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              required
            >
            <p v-if="errors.email" class="mt-1 text-sm text-red-600">{{ errors.email }}</p>
          </div>
          
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Vorname</label>
            <input 
              v-model="formData.first_name" 
              type="text" 
              class="w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
          </div>
          
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Nachname</label>
            <input 
              v-model="formData.last_name" 
              type="text" 
              class="w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
          </div>
        </div>
        
        <div v-if="!isEditing" class="mt-6 grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Passwort*</label>
            <input 
              v-model="formData.password" 
              type="password" 
              class="w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              :required="!isEditing"
            >
            <p v-if="errors.password" class="mt-1 text-sm text-red-600">{{ errors.password }}</p>
          </div>
          
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Passwort bestätigen*</label>
            <input 
              v-model="formData.password_confirm" 
              type="password" 
              class="w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              :required="!isEditing"
            >
            <p v-if="errors.password_confirm" class="mt-1 text-sm text-red-600">{{ errors.password_confirm }}</p>
          </div>
        </div>
        
        <div class="mt-6">
          <div class="flex items-center justify-between">
            <div class="flex items-center">
              <input 
                id="is_active" 
                v-model="formData.is_active" 
                type="checkbox" 
                class="h-4 w-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
              >
              <label for="is_active" class="ml-2 block text-sm text-gray-700">Aktiv</label>
            </div>
            
            <div class="flex items-center">
              <input 
                id="is_staff" 
                v-model="formData.is_staff" 
                type="checkbox" 
                class="h-4 w-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
              >
              <label for="is_staff" class="ml-2 block text-sm text-gray-700">Mitarbeiter (Staff)</label>
            </div>
            
            <div class="flex items-center">
              <input 
                id="is_superuser" 
                v-model="formData.is_superuser" 
                type="checkbox" 
                class="h-4 w-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
              >
              <label for="is_superuser" class="ml-2 block text-sm text-gray-700">Administrator</label>
            </div>
          </div>
        </div>
      </div>
      
      <!-- Profile Information Section -->
      <div class="bg-gray-50 p-4 rounded-md">
        <h3 class="text-lg font-medium mb-4">Profil-Informationen</h3>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Abteilung</label>
            <input 
              v-model="formData.profile.department" 
              type="text" 
              class="w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
          </div>
          
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Position</label>
            <input 
              v-model="formData.profile.position" 
              type="text" 
              class="w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
          </div>
          
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Telefon</label>
            <input 
              v-model="formData.profile.phone" 
              type="text" 
              class="w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
          </div>
          
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Sprache</label>
            <select 
              v-model="formData.profile.language_preference" 
              class="w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="de">Deutsch</option>
              <option value="en">Englisch</option>
              <option value="fr">Französisch</option>
              <option value="es">Spanisch</option>
            </select>
          </div>
          
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">Status</label>
            <select 
              v-model="formData.profile.status" 
              class="w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="active">Aktiv</option>
              <option value="inactive">Inaktiv</option>
              <option value="pending">Ausstehend</option>
              <option value="locked">Gesperrt</option>
            </select>
          </div>
          
          <div>
            <div class="flex items-center mt-7">
              <input 
                id="two_factor_enabled" 
                v-model="formData.profile.two_factor_enabled" 
                type="checkbox" 
                class="h-4 w-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
              >
              <label for="two_factor_enabled" class="ml-2 block text-sm text-gray-700">
                Zwei-Faktor-Authentifizierung aktivieren
              </label>
            </div>
          </div>
        </div>
      </div>
      
      <!-- Group Selection Section -->
      <div class="bg-gray-50 p-4 rounded-md">
        <h3 class="text-lg font-medium mb-4">Gruppen</h3>
        <div v-if="loading.groups" class="text-center py-4">
          <p class="text-gray-500">Gruppen werden geladen...</p>
        </div>
        <div v-else-if="groups.length === 0" class="text-center py-4">
          <p class="text-gray-500">Keine Gruppen verfügbar</p>
        </div>
        <div v-else class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-3">
          <div v-for="group in groups" :key="group.id" class="flex items-center">
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
      
      <!-- Form Actions -->
      <div class="flex justify-end space-x-4">
        <button 
          type="button" 
          @click="$emit('cancel')" 
          class="px-4 py-2 border rounded-md hover:bg-gray-50"
        >
          Abbrechen
        </button>
        <button 
          type="submit" 
          class="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
          :disabled="loading.submit"
        >
          {{ loading.submit ? 'Wird gespeichert...' : (isEditing ? 'Speichern' : 'Erstellen') }}
        </button>
      </div>
    </form>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue';
import usersApi from '../../services/users';

const props = defineProps({
  user: {
    type: Object,
    default: null
  }
});

const emit = defineEmits(['save', 'cancel']);

// Check if we're editing an existing user or creating a new one
const isEditing = computed(() => !!props.user);

// Form data with default values
const formData = ref({
  username: '',
  email: '',
  first_name: '',
  last_name: '',
  is_active: true,
  is_staff: false,
  is_superuser: false,
  password: '',
  password_confirm: '',
  profile: {
    department: '',
    position: '',
    phone: '',
    language_preference: 'de',
    status: 'active',
    two_factor_enabled: false
  }
});

// Validation errors
const errors = ref({});

// Loading states
const loading = ref({
  submit: false,
  groups: false
});

// Available groups
const groups = ref([]);

// Selected groups
const selectedGroups = ref([]);

// Load available groups
const loadGroups = async () => {
  loading.value.groups = true;
  try {
    const response = await usersApi.getGroups();
    groups.value = response.data.results || response.data;
  } catch (error) {
    console.error('Error loading groups:', error);
    // Handle error - maybe show a notification
  } finally {
    loading.value.groups = false;
  }
};

// Initialize form if editing an existing user
const initForm = () => {
  if (props.user) {
    // Copy user data to form
    formData.value = {
      username: props.user.username || '',
      email: props.user.email || '',
      first_name: props.user.first_name || '',
      last_name: props.user.last_name || '',
      is_active: props.user.is_active ?? true,
      is_staff: props.user.is_staff ?? false,
      is_superuser: props.user.is_superuser ?? false,
      password: '',
      password_confirm: '',
      profile: {
        department: props.user.profile?.department || '',
        position: props.user.profile?.position || '',
        phone: props.user.profile?.phone || '',
        language_preference: props.user.profile?.language_preference || 'de',
        status: props.user.profile?.status || 'active',
        two_factor_enabled: props.user.profile?.two_factor_enabled ?? false
      }
    };
    
    // Set selected groups
    selectedGroups.value = props.user.groups?.map(group => group.id) || [];
  }
};

// Validate form
const validateForm = () => {
  errors.value = {};
  let isValid = true;
  
  // Username validation
  if (!formData.value.username.trim()) {
    errors.value.username = 'Benutzername ist erforderlich';
    isValid = false;
  }
  
  // Email validation
  if (!formData.value.email.trim()) {
    errors.value.email = 'E-Mail ist erforderlich';
    isValid = false;
  } else if (!/\S+@\S+\.\S+/.test(formData.value.email)) {
    errors.value.email = 'Bitte geben Sie eine gültige E-Mail-Adresse ein';
    isValid = false;
  }
  
  // Password validation (only for new users)
  if (!isEditing.value) {
    if (!formData.value.password) {
      errors.value.password = 'Passwort ist erforderlich';
      isValid = false;
    } else if (formData.value.password.length < 8) {
      errors.value.password = 'Passwort muss mindestens 8 Zeichen lang sein';
      isValid = false;
    }
    
    if (formData.value.password !== formData.value.password_confirm) {
      errors.value.password_confirm = 'Passwörter stimmen nicht überein';
      isValid = false;
    }
  }
  
  return isValid;
};

// Submit form
const submitForm = async () => {
  if (!validateForm()) return;
  
  loading.value.submit = true;
  
  try {
    // Prepare user data for submission
    const userData = {
      username: formData.value.username,
      email: formData.value.email,
      first_name: formData.value.first_name,
      last_name: formData.value.last_name,
      is_active: formData.value.is_active,
      is_staff: formData.value.is_staff,
      is_superuser: formData.value.is_superuser,
      profile: {
        department: formData.value.profile.department,
        position: formData.value.profile.position,
        phone: formData.value.profile.phone,
        language_preference: formData.value.profile.language_preference,
        status: formData.value.profile.status,
        two_factor_enabled: formData.value.profile.two_factor_enabled
      }
    };
    
    // Add password only for new users
    if (!isEditing.value) {
      userData.password = formData.value.password;
    }
    
    let response;
    
    if (isEditing.value) {
      // Update existing user
      response = await usersApi.updateUser(props.user.id, userData);
      
      // Update user groups if they've changed
      const currentGroups = props.user.groups?.map(g => g.id) || [];
      const hasGroupChanges = JSON.stringify(currentGroups.sort()) !== JSON.stringify([...selectedGroups.value].sort());
      
      if (hasGroupChanges) {
        await usersApi.assignGroups(props.user.id, selectedGroups.value);
      }
    } else {
      // Create new user
      response = await usersApi.createUser(userData);
      
      // Assign groups to the new user if any selected
      if (selectedGroups.value.length > 0) {
        await usersApi.assignGroups(response.data.id, selectedGroups.value);
      }
    }
    
    // Emit save event with the saved user
    emit('save', response.data);
  } catch (error) {
    console.error('Error saving user:', error);
    
    // Handle API validation errors
    if (error.response?.data) {
      const apiErrors = error.response.data;
      
      // Map API errors to our form errors
      Object.keys(apiErrors).forEach(key => {
        if (key === 'profile') {
          Object.keys(apiErrors.profile).forEach(profileKey => {
            errors.value[`profile.${profileKey}`] = apiErrors.profile[profileKey][0];
          });
        } else {
          errors.value[key] = Array.isArray(apiErrors[key]) ? apiErrors[key][0] : apiErrors[key];
        }
      });
    } else {
      // Generic error
      alert('Ein Fehler ist aufgetreten. Bitte versuchen Sie es später erneut.');
    }
  } finally {
    loading.value.submit = false;
  }
};

// Watch for user prop changes to update form
watch(() => props.user, initForm, { immediate: true });

// Load data when component is mounted
onMounted(() => {
  loadGroups();
});
</script> 