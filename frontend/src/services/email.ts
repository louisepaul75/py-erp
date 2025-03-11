import api from './api';

// Types
export interface SMTPSettings {
  host: string;
  port: number;
  username: string;
  password: string;
  from_email: string;
  from_name: string;
  encryption: 'none' | 'ssl' | 'tls';
}

export interface TestEmailData {
  to_email: string;
  subject: string;
  message: string;
}

export interface EmailLog {
  id: number;
  message_id: string;
  subject: string;
  from_email: string;
  to_email: string;
  status: string;
  esp: string;
  opens: number;
  clicks: number;
  created_at: string;
  sent_at: string;
  delivered_at: string;
  error_message: string;
}

export interface EmailStats {
  total: number;
  sent: number;
  delivered: number;
  opened: number;
  clicked: number;
  bounced: number;
  failed: number;
  delivery_rate: number;
  open_rate: number;
  click_rate: number;
  bounce_rate: number;
  failure_rate: number;
}

// Default SMTP settings
const defaultSettings: SMTPSettings = {
  host: 'smtp.example.com',
  port: 587,
  username: 'user@example.com',
  password: '',
  from_email: 'no-reply@example.com',
  from_name: 'pyERP System',
  encryption: 'tls'
};

// Load settings from localStorage or use defaults
const loadSettingsFromStorage = (): SMTPSettings => {
  const storedSettings = localStorage.getItem('smtp_settings');
  if (storedSettings) {
    try {
      return JSON.parse(storedSettings);
    } catch (e) {
      console.error('Error parsing stored SMTP settings:', e);
    }
  }
  return { ...defaultSettings };
};

// Save settings to localStorage
const saveSettingsToStorage = (settings: SMTPSettings): void => {
  try {
    // Don't store the password in localStorage for security reasons
    // unless it's a new password (not empty)
    const settingsToStore = { ...settings };
    if (!settingsToStore.password) {
      // If password is empty, try to get the existing one from storage
      const existingSettings = loadSettingsFromStorage();
      settingsToStore.password = existingSettings.password;
    }

    localStorage.setItem('smtp_settings', JSON.stringify(settingsToStore));
  } catch (e) {
    console.error('Error saving SMTP settings to storage:', e);
  }
};

// Initialize mock settings from localStorage
let mockSettings: SMTPSettings = loadSettingsFromStorage();

// Load logs from localStorage or use defaults
const loadLogsFromStorage = (): EmailLog[] => {
  const storedLogs = localStorage.getItem('email_logs');
  if (storedLogs) {
    try {
      return JSON.parse(storedLogs);
    } catch (e) {
      console.error('Error parsing stored email logs:', e);
    }
  }
  return [
    {
      id: 1,
      message_id: '<20230615123456.1234567@pyerp.local>',
      subject: 'Welcome to pyERP',
      from_email: 'no-reply@example.com',
      to_email: 'user@example.com',
      status: 'delivered',
      esp: 'smtp',
      opens: 2,
      clicks: 1,
      created_at: '2023-06-15T12:34:56Z',
      sent_at: '2023-06-15T12:34:57Z',
      delivered_at: '2023-06-15T12:35:01Z',
      error_message: ''
    },
    {
      id: 2,
      message_id: '<20230616123456.7654321@pyerp.local>',
      subject: 'Password Reset',
      from_email: 'no-reply@example.com',
      to_email: 'admin@example.com',
      status: 'opened',
      esp: 'smtp',
      opens: 1,
      clicks: 0,
      created_at: '2023-06-16T10:11:12Z',
      sent_at: '2023-06-16T10:11:13Z',
      delivered_at: '2023-06-16T10:11:18Z',
      error_message: ''
    },
    {
      id: 3,
      message_id: '<20230617123456.1122334@pyerp.local>',
      subject: 'Failed Test Email',
      from_email: 'no-reply@example.com',
      to_email: 'invalid@example',
      status: 'failed',
      esp: 'smtp',
      opens: 0,
      clicks: 0,
      created_at: '2023-06-17T15:16:17Z',
      sent_at: '2023-06-17T15:16:18Z',
      delivered_at: '',
      error_message: 'Invalid email address'
    }
  ];
};

// Save logs to localStorage
const saveLogsToStorage = (logs: EmailLog[]): void => {
  try {
    localStorage.setItem('email_logs', JSON.stringify(logs));
  } catch (e) {
    console.error('Error saving email logs to storage:', e);
  }
};

// Initialize mock logs from localStorage
let mockLogs: EmailLog[] = loadLogsFromStorage();

