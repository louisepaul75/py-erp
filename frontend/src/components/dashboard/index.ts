import QuickAccessModule from './QuickAccessModule.vue';
import RecentOrdersModule from './RecentOrdersModule.vue';
import ImportantLinksModule from './ImportantLinksModule.vue';
import NewsBoardModule from './NewsBoardModule.vue';
import UsersPermissionsModule from './UsersPermissionsModule.vue';

export const dashboardModules = {
  'quick-access': QuickAccessModule,
  'recent-orders': RecentOrdersModule,
  'important-links': ImportantLinksModule,
  'news-board': NewsBoardModule,
  'users-permissions': UsersPermissionsModule
};

export type DashboardModuleType = keyof typeof dashboardModules; 