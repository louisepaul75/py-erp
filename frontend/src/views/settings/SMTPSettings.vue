<template>
  <div class="min-h-screen bg-gray-50 p-6">
    <div class="max-w-4xl mx-auto">
      <div class="bg-white shadow rounded-lg p-6 mb-6">
        <div class="mb-6">
          <h2 class="text-2xl font-bold tracking-tight">SMTP Einstellungen</h2>
          <p class="text-gray-500">Konfigurieren Sie Ihren SMTP-Server für den E-Mail-Versand.</p>
        </div>

        <div class="border-b border-gray-200 mb-6"></div>

        <!-- SMTP Settings Form -->
        <div>
          <h4 class="text-base font-semibold mb-4">SMTP Server Konfiguration</h4>
          <p class="text-sm text-gray-500 mb-6">
            Geben Sie die Verbindungsdaten für Ihren SMTP-Server ein.
          </p>

          <!-- Status Banner -->
          <div v-if="lastSaveStatus" 
               :class="[
                 'mb-6 p-4 rounded-md',
                 lastSaveStatus === 'success' 
                   ? 'bg-green-50 border border-green-200' 
                   : 'bg-red-50 border border-red-200'
               ]">
            <div class="flex">
              <div class="flex-shrink-0">
                <svg v-if="lastSaveStatus === 'success'" 
                     class="h-5 w-5 text-green-500" 
                     xmlns="http://www.w3.org/2000/svg" 
                     viewBox="0 0 20 20" 
                     fill="currentColor">
                  <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
                </svg>
                <svg v-else 
                     class="h-5 w-5 text-red-500" 
                     xmlns="http://www.w3.org/2000/svg" 
                     viewBox="0 0 20 20" 
                     fill="currentColor">
                  <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd" />
                </svg>
              </div>
              <div class="ml-3">
                <h3 :class="[
                  'text-sm font-medium',
                  lastSaveStatus === 'success' ? 'text-green-800' : 'text-red-800'
                ]">
                  {{ lastSaveStatus === 'success' ? 'Einstellungen gespeichert' : 'Fehler beim Speichern' }}
                </h3>
                <div :class="[
                  'mt-2 text-sm',
                  lastSaveStatus === 'success' ? 'text-green-700' : 'text-red-700'
                ]">
                  <p>{{ lastSaveMessage }}</p>
                  <p v-if="lastSaveDetails" class="mt-1 text-xs">
                    {{ lastSaveDetails }}
                  </p>
                  <p v-if="lastSaveTime" class="mt-2 text-xs font-medium">
                    Zeitpunkt: {{ lastSaveTime }}
                  </p>
                </div>
              </div>
            </div>
          </div>

          <form @submit.prevent="saveSettings" class="space-y-4">
            <div class="grid grid-cols-1 gap-4 sm:grid-cols-2">
              <div>
                <label for="host" class="block text-sm font-medium text-gray-700">SMTP Host</label>
                <input
                  id="host"
                  v-model="smtpForm.host"
                  type="text"
                  placeholder="smtp.example.com"
                  class="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary focus:border-primary"
                  required
                />
                <p v-if="errors.host" class="mt-1 text-sm text-red-600">{{ errors.host }}</p>
              </div>

              <div>
                <label for="port" class="block text-sm font-medium text-gray-700">Port</label>
                <input
                  id="port"
                  v-model.number="smtpForm.port"
                  type="number"
                  class="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary focus:border-primary"
                  required
                />
                <p class="mt-1 text-xs text-gray-500">
                  Üblicherweise 587 (TLS), 465 (SSL) oder 25 (ohne Verschlüsselung)
                </p>
                <p v-if="errors.port" class="mt-1 text-sm text-red-600">{{ errors.port }}</p>
              </div>
            </div>

            <div class="grid grid-cols-1 gap-4 sm:grid-cols-2">
              <div>
                <label for="username" class="block text-sm font-medium text-gray-700">Benutzername</label>
                <input
                  id="username"
                  v-model="smtpForm.username"
                  type="text"
                  placeholder="username@example.com"
                  class="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary focus:border-primary"
                  required
                />
                <p v-if="errors.username" class="mt-1 text-sm text-red-600">
                  {{ errors.username }}
                </p>
              </div>

              <div>
                <label for="password" class="block text-sm font-medium text-gray-700">Passwort</label>
                <input
                  id="password"
                  v-model="smtpForm.password"
                  type="password"
                  class="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary focus:border-primary"
                  required
                />
                <p v-if="errors.password" class="mt-1 text-sm text-red-600">
                  {{ errors.password }}
                </p>
              </div>
            </div>

            <div class="grid grid-cols-1 gap-4 sm:grid-cols-2">
              <div>
                <label for="from_email" class="block text-sm font-medium text-gray-700">Absender E-Mail</label>
                <input
                  id="from_email"
                  v-model="smtpForm.from_email"
                  type="email"
                  placeholder="no-reply@example.com"
                  class="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary focus:border-primary"
                  required
                />
                <p v-if="errors.from_email" class="mt-1 text-sm text-red-600">
                  {{ errors.from_email }}
                </p>
              </div>

              <div>
                <label for="from_name" class="block text-sm font-medium text-gray-700">Absendername</label>
                <input
                  id="from_name"
                  v-model="smtpForm.from_name"
                  type="text"
                  placeholder="Meine Firma"
                  class="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary focus:border-primary"
                  required
                />
                <p v-if="errors.from_name" class="mt-1 text-sm text-red-600">
                  {{ errors.from_name }}
                </p>
              </div>
            </div>

            <div>
              <label for="encryption" class="block text-sm font-medium text-gray-700">Verschlüsselung</label>
              <select
                id="encryption"
                v-model="smtpForm.encryption"
                class="mt-1 block w-full pl-3 pr-10 py-2 text-base border border-gray-300 focus:outline-none focus:ring-primary focus:border-primary sm:text-sm rounded-md"
              >
                <option value="none">Keine Verschlüsselung</option>
                <option value="ssl">SSL</option>
                <option value="tls">TLS (STARTTLS)</option>
              </select>
              <p class="mt-1 text-xs text-gray-500">
                SSL: Port 465 | TLS: Port 587 | Keine: Port 25
              </p>
            </div>

            <div class="pt-4">
              <button
                type="submit"
                class="inline-flex justify-center py-2 px-4 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-primary hover:bg-primary-dark focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary"
                :disabled="isSaving"
              >
                <svg
                  v-if="isSaving"
                  class="animate-spin -ml-1 mr-2 h-4 w-4 text-white"
                  xmlns="http://www.w3.org/2000/svg"
                  fill="none"
                  viewBox="0 0 24 24"
                >
                  <circle
                    class="opacity-25"
                    cx="12"
                    cy="12"
                    r="10"
                    stroke="currentColor"
                    stroke-width="4"
                  ></circle>
                  <path
                    class="opacity-75"
                    fill="currentColor"
                    d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                  ></path>
                </svg>
                Einstellungen speichern
              </button>
            </div>
          </form>
        </div>
      </div>

      <!-- Test Email Form -->
      <div class="bg-white shadow rounded-lg p-6 mb-6">
        <h4 class="text-base font-semibold mb-4">Test E-Mail senden</h4>
        <p class="text-sm text-gray-500 mb-6">
          Testen Sie Ihre SMTP-Konfiguration durch das Senden einer Test-E-Mail.
        </p>

        <form @submit.prevent="sendTestEmail" class="space-y-4">
          <div>
            <label for="to_email" class="block text-sm font-medium text-gray-700">Empfänger E-Mail</label>
            <input
              id="to_email"
              v-model="testForm.to_email"
              type="email"
              placeholder="empfaenger@example.com"
              class="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary focus:border-primary"
              required
            />
            <p v-if="errors.to_email" class="mt-1 text-sm text-red-600">
              {{ errors.to_email }}
            </p>
          </div>

          <div>
            <label for="subject" class="block text-sm font-medium text-gray-700">Betreff</label>
            <input
              id="subject"
              v-model="testForm.subject"
              type="text"
              class="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary focus:border-primary"
              required
            />
            <p v-if="errors.subject" class="mt-1 text-sm text-red-600">{{ errors.subject }}</p>
          </div>

          <div>
            <label for="message" class="block text-sm font-medium text-gray-700">Nachricht</label>
            <textarea
              id="message"
              v-model="testForm.message"
              rows="3"
              class="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary focus:border-primary"
              required
            ></textarea>
            <p v-if="errors.message" class="mt-1 text-sm text-red-600">{{ errors.message }}</p>
          </div>

          <div class="pt-4">
            <button
              type="submit"
              class="inline-flex justify-center py-2 px-4 border border-transparent shadow-sm text-sm font-medium rounded-md text-gray-700 bg-gray-100 hover:bg-gray-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-gray-500"
              :disabled="isTesting || !isFormValid"
            >
              <svg
                v-if="isTesting"
                class="animate-spin -ml-1 mr-2 h-4 w-4 text-gray-700"
                xmlns="http://www.w3.org/2000/svg"
                fill="none"
                viewBox="0 0 24 24"
              >
                <circle
                  class="opacity-25"
                  cx="12"
                  cy="12"
                  r="10"
                  stroke="currentColor"
                  stroke-width="4"
                ></circle>
                <path
                  class="opacity-75"
                  fill="currentColor"
                  d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                ></path>
              </svg>
              Test E-Mail senden
            </button>
          </div>
        </form>
      </div>

      <!-- Logs Section -->
      <div class="bg-white shadow rounded-lg p-6">
        <div class="flex justify-between items-center mb-4">
          <h4 class="text-base font-semibold">E-Mail Logs</h4>
          <div class="flex space-x-2">
            <button
              @click="clearLogs"
              class="inline-flex items-center px-3 py-1.5 border border-gray-300 shadow-sm text-sm font-medium rounded text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary"
            >
              <TrashIcon class="h-4 w-4 mr-1" />
              Logs löschen
            </button>
            <button
              @click="refreshLogs"
              class="inline-flex items-center px-3 py-1.5 border border-gray-300 shadow-sm text-sm font-medium rounded text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary"
              :disabled="isRefreshing"
            >
              <RefreshCwIcon v-if="!isRefreshing" class="h-4 w-4 mr-1" />
              <svg
                v-else
                class="animate-spin h-4 w-4 mr-1"
                xmlns="http://www.w3.org/2000/svg"
                fill="none"
                viewBox="0 0 24 24"
              >
                <circle
                  class="opacity-25"
                  cx="12"
                  cy="12"
                  r="10"
                  stroke="currentColor"
                  stroke-width="4"
                ></circle>
                <path
                  class="opacity-75"
                  fill="currentColor"
                  d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                ></path>
              </svg>
              Aktualisieren
            </button>
          </div>
        </div>

        <div
          class="bg-gray-900 rounded-md p-4 h-64 overflow-y-auto font-mono text-sm text-gray-200"
        >
          <div v-if="logs.length === 0" class="text-gray-400 italic">
            Keine Logs vorhanden. Senden Sie eine Test-E-Mail, um Logs zu generieren.
          </div>
          <div v-for="(log, index) in logs" :key="index" class="mb-2">
            <div
              :class="[
                'py-1 border-l-4 pl-3',
                log.type === 'success'
                  ? 'border-green-500'
                  : log.type === 'error'
                    ? 'border-red-500'
                    : log.type === 'info'
                      ? 'border-blue-500'
                      : 'border-gray-500'
              ]"
            >
              <div class="flex items-center">
                <span class="text-gray-400">{{ log.timestamp }}</span>
                <span
                  :class="[
                    'ml-2 px-2 py-0.5 text-xs rounded-full',
                    log.type === 'success'
                      ? 'bg-green-900 text-green-300'
                      : log.type === 'error'
                        ? 'bg-red-900 text-red-300'
                        : log.type === 'info'
                          ? 'bg-blue-900 text-blue-300'
                          : 'bg-gray-700 text-gray-300'
                  ]"
                >
                  {{ log.type.toUpperCase() }}
                </span>
              </div>
              <div class="mt-1">{{ log.message }}</div>
              <div v-if="log.details" class="mt-1 text-gray-400 text-xs">
                {{ log.details }}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Toast Notifications -->
    <div class="fixed bottom-4 right-4 z-50">
      <transition-group name="toast">
        <div
          v-for="toast in toasts"
          :key="toast.id"
          :class="[
            'mb-2 p-4 rounded-md shadow-lg max-w-md transform transition-all duration-300',
            toast.type === 'success' ? 'bg-green-500 text-white' : 'bg-red-500 text-white'
          ]"
        >
          <div class="flex items-start">
            <div class="flex-shrink-0">
              <svg
                v-if="toast.type === 'success'"
                class="h-5 w-5 text-white"
                xmlns="http://www.w3.org/2000/svg"
                viewBox="0 0 20 20"
                fill="currentColor"
              >
                <path
                  fill-rule="evenodd"
                  d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
                  clip-rule="evenodd"
                />
              </svg>
              <svg
                v-else
                class="h-5 w-5 text-white"
                xmlns="http://www.w3.org/2000/svg"
                viewBox="0 0 20 20"
                fill="currentColor"
              >
                <path
                  fill-rule="evenodd"
                  d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z"
                  clip-rule="evenodd"
                />
              </svg>
            </div>
            <div class="ml-3">
              <p class="text-sm font-medium">{{ toast.title }}</p>
              <p v-if="toast.message" class="mt-1 text-sm">{{ toast.message }}</p>
            </div>
            <div class="ml-auto pl-3">
              <button
                @click="removeToast(toast.id)"
                class="inline-flex text-white hover:text-gray-100 focus:outline-none"
              >
                <svg
                  class="h-5 w-5"
                  xmlns="http://www.w3.org/2000/svg"
                  viewBox="0 0 20 20"
                  fill="currentColor"
                >
                  <path
                    fill-rule="evenodd"
                    d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z"
                    clip-rule="evenodd"
                  />
                </svg>
              </button>
            </div>
          </div>
        </div>
      </transition-group>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue';