// Email API service
const emailService = {
  // Get SMTP settings
  getSettings: async () => {
    try {
      // In production, this would call the API
      // const response = await api.get('/email/settings/');
      // return response.data;

      // For development without database, return mock data from localStorage
      return {
        success: true,
        data: mockSettings
      };
    } catch (error) {
      console.error('Error fetching SMTP settings:', error);
      throw error;
    }
  },

  // Update SMTP settings
  updateSettings: async (settings: SMTPSettings) => {
    try {
      // In production, this would call the API
      // const response = await api.post('/email/settings/', settings);
      // return response.data;

      // For development without database, update mock data and localStorage
      mockSettings = { ...settings };
      saveSettingsToStorage(mockSettings);

      return {
        success: true,
        message: 'SMTP settings updated successfully'
      };
    } catch (error) {
      console.error('Error updating SMTP settings:', error);
      throw error;
    }
  },

  // Send test email
  sendTestEmail: async (testData: TestEmailData) => {
    try {
      // In production, this would call the API
      // const response = await api.post('/email/test-email/', testData);
      // return response.data;

      // For development without database, simulate sending an email
      // Add a new log entry for the test email
      const newId = mockLogs.length > 0 ? Math.max(...mockLogs.map((log) => log.id)) + 1 : 1;
      const now = new Date().toISOString();
      const messageId = `<${Date.now()}.${Math.floor(Math.random() * 1000000)}@pyerp.local>`;

      const newLog: EmailLog = {
        id: newId,
        message_id: messageId,
        subject: testData.subject,
        from_email: mockSettings.from_email,
        to_email: testData.to_email,
        status: 'sent',
        esp: 'smtp',
        opens: 0,
        clicks: 0,
        created_at: now,
        sent_at: now,
        delivered_at: '',
        error_message: ''
      };

      mockLogs.unshift(newLog);
      saveLogsToStorage(mockLogs);

      return {
        success: true,
        message: 'Test email sent successfully',
        data: { message_id: messageId }
      };
    } catch (error) {
      console.error('Error sending test email:', error);
      throw error;
    }
  },

  // Get email logs
  getEmailLogs: async () => {
    try {
      // In production, this would call the API
      // const response = await api.get('/email/email-logs/');
      // return response.data;

      // For development without database, return mock data from localStorage
      return {
        success: true,
        data: {
          logs: mockLogs,
          total: mockLogs.length
        }
      };
    } catch (error) {
      console.error('Error fetching email logs:', error);
      throw error;
    }
  },

  // Clear email logs
  clearEmailLogs: async () => {
    try {
      // In production, this would call the API
      // const response = await api.delete('/email/email-logs/');
      // return response.data;

      // For development without database, clear mock data and localStorage
      mockLogs = [];
      saveLogsToStorage(mockLogs);

      return {
        success: true,
        message: 'Email logs cleared successfully'
      };
    } catch (error) {
      console.error('Error clearing email logs:', error);
      throw error;
    }
  },

  // Get email statistics
  getEmailStats: async () => {
    try {
      // In production, this would call the API
      // const response = await api.get('/email/email-stats/');
      // return response.data;

      // For development without database, calculate stats from mock data
      const total = mockLogs.length;
      const sent = mockLogs.filter(
        (log) =>
          log.status === 'sent' ||
          log.status === 'delivered' ||
          log.status === 'opened' ||
          log.status === 'clicked'
      ).length;
      const delivered = mockLogs.filter(
        (log) => log.status === 'delivered' || log.status === 'opened' || log.status === 'clicked'
      ).length;
      const opened = mockLogs.filter(
        (log) => log.status === 'opened' || log.status === 'clicked'
      ).length;
      const clicked = mockLogs.filter((log) => log.status === 'clicked').length;
      const bounced = mockLogs.filter((log) => log.status === 'bounced').length;
      const failed = mockLogs.filter((log) => log.status === 'failed').length;

      return {
        success: true,
        data: {
          total,
          sent,
          delivered,
          opened,
          clicked,
          bounced,
          failed,
          delivery_rate: sent > 0 ? (delivered / sent) * 100 : 0,
          open_rate: delivered > 0 ? (opened / delivered) * 100 : 0,
          click_rate: opened > 0 ? (clicked / opened) * 100 : 0,
          bounce_rate: sent > 0 ? (bounced / sent) * 100 : 0,
          failure_rate: total > 0 ? (failed / total) * 100 : 0
        }
      };
    } catch (error) {
      console.error('Error fetching email statistics:', error);
      throw error;
    }
  }
};

export default emailService;
