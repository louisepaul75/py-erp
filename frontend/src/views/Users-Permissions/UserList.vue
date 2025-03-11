<template>
  <div class="container mx-auto py-10">
    <div class="flex justify-between items-center mb-6">
      <h1 class="text-3xl font-bold">Benutzer</h1>
      <button class="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700">
        Neuer Benutzer
      </button>
    </div>

    <div class="bg-white rounded-lg shadow-md overflow-hidden">
      <div class="p-6">
        <h2 class="text-xl font-semibold mb-4">Alle Benutzer</h2>
        <div class="overflow-x-auto">
          <table class="w-full">
            <thead>
              <tr class="border-b">
                <th class="text-left py-3 px-4">Benutzername</th>
                <th class="text-left py-3 px-4">Name</th>
                <th class="text-left py-3 px-4">E-Mail</th>
                <th class="text-left py-3 px-4">Gruppen</th>
                <th class="text-right py-3 px-4">Aktionen</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="user in users" :key="user.id" class="border-b hover:bg-gray-50">
                <td class="py-3 px-4 font-medium">{{ user.username }}</td>
                <td class="py-3 px-4">{{ user.name }}</td>
                <td class="py-3 px-4">{{ user.email }}</td>
                <td class="py-3 px-4">
                  <div class="flex flex-wrap gap-1">
                    <span 
                      v-for="(group, i) in user.groups" 
                      :key="i" 
                      class="px-2 py-1 text-xs rounded-full border border-gray-200"
                    >
                      {{ group }}
                    </span>
                  </div>
                </td>
                <td class="py-3 px-4 text-right">
                  <div class="flex justify-end gap-2">
                    <button
                      @click="$emit('user-action', 'groups', user.id)"
                      class="p-1 rounded-md hover:bg-gray-100"
                      title="Gruppen zuweisen"
                    >
                      <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                        <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2" />
                        <circle cx="9" cy="7" r="4" />
                        <path d="M23 21v-2a4 4 0 0 0-3-3.87" />
                        <path d="M16 3.13a4 4 0 0 1 0 7.75" />
                      </svg>
                    </button>
                    <button
                      class="p-1 rounded-md hover:bg-gray-100"
                      title="Bearbeiten"
                    >
                      <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                        <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7" />
                        <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z" />
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
  </div>
</template>

<script setup>
import { ref } from 'vue';

defineEmits(['user-action']);

// In einer echten Anwendung würden diese Daten vom Django-Backend abgerufen werden
const users = ref([
  { 
    id: '1', 
    username: "anna.mueller", 
    name: "Anna Müller", 
    email: "anna.mueller@example.com", 
    groups: ["Administratoren", "Buchhaltung"] 
  },
  { 
    id: '2', 
    username: "thomas.schmidt", 
    name: "Thomas Schmidt", 
    email: "thomas.schmidt@example.com", 
    groups: ["Buchhaltung"] 
  },
  { 
    id: '3', 
    username: "lisa.wagner", 
    name: "Lisa Wagner", 
    email: "lisa.wagner@example.com", 
    groups: ["Vertrieb", "Buchhaltung"] 
  },
  { 
    id: '4', 
    username: "michael.becker", 
    name: "Michael Becker", 
    email: "michael.becker@example.com", 
    groups: ["Lager"] 
  },
  { 
    id: '5', 
    username: "sarah.hoffmann", 
    name: "Sarah Hoffmann", 
    email: "sarah.hoffmann@example.com", 
    groups: ["Vertrieb"] 
  },
]);
</script>