import { TrashIcon, RefreshCwIcon } from 'lucide-vue-next';
import emailService from '@/services/email';

// Form state
const smtpForm = ref({
  host: '',
  port: 587,
  username: '',
  password: '',
  from_email: '',
  from_name: '',
  encryption: 'tls' // 'none', 'ssl', 'tls'
});

const testForm = ref({
  to_email: '',
  subject: 'Test E-Mail',
  message: 'Dies ist eine Test-E-Mail, um die SMTP-Konfiguration zu überprüfen.'
});

const errors = ref({});
const isSaving = ref(false);
const isTesting = ref(false);
const isRefreshing = ref(false);

// Logs
const logs = ref([]);

// Toast notifications
const toasts = ref([]);
let toastId = 0;

// Add these new refs for save status
const lastSaveStatus = ref(null); // 'success' or 'error'
const lastSaveMessage = ref('');
const lastSaveDetails = ref('');
const lastSaveTime = ref('');

// Helper functions
const formatDate = (date) => {
  return new Intl.DateTimeFormat('de-DE', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  }).format(date);
};

const addToast = (title, message = '', type = 'success') => {
  const id = toastId++;
  toasts.value.push({ id, title, message, type });

  // Auto-remove toast after 5 seconds
  setTimeout(() => {
    removeToast(id);
  }, 5000);
};

