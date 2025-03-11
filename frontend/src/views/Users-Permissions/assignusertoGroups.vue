<template>
  <div class="container mx-auto py-10">
    <div class="mb-6">
      <button @click="$emit('cancel')" class="flex items-center text-blue-600 hover:underline">
        <svg
          xmlns="http://www.w3.org/2000/svg"
          class="h-4 w-4 mr-2"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="2"
          stroke-linecap="round"
          stroke-linejoin="round"
        >
          <line x1="19" y1="12" x2="5" y2="12" />
          <polyline points="12 19 5 12 12 5" />
        </svg>
        Zurück zur Benutzerliste
      </button>
    </div>

    <div class="bg-white rounded-lg shadow-md overflow-hidden">
      <div class="p-6">
        <h2 class="text-xl font-semibold mb-2">Gruppen für "{{ userName }}" verwalten</h2>
        <p class="text-gray-500 mb-6">
          Wählen Sie die Gruppen aus, zu denen dieser Benutzer gehören soll.
        </p>

        <form @submit.prevent="handleSubmit">
          <div class="overflow-x-auto">
            <table class="w-full">
              <thead>
                <tr class="border-b">
                  <th class="w-12 py-3 px-4">
                    <span class="sr-only">Auswählen</span>
                  </th>
                  <th class="text-left py-3 px-4">Gruppenname</th>
                  <th class="text-left py-3 px-4">Beschreibung</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="group in allGroups" :key="group.id" class="border-b hover:bg-gray-50">
                  <td class="py-3 px-4">
                    <input
                      type="checkbox"
                      :id="`group-${group.id}`"
                      :value="group.id"
                      v-model="selectedGroups"
                      class="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                    />
                  </td>
                  <td class="py-3 px-4 font-medium">{{ group.name }}</td>
                  <td class="py-3 px-4">{{ group.description }}</td>
                </tr>
              </tbody>
            </table>
          </div>

          <div class="flex justify-between mt-8">
            <button
              type="button"
              @click="$emit('cancel')"
              class="px-4 py-2 border border-gray-300 rounded-md hover:bg-gray-50"
            >
              Abbrechen
            </button>
            <button
              type="submit"
              class="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
            >
              Änderungen speichern
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue';

const props = defineProps({
  userId: {
    type: String,
    default: null
  }
});

const emit = defineEmits(['cancel', 'save']);

const userName = ref('');
const selectedGroups = ref([]);

// In einer echten Anwendung würden diese Daten vom Django-Backend abgerufen werden
const allGroups = ref([
  { id: 1, name: 'Administratoren', description: 'Vollzugriff auf alle Funktionen', inGroup: true },
  { id: 2, name: 'Buchhaltung', description: 'Zugriff auf Rechnungen und Finanzen', inGroup: true },
  { id: 3, name: 'Vertrieb', description: 'Zugriff auf Kunden und Angebote', inGroup: false },
  { id: 4, name: 'Lager', description: 'Zugriff auf Bestand und Lieferungen', inGroup: false }
]);

const loadUserData = () => {
  // In einer echten Anwendung würden die Benutzerdaten vom Django-Backend abgerufen werden
  // Für Demo-Zwecke verwenden wir hartcodierte Daten
  if (props.userId === '1') {
    userName.value = 'Anna Müller';
    selectedGroups.value = [1, 2]; // Administratoren, Buchhaltung
  } else if (props.userId === '2') {
    userName.value = 'Thomas Schmidt';
    selectedGroups.value = [2]; // Buchhaltung
  } else if (props.userId === '3') {
    userName.value = 'Lisa Wagner';
    selectedGroups.value = [2, 3]; // Buchhaltung, Vertrieb
  } else if (props.userId === '4') {
    userName.value = 'Michael Becker';
    selectedGroups.value = [4]; // Lager
  } else if (props.userId === '5') {
    userName.value = 'Sarah Hoffmann';
    selectedGroups.value = [3]; // Vertrieb
  }
};

// Benutzerdaten laden, wenn sich die userId ändert
watch(
  () => props.userId,
  () => {
    loadUserData();
  }
);

// Benutzerdaten beim Mounten laden
onMounted(() => {
  loadUserData();
});

const handleSubmit = () => {
  // In einer echten Anwendung würden die Daten an das Django-Backend gesendet werden
  console.log({
    userId: props.userId,
    groupIds: selectedGroups.value
  });

  // Für Demo-Zwecke nur eine Meldung anzeigen und weiterleiten
  alert('Gruppen wurden dem Benutzer zugewiesen!');
  emit('save');
};
</script>
