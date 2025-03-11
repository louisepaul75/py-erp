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

    <div class="bg-white rounded-lg shadow-md overflow-hidden max-w-2xl mx-auto">
      <div class="p-6">
        <h2 class="text-xl font-semibold mb-2">Neue Berechtigungsgruppe erstellen</h2>
        <p class="text-gray-500 mb-6">Definieren Sie einen Namen und wählen Sie Berechtigungen für die neue Gruppe aus.</p>
        
        <form @submit.prevent="handleSubmit">
          <div class="space-y-6">
            <div class="space-y-2">
              <label for="group-name" class="block text-sm font-medium">Gruppenname</label>
              <input 
                id="group-name" 
                v-model="groupName"
                type="text"
                class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="z.B. Buchhaltung, Vertrieb, etc."
                required
              />
            </div>

            <div class="space-y-4">
              <label class="block text-sm font-medium">Berechtigungen</label>
              <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
                <div 
                  v-for="permission in availablePermissions" 
                  :key="permission.id" 
                  class="flex items-center space-x-2"
                >
                  <input 
                    type="checkbox"
                    :id="permission.id"
                    :value="permission.id"
                    v-model="selectedPermissions"
                    class="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                  />
                  <label :for="permission.id" class="text-sm cursor-pointer">
                    {{ permission.label }}
                  </label>
                </div>
              </div>
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
              Gruppe erstellen
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';

defineEmits(['cancel', 'save']);

const groupName = ref('');
const selectedPermissions = ref([]);

// In einer echten Anwendung würden diese Daten vom Django-Backend abgerufen werden
const availablePermissions = [
  { id: "view_users", label: "Benutzer ansehen" },
  { id: "edit_users", label: "Benutzer bearbeiten" },
  { id: "view_invoices", label: "Rechnungen ansehen" },
  { id: "create_invoices", label: "Rechnungen erstellen" },
  { id: "view_customers", label: "Kunden ansehen" },
  { id: "edit_customers", label: "Kunden bearbeiten" },
  { id: "view_inventory", label: "Bestand ansehen" },
  { id: "edit_inventory", label: "Bestand bearbeiten" },
  { id: "view_reports", label: "Berichte ansehen" },
  { id: "admin_access", label: "Administrator-Zugriff" },
];

const handleSubmit = () => {
  // In einer echten Anwendung würden die Daten an das Django-Backend gesendet werden
  console.log({
    name: groupName.value,
    permissions: selectedPermissions.value
  });
  
  // Für Demo-Zwecke nur eine Meldung anzeigen und weiterleiten
  alert('Gruppe wurde erfolgreich erstellt!');
  groupName.value = '';
  selectedPermissions.value = [];
  
  // Zurück zur Gruppenliste
  emit('save');
};
</script>