const removeToast = (id) => {
  toasts.value = toasts.value.filter((toast) => toast.id !== id);
};

const addLog = (message, type = 'info', details = '') => {
  logs.value.unshift({
    timestamp: formatDate(new Date()),
    message,
    type,
    details
  });
};

const clearLogs = async () => {
  try {
    await emailService.clearEmailLogs();
    logs.value = [];
    addLog('Logs wurden gelöscht', 'info');
    addToast('Logs gelöscht', 'Alle E-Mail-Logs wurden erfolgreich gelöscht.');
  } catch (error) {
    addLog('Fehler beim Löschen der Logs', 'error', error.message);
    addToast('Fehler', 'Die Logs konnten nicht gelöscht werden.', 'error');
  }
};

const refreshLogs = async () => {
  isRefreshing.value = true;

  try {
    const response = await emailService.getEmailLogs();

    if (response.success) {
      // Clear existing logs
      logs.value = [];

      // Add logs from API
      response.data.logs.forEach((log) => {
        let logType = 'info';
        if (log.status === 'sent' || log.status === 'delivered') {
          logType = 'success';
        } else if (
          log.status === 'failed' ||
          log.status === 'bounced' ||
          log.status === 'rejected'
        ) {
          logType = 'error';
        }

        addLog(
          `E-Mail: ${log.subject} an ${log.to_email} (${log.status})`,
          logType,
          log.error_message || `Message-ID: ${log.message_id}`
        );
      });

      addLog('Logs wurden aktualisiert', 'info');
      addToast('Logs aktualisiert', 'Die E-Mail-Logs wurden erfolgreich aktualisiert.');
    } else {
      throw new Error(response.error || 'Unbekannter Fehler');
    }
  } catch (error) {
    addLog('Fehler beim Aktualisieren der Logs', 'error', error.message);
    addToast('Fehler', 'Die Logs konnten nicht aktualisiert werden.', 'error');
  } finally {
    isRefreshing.value = false;
  }
};

