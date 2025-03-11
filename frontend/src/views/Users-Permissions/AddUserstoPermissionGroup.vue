<template>
  <div class="container mx-auto py-10">
    <div class="mb-6">
      <button @click="$emit('cancel')" class="flex items-center text-blue-600 hover:underline">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 mr-2" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <line x1="19" y1="12" x2="5" y2="12" />
          <polyline points="12 19 5 12 12 5" />
        </svg>
        Zurück zur Gruppenliste
      </button>
    </div>

    <div class="bg-white rounded-lg shadow-md overflow-hidden">
      <div class="p-6">
        <h2 class="text-xl font-semibold mb-2">Benutzer der Gruppe "{{ groupName }}" zuweisen</h2>
        <p class="text-gray-500 mb-6">Wählen Sie die Benutzer aus, die zu dieser Gruppe gehören sollen.</p>
        
        <form @submit.prevent="handleSubmit">
          <div class="space-y-6">
            <div class="relative">
              <svg xmlns="http://www.w3.org/2000/svg" class="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <circle cx="11" cy="11" r="8" />
                <line x1="21" y1="21" x2="16.65" y2="16.65" />
              </svg>
              <input
                type="search"
                v-model="searchTerm"
                placeholder="Benutzer suchen..."
                class="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>

            <div class="overflow-x-auto">
              <table class="w-full">
                <thead>
                  <tr class="border-b">
                    <th class="w-12 py-3 px-4">
                      <span class="sr-only">Auswählen</span>
                    </th>
                    <th class="text-left py-3 px-4">Benutzername</th>
                    <th class="text-left py-3 px-4">Name</th>
                    <th class="text-left py-3 px-4">E-Mail</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="user in filteredUsers" :key="user.id" class="border-b hover:bg-gray-50">
                    <td class="py-3 px-4">
                      <input 
                        type="checkbox"
                        :id="`user-${user.id}`"
                        :value="user.id"
                        v-model="selectedUsers"
                        class="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                      />
                    </td>
                    <td class="py-3 px-4 font-medium">{{ user.username }}</td>
                    <td class="py-3 px-4">{{ user.name }}</td>
                    <td class="py-3 px-4">{{ user.email }}</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>

          <div class="flex justify-between mt-8">
            <button 
              type="button" 
              @click="$emit('cancel')"
              class="px-4 py-2 border border-gray-300 rounded-md hover:bg-gray-50"
            >
              Abbrechen
            </button>
            <button type="submit" class="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700">
              Änderungen speichern
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue';

const props = defineProps({
  groupId: {
    type: String,
    default: null
  }
});

const emit = defineEmits(['cancel', 'save']);

const groupName = ref('');
const searchTerm = ref('');
const selectedUsers = ref([]);

// In einer echten Anwendung würden diese Daten vom Django-Backend abgerufen werden
const allUsers = ref([
  { id: 1, username: "anna.mueller", name: "Anna Müller", email: "anna.mueller@example.com", inGroup: true },
  { id: 2, username: "thomas.schmidt", name: "Thomas Schmidt", email: "thomas.schmidt@example.com", inGroup: true },
  { id: 3, username: "lisa.wagner", name: "Lisa Wagner", email: "lisa.wagner@example.com", inGroup: true },
  { id: 4, username: "michael.becker", name: "Michael Becker", email: "michael.becker@example.com", inGroup: false },
  { id: 5, username: "sarah.hoffmann", name: "Sarah Hoffmann", email: "sarah.hoffmann@example.com", inGroup: false },
  { id: 6, username: "markus.weber", name: "Markus Weber", email: "markus.weber@example.com", inGroup: false },
  { id: 7, username: "julia.schneider", name: "Julia Schneider", email: "julia.schneider@example.com", inGroup: false },
  { id: 8, username: "stefan.fischer", name: "Stefan Fischer", email: "stefan.fischer@example.com", inGroup: false },
]);

// Benutzer nach Suchbegriff filtern
const filteredUsers = computed(() => {
  if (!searchTerm.value) {
    return allUsers.value;
  }
  
  const term = searchTerm.value.toLowerCase();
  return allUsers.value.filter(user => 
    user.name.toLowerCase().includes(term) || 
    user.username.toLowerCase().includes(term) ||
    user.email.toLowerCase().includes(term)
  );
});

const loadGroupData = () => {
  // In einer echten Anwendung würden die Gruppendaten vom Django-Backend abgerufen werden
  // Für Demo-Zwecke verwenden wir hartcodierte Daten
  if (props.groupId === '2') {
    groupName.value = 'Buchhaltung';
  } else if (props.groupId === '1') {
    groupName.value = 'Administratoren';
  } else if (props.groupId === '3') {
    groupName.value = 'Vertrieb';
  } else if (props.groupId === '4') {
    groupName.value = 'Lager';
  }
  
  // Initial ausgewählte Benutzer setzen
  selectedUsers.value = allUsers.value
    .filter(user => user.inGroup)
    .map(user => user.id);
};

// Gruppendaten laden, wenn sich die groupId ändert
watch(() => props.groupId, () => {
  loadGroupData();
});

// Gruppendaten beim Mounten laden
onMounted(() => {
  loadGroupData();
});

const handleSubmit = () => {
  // In einer echten Anwendung würden die Daten an das Django-Backend gesendet werden
  console.log({
    groupId: props.groupId,
    userIds: selectedUsers.value
  });
  
  // Für Demo-Zwecke nur eine Meldung anzeigen und weiterleiten
  alert('Benutzer wurden der Gruppe zugewiesen!');
  emit('save');
};
</script>