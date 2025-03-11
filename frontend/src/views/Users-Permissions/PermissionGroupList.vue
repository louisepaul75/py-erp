<template>
  <div class="container mx-auto py-10">
    <div class="flex justify-between items-center mb-6">
      <h1 class="text-3xl font-bold">Berechtigungsgruppen</h1>
      <button 
        @click="$emit('group-action', 'new')"
        class="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
      >
        Neue Gruppe
      </button>
    </div>

    <div class="bg-white rounded-lg shadow-md overflow-hidden">
      <div class="p-6">
        <h2 class="text-xl font-semibold mb-4">Alle Gruppen</h2>
        <div class="overflow-x-auto">
          <table class="w-full">
            <thead>
              <tr class="border-b">
                <th class="text-left py-3 px-4">Name</th>
                <th class="text-left py-3 px-4">Benutzer</th>
                <th class="text-left py-3 px-4">Berechtigungen</th>
                <th class="text-right py-3 px-4">Aktionen</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="group in groups" :key="group.id" class="border-b hover:bg-gray-50">
                <td class="py-3 px-4 font-medium">{{ group.name }}</td>
                <td class="py-3 px-4">
                  <div class="flex items-center">
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 mr-2" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                      <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2" />
                      <circle cx="9" cy="7" r="4" />
                      <path d="M23 21v-2a4 4 0 0 0-3-3.87" />
                      <path d="M16 3.13a4 4 0 0 1 0 7.75" />
                    </svg>
                    {{ group.userCount }}
                  </div>
                </td>
                <td class="py-3 px-4">
                  <div class="flex flex-wrap gap-1">
                    <span 
                      v-for="(permission, i) in group.permissions" 
                      :key="i" 
                      class="px-2 py-1 text-xs rounded-full border border-gray-200"
                    >
                      {{ permission }}
                    </span>
                  </div>
                </td>
                <td class="py-3 px-4 text-right">
                  <div class="flex justify-end gap-2">
                    <button
                      @click="$emit('group-action', 'users', group.id)"
                      class="p-1 rounded-md hover:bg-gray-100"
                      title="Benutzer zuweisen"
                    >
                      <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                        <path d="M16 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2" />
                        <circle cx="8.5" cy="7" r="4" />
                        <line x1="20" y1="8" x2="20" y2="14" />
                        <line x1="23" y1="11" x2="17" y2="11" />
                      </svg>
                    </button>
                    <button
                      @click="$emit('group-action', 'edit', group.id)"
                      class="p-1 rounded-md hover:bg-gray-100"
                      title="Bearbeiten"
                    >
                      <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                        <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7" />
                        <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z" />
                      </svg>
                    </button>
                    <button 
                      class="p-1 rounded-md hover:bg-gray-100 text-red-500" 
                      title="Löschen"
                      @click="confirmDelete(group)"
                    >
                      <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                        <polyline points="3 6 5 6 21 6" />
                        <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2" />
                        <line x1="10" y1="11" x2="10" y2="17" />
                        <line x1="14" y1="11" x2="14" y2="17" />
                      </svg>
                    </button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- Delete Confirmation Modal -->
    <div v-if="showDeleteModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-white rounded-lg p-6 max-w-md w-full">
        <h3 class="text-lg font-semibold mb-4">Gruppe löschen</h3>
        <p class="mb-6">Sind Sie sicher, dass Sie die Gruppe "{{ groupToDelete?.name }}" löschen möchten? Diese Aktion kann nicht rückgängig gemacht werden.</p>
        <div class="flex justify-end gap-2">
          <button 
            class="px-4 py-2 border border-gray-300 rounded-md hover:bg-gray-50"
            @click="showDeleteModal = false"
          >
            Abbrechen
          </button>
          <button 
            class="px-4 py-2 bg-red-500 text-white rounded-md hover:bg-red-600"
            @click="deleteGroup"
          >
            Löschen
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';

defineEmits(['group-action']);

// In einer echten Anwendung würden diese Daten vom Django-Backend abgerufen werden
const groups = ref([
  { id: '1', name: "Administratoren", userCount: 3, permissions: ["Vollzugriff"] },
  { id: '2', name: "Buchhaltung", userCount: 5, permissions: ["Rechnungen ansehen", "Rechnungen erstellen"] },
  { id: '3', name: "Vertrieb", userCount: 8, permissions: ["Kunden ansehen", "Angebote erstellen"] },
  { id: '4', name: "Lager", userCount: 4, permissions: ["Bestand ansehen", "Bestand bearbeiten"] },
]);

const showDeleteModal = ref(false);
const groupToDelete = ref(null);

const confirmDelete = (group) => {
  groupToDelete.value = group;
  showDeleteModal.value = true;
};

const deleteGroup = () => {
  // In einer echten Anwendung würde hier eine Anfrage an das Django-Backend gesendet werden
  groups.value = groups.value.filter(g => g.id !== groupToDelete.value.id);
  showDeleteModal.value = false;
  groupToDelete.value = null;
  // Erfolgsmeldung anzeigen
  alert("Gruppe wurde erfolgreich gelöscht.");
};
</script>