// Form validation
const validateEmail = (email) => {
  const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return re.test(email);
};

const validateSMTPForm = () => {
  const newErrors = {};

  if (!smtpForm.value.host) {
    newErrors.host = 'SMTP Host ist erforderlich';
  }

  if (!smtpForm.value.port || smtpForm.value.port < 1 || smtpForm.value.port > 65535) {
    newErrors.port = 'Gültiger Port ist erforderlich (1-65535)';
  }

  if (!smtpForm.value.username) {
    newErrors.username = 'Benutzername ist erforderlich';
  }

  if (!smtpForm.value.password) {
    newErrors.password = 'Passwort ist erforderlich';
  }

  if (!smtpForm.value.from_email) {
    newErrors.from_email = 'Absender E-Mail ist erforderlich';
  } else if (!validateEmail(smtpForm.value.from_email)) {
    newErrors.from_email = 'Gültige E-Mail-Adresse erforderlich';
  }

  if (!smtpForm.value.from_name) {
    newErrors.from_name = 'Absendername ist erforderlich';
  }

  errors.value = newErrors;
  return Object.keys(newErrors).length === 0;
};

const validateTestForm = () => {
  const newErrors = {};

  if (!testForm.value.to_email) {
    newErrors.to_email = 'Empfänger E-Mail ist erforderlich';
  } else if (!validateEmail(testForm.value.to_email)) {
    newErrors.to_email = 'Gültige E-Mail-Adresse erforderlich';
  }

  if (!testForm.value.subject) {
    newErrors.subject = 'Betreff ist erforderlich';
  }

  if (!testForm.value.message) {
    newErrors.message = 'Nachricht ist erforderlich';
  }

  errors.value = { ...errors.value, ...newErrors };
  return Object.keys(newErrors).length === 0;
};

