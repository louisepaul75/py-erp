'use client';

import { useState } from 'react';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Switch } from '@/components/ui/switch';
import { Label } from '@/components/ui/label';
import { useIsAuthenticated } from '@/lib/auth/authHooks';
import useAppTranslation from '@/hooks/useTranslationWrapper';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Input } from '@/components/ui/input';
import { Search, Download, Database, Users, Sliders } from 'lucide-react';

export default function SettingsPage() {
  const { t } = useAppTranslation('settings');
  const { user } = useIsAuthenticated();
  const isAdmin = user?.isAdmin || false;
  
  // Tabs state
  const [activeTab, setActiveTab] = useState('account');
  
  // Mock data for connections
  const [connections, setConnections] = useState({
    legacy_erp: true,
    images_cms: false
  });
  
  // Mock data for database tables
  const [tables, setTables] = useState([
    { name: 'products', rows: 1254, last_updated: '2023-10-15' },
    { name: 'customers', rows: 876, last_updated: '2023-10-14' },
    { name: 'orders', rows: 2541, last_updated: '2023-10-15' },
    { name: 'inventory', rows: 542, last_updated: '2023-10-12' },
  ]);
  
  // Search state
  const [searchQuery, setSearchQuery] = useState('');
  
  // Handle connection toggle
  const toggleConnection = (name: string) => {
    setConnections(prev => ({
      ...prev,
      [name]: !prev[name as keyof typeof prev]
    }));
  };
  
  // Filter tables based on search query
  const filteredTables = tables.filter(table => 
    table.name.toLowerCase().includes(searchQuery.toLowerCase())
  );
  
  // Download mock function
  const handleDownload = (tableName: string) => {
    console.log(`Downloading ${tableName} as Excel`);
    // In a real implementation, this would call an API endpoint
  };

  return (
    <div className="container mx-auto py-10">
      <h1 className="text-3xl font-bold mb-6">
        {isAdmin ? t('admin_settings') : t('user_settings')}
      </h1>

      <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
        <TabsList className="mb-4">
          <TabsTrigger value="account">
            {t('account')}
          </TabsTrigger>
          <TabsTrigger value="preferences">
            {t('preferences')}
          </TabsTrigger>
          {isAdmin && (
            <>
              <TabsTrigger value="user-management">
                <Users className="h-4 w-4 mr-2" />
                {t('user_management')}
              </TabsTrigger>
              <TabsTrigger value="system">
                <Sliders className="h-4 w-4 mr-2" />
                {t('system')}
              </TabsTrigger>
              <TabsTrigger value="data-viewer">
                <Database className="h-4 w-4 mr-2" />
                {t('data_viewer')}
              </TabsTrigger>
            </>
          )}
        </TabsList>

        {/* Account Settings */}
        <TabsContent value="account" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>{t('profile_information')}</CardTitle>
              <CardDescription>
                {t('update_your_profile_details')}
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              {/* Account settings content would go here */}
              <p>{t('account_placeholder')}</p>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Preferences Settings */}
        <TabsContent value="preferences" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>{t('preferences')}</CardTitle>
              <CardDescription>
                {t('customize_your_experience')}
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              {/* Preferences content would go here */}
              <p>{t('preferences_placeholder')}</p>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Admin Only: User Management */}
        {isAdmin && (
          <TabsContent value="user-management" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle>{t('user_management')}</CardTitle>
                <CardDescription>
                  {t('manage_users_and_permissions')}
                </CardDescription>
              </CardHeader>
              <CardContent>
                <p className="text-muted-foreground italic">
                  {t('user_management_placeholder')}
                </p>
              </CardContent>
            </Card>
          </TabsContent>
        )}

        {/* Admin Only: System Settings */}
        {isAdmin && (
          <TabsContent value="system" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle>{t('api_connections')}</CardTitle>
                <CardDescription>
                  {t('manage_external_api_connections')}
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                <div className="flex items-center justify-between">
                  <div className="space-y-0.5">
                    <Label htmlFor="legacy_erp">{t('legacy_erp_connection')}</Label>
                    <p className="text-sm text-muted-foreground">
                      {t('legacy_erp_description')}
                    </p>
                  </div>
                  <Switch
                    id="legacy_erp"
                    checked={connections.legacy_erp}
                    onCheckedChange={() => toggleConnection('legacy_erp')}
                  />
                </div>
                
                <div className="flex items-center justify-between">
                  <div className="space-y-0.5">
                    <Label htmlFor="images_cms">{t('images_cms_connection')}</Label>
                    <p className="text-sm text-muted-foreground">
                      {t('images_cms_description')}
                    </p>
                  </div>
                  <Switch
                    id="images_cms"
                    checked={connections.images_cms}
                    onCheckedChange={() => toggleConnection('images_cms')}
                  />
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        )}

        {/* Admin Only: Data Viewer */}
        {isAdmin && (
          <TabsContent value="data-viewer" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle>{t('database_viewer')}</CardTitle>
                <CardDescription>
                  {t('view_and_export_database_tables')}
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="flex mb-4">
                  <div className="relative flex-1">
                    <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
                    <Input
                      placeholder={t('search_tables')}
                      className="pl-8"
                      value={searchQuery}
                      onChange={(e) => setSearchQuery(e.target.value)}
                    />
                  </div>
                </div>
                
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>{t('table_name')}</TableHead>
                      <TableHead>{t('row_count')}</TableHead>
                      <TableHead>{t('last_updated')}</TableHead>
                      <TableHead className="text-right">{t('actions')}</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {filteredTables.map((table) => (
                      <TableRow key={table.name}>
                        <TableCell className="font-medium">{table.name}</TableCell>
                        <TableCell>{table.rows}</TableCell>
                        <TableCell>{table.last_updated}</TableCell>
                        <TableCell className="text-right">
                          <Button 
                            variant="outline" 
                            size="sm"
                            onClick={() => handleDownload(table.name)}
                          >
                            <Download className="h-4 w-4 mr-2" />
                            {t('export_excel')}
                          </Button>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </CardContent>
            </Card>
          </TabsContent>
        )}
      </Tabs>
    </div>
  );
} 