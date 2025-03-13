import { defineStore } from 'pinia';

interface Notification {
  id: number;
  message: string;
  type: 'success' | 'error' | 'info' | 'warning';
  timeout?: number;
}

interface NotificationsState {
  notifications: Notification[];
}

export const useNotificationsStore = defineStore('notifications', {
  state: (): NotificationsState => ({
    notifications: [],
  }),

  actions: {
    add(notification: Omit<Notification, 'id'>) {
      const id = Date.now();
      this.notifications.push({
        ...notification,
        id,
      });

      if (notification.timeout !== 0) {
        setTimeout(() => {
          this.remove(id);
        }, notification.timeout || 5000);
      }
    },

    remove(id: number) {
      const index = this.notifications.findIndex((n) => n.id === id);
      if (index > -1) {
        this.notifications.splice(index, 1);
      }
    },

    success(message: string, timeout?: number) {
      this.add({ message, type: 'success', timeout });
    },

    error(message: string, timeout?: number) {
      this.add({ message, type: 'error', timeout });
    },

    info(message: string, timeout?: number) {
      this.add({ message, type: 'info', timeout });
    },

    warning(message: string, timeout?: number) {
      this.add({ message, type: 'warning', timeout });
    },

    clear() {
      this.notifications = [];
    },
  },
}); 