const isFormValid = computed(() => {
  return (
    smtpForm.value.host &&
    smtpForm.value.port &&
    smtpForm.value.username &&
    smtpForm.value.password &&
    smtpForm.value.from_email &&
    validateEmail(smtpForm.value.from_email) &&
    smtpForm.value.from_name
  );
});

// Load SMTP settings
const loadSettings = async () => {
  try {
    const response = await emailService.getSettings();

    if (response.success) {
      const data = response.data;

      smtpForm.value.host = data.host || '';
      smtpForm.value.port = data.port || 587;
      smtpForm.value.username = data.username || '';
      // Password is not loaded for security reasons
      smtpForm.value.from_email = data.from_email || '';
      smtpForm.value.from_name = data.from_name || '';
      smtpForm.value.encryption = data.encryption || 'tls';

      addLog('SMTP-Einstellungen geladen', 'info');
    } else {
      throw new Error(response.error || 'Unbekannter Fehler');
    }
  } catch (error) {
    addLog('Fehler beim Laden der SMTP-Einstellungen', 'error', error.message);
    addToast('Fehler', 'Die SMTP-Einstellungen konnten nicht geladen werden.', 'error');
  }
};

// Form submission
const saveSettings = async () => {
  if (!validateSMTPForm()) return;

  isSaving.value = true;
  addLog('Speichere SMTP-Einstellungen...', 'info');

  try {
    const response = await emailService.updateSettings(smtpForm.value);

    if (response.success) {
      // Update save status
      lastSaveStatus.value = 'success';
      lastSaveMessage.value = 'Die SMTP-Einstellungen wurden erfolgreich gespeichert.';
      lastSaveDetails.value = `Host: ${smtpForm.value.host}, Port: ${smtpForm.value.port}, Benutzer: ${smtpForm.value.username}`;
      lastSaveTime.value = formatDate(new Date());
      
      addToast(
        'Einstellungen gespeichert',
        'Die SMTP-Einstellungen wurden erfolgreich gespeichert.'
      );
      addLog(
        'SMTP-Einstellungen erfolgreich gespeichert',
        'success',
        JSON.stringify({
          host: smtpForm.value.host,
          port: smtpForm.value.port,
          username: smtpForm.value.username,
          encryption: smtpForm.value.encryption,
          from_email: smtpForm.value.from_email,
          from_name: smtpForm.value.from_name
        })
      );
    } else {
      throw new Error(response.error || 'Unbekannter Fehler');
    }
  } catch (error) {
    // Update save status for error
    lastSaveStatus.value = 'error';
    lastSaveMessage.value = 'Die SMTP-Einstellungen konnten nicht gespeichert werden.';
    lastSaveDetails.value = error.message || 'Unbekannter Fehler';
    lastSaveTime.value = formatDate(new Date());
    
    addToast('Fehler', 'Die SMTP-Einstellungen konnten nicht gespeichert werden.', 'error');
    addLog('Fehler beim Speichern der SMTP-Einstellungen', 'error', error.message);
    console.error('Error saving SMTP settings:', error);
  } finally {
    isSaving.value = false;
  }
};

const sendTestEmail = async () => {
  if (!validateTestForm()) return;
  if (!validateSMTPForm()) {
    addToast('Fehler', 'Bitte füllen Sie zuerst die SMTP-Einstellungen aus.', 'error');
    return;
  }

  isTesting.value = true;
  addLog(`Sende Test-E-Mail an ${testForm.value.to_email}...`, 'info');

  try {
    const response = await emailService.sendTestEmail(testForm.value);

    if (response.success) {
      addToast('Test erfolgreich', 'Die Test-E-Mail wurde erfolgreich versendet.');
      addLog('Test-E-Mail erfolgreich versendet', 'success');

      // Refresh logs to show the new email
      await refreshLogs();
    } else {
      throw new Error(response.error || 'Unbekannter Fehler');
    }
  } catch (error) {
    addToast(
      'Test fehlgeschlagen',
      error.message || 'Die Test-E-Mail konnte nicht versendet werden.',
      'error'
    );
    addLog('Fehler beim Senden der Test-E-Mail', 'error', error.message);
    console.error('Error sending test email:', error);
  } finally {
    isTesting.value = false;
  }
};

// Lifecycle hooks
onMounted(() => {
  // Load SMTP settings
  loadSettings();

  // Load initial logs
  refreshLogs();
});

// Watch für Änderungen an der Verschlüsselungseinstellung
watch(
  () => smtpForm.value.encryption,
  (newValue) => {
    updatePortBasedOnEncryption(newValue);
  }
);

// Update port based on encryption
const updatePortBasedOnEncryption = (encryption) => {
  if (encryption === 'ssl') {
    smtpForm.value.port = 465;
  } else if (encryption === 'tls') {
    smtpForm.value.port = 587;
  } else {
    smtpForm.value.port = 25;
  }
};
</script>

<style scoped>
.toast-enter-active,
.toast-leave-active {
  transition: all 0.3s ease;
}
.toast-enter-from {
  opacity: 0;
  transform: translateY(30px);
}
.toast-leave-to {
  opacity: 0;
  transform: translateX(100%);
}

/* Tailwind-ähnliche Klassen */
.bg-primary {
  background-color: #0070f3;
}
.bg-primary-dark {
  background-color: #0060df;
}
.text-primary {
  color: #0070f3;
}
.focus\:ring-primary:focus {
  --tw-ring-color: #0070f3;
  --tw-ring-opacity: 0.5;
}
.focus\:border-primary:focus {
  border-color: #0070f3;
}

/* Zusätzliche Stile für besseres Layout */
.min-h-screen {
  min-height: 100vh;
}

.bg-gray-50 {
  background-color: #f9fafb;
}

.p-6 {
  padding: 1.5rem;
}

.max-w-4xl {
  max-width: 56rem;
}

.mx-auto {
  margin-left: auto;
  margin-right: auto;
}

.bg-white {
  background-color: #ffffff;
}

.shadow {
  box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06);
}

.rounded-lg {
  border-radius: 0.5rem;
}

.space-y-6 > * + * {
  margin-top: 1.5rem;
}

.grid {
  display: grid;
}

.grid-cols-1 {
  grid-template-columns: repeat(1, minmax(0, 1fr));
}

@media (min-width: 640px) {
  .sm\:grid-cols-2 {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

.gap-4 {
  gap: 1rem;
}

.mt-1 {
  margin-top: 0.25rem;
}

.block {
  display: block;
}

.w-full {
  width: 100%;
}

.px-3 {
  padding-left: 0.75rem;
  padding-right: 0.75rem;
}

.py-2 {
  padding-top: 0.5rem;
  padding-bottom: 0.5rem;
}

.border {
  border-width: 1px;
}

.border-gray-300 {
  border-color: #d1d5db;
}

.rounded-md {
  border-radius: 0.375rem;
}

.shadow-sm {
  box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
}

.focus\:outline-none:focus {
  outline: 2px solid transparent;
  outline-offset: 2px;
}

.text-white {
  color: #ffffff;
}

.bg-gray-100 {
  background-color: #f3f4f6;
}

.hover\:bg-gray-200:hover {
  background-color: #e5e7eb;
}

.focus\:ring-2:focus {
  --tw-ring-offset-shadow: var(--tw-ring-inset) 0 0 0 var(--tw-ring-offset-width) var(--tw-ring-offset-color);
  --tw-ring-shadow: var(--tw-ring-inset) 0 0 0 calc(2px + var(--tw-ring-offset-width)) var(--tw-ring-color);
  box-shadow: var(--tw-ring-offset-shadow), var(--tw-ring-shadow), var(--tw-shadow, 0 0 #0000);
}

.focus\:ring-offset-2:focus {
  --tw-ring-offset-width: 2px;
}

.focus\:ring-gray-500:focus {
  --tw-ring-color: #6b7280;
}

.h-64 {
  height: 16rem;
}

.overflow-y-auto {
  overflow-y: auto;
}

.font-mono {
  font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace;
}

.text-sm {
  font-size: 0.875rem;
  line-height: 1.25rem;
}

.text-gray-200 {
  color: #e5e7eb;
}

.text-gray-400 {
  color: #9ca3af;
}

.italic {
  font-style: italic;
}

.mb-2 {
  margin-bottom: 0.5rem;
}

.py-1 {
  padding-top: 0.25rem;
  padding-bottom: 0.25rem;
}

.border-l-4 {
  border-left-width: 4px;
}

.pl-3 {
  padding-left: 0.75rem;
}

.border-green-500 {
  border-color: #10b981;
}

.border-red-500 {
  border-color: #ef4444;
}

.border-blue-500 {
  border-color: #3b82f6;
}

.border-gray-500 {
  border-color: #6b7280;
}

.flex {
  display: flex;
}

.items-center {
  align-items: center;
}

.ml-2 {
  margin-left: 0.5rem;
}

.px-2 {
  padding-left: 0.5rem;
  padding-right: 0.5rem;
}

.py-0\.5 {
  padding-top: 0.125rem;
  padding-bottom: 0.125rem;
}

.text-xs {
  font-size: 0.75rem;
  line-height: 1rem;
}

.rounded-full {
  border-radius: 9999px;
}

.bg-green-900 {
  background-color: #064e3b;
}

.text-green-300 {
  color: #6ee7b7;
}

.bg-red-900 {
  background-color: #7f1d1d;
}

.text-red-300 {
  color: #fca5a5;
}

.bg-blue-900 {
  background-color: #1e3a8a;
}

.text-blue-300 {
  color: #93c5fd;
}

.bg-gray-700 {
  background-color: #374151;
}

.text-gray-300 {
  color: #d1d5db;
}

.mt-1 {
  margin-top: 0.25rem;
}
</style>
