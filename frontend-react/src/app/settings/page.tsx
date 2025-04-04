"use client";

import { useState, useEffect } from "react";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
  CardFooter,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Switch } from "@/components/ui/switch";
import { Label } from "@/components/ui/label";
import { useIsAuthenticated } from "@/lib/auth/authHooks";
import useAppTranslation from "@/hooks/useTranslationWrapper";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Input } from "@/components/ui/input";
import {
  Search,
  Download,
  Database,
  Users,
  Sliders,
  Save,
  User,
  X,
} from "lucide-react";
import { useUpdateProfile } from "@/lib/auth/authHooks";
import { authService } from "@/lib/auth/authService";
import IntegrationDashboard from "./system/IntegrationDashboard";
import CurrencyList from "./currencies/currency-list";
import { CurrencyProvider } from "./currencies/currency-provider";
import { UserManagement } from "@/components/users/user-management"
import { GroupManagement } from "@/components/users/group-management"
import { PermissionManagement } from "@/components/users/permission-management"
import { PasswordPolicyManagement } from "@/components/users/password-policy"
import SyncWorkflows from "@/components/settings/sync/SyncWorkflows";

// Form interface for user profile
interface ProfileForm {
  username: string;
  email: string;
  first_name: string;
  last_name: string;
}

// Error interface that extends ProfileForm for additional error fields
interface ErrorState extends Partial<ProfileForm> {
  advanced?: string;
}

// Password change form interface
interface PasswordForm {
  old_password: string;
  new_password: string;
  confirm_password: string;
}

// Error interface to handle all possible error types
interface ErrorState extends Partial<ProfileForm>, Partial<PasswordForm> {
  advanced?: string;
  general?: string;
}

export default function SettingsPage() {
  const { t } = useAppTranslation("settings");
  const { user } = useIsAuthenticated();
  const updateProfile = useUpdateProfile();

  // Manually set isAdmin to true for demonstration
  // This will show admin options for testing
  // const isAdmin = user?.isAdmin || false;
  const isAdmin = true;

  console.log("User data:", user);
  console.log("Is admin:", isAdmin);

  // User profile form state
  const [profileForm, setProfileForm] = useState<ProfileForm>({
    username: "",
    email: "",
    first_name: "",
    last_name: "",
  });

  // Advanced settings state
  const [advancedSettings, setAdvancedSettings] = useState({
    maintenanceMode: false,
    debugMode: false,
    cacheLifetime: 3600,
    logLevel: "info",
  });

  // System info state
  const [systemInfo] = useState({
    version: "v1.0.0",
    databaseVersion: "PostgreSQL 14.5",
    environment: "Production",
    lastUpdate: "2023-10-15",
  });

  // Password form state
  const [passwordForm, setPasswordForm] = useState<PasswordForm>({
    old_password: "",
    new_password: "",
    confirm_password: "",
  });

  // Password dialog state
  const [showPasswordDialog, setShowPasswordDialog] = useState(false);

  // Password form errors
  const [passwordErrors, setPasswordErrors] = useState<Partial<PasswordForm>>(
    {}
  );

  // Password success message
  const [passwordSuccess, setPasswordSuccess] = useState("");

  // Form errors state
  const [errors, setErrors] = useState<ErrorState>({});

  // Success message state
  const [successMessage, setSuccessMessage] = useState("");

  // Tabs state
  const [activeTab, setActiveTab] = useState("account");

  // Mock data for connections
  const [connections, setConnections] = useState({
    legacy_erp: true,
    images_cms: false,
  });

  // Mock data for database tables
  const [tables, setTables] = useState([
    { name: "products", rows: 1254, last_updated: "2023-10-15" },
    { name: "customers", rows: 876, last_updated: "2023-10-14" },
    { name: "orders", rows: 2541, last_updated: "2023-10-15" },
    { name: "inventory", rows: 542, last_updated: "2023-10-12" },
  ]);

  // Search state
  const [searchQuery, setSearchQuery] = useState("");

  // Load user data into form when user data is available
  useEffect(() => {
    if (user) {
      setProfileForm({
        username: user.username || "",
        email: user.email || "",
        first_name: user.firstName || "",
        last_name: user.lastName || "",
      });
    }
  }, [user]);

  // Handle form input changes
  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setProfileForm((prev) => ({
      ...prev,
      [name]: value,
    }));

    // Clear error for this field when user types
    if (errors[name as keyof typeof errors]) {
      setErrors((prev) => ({
        ...prev,
        [name]: undefined,
      }));
    }

    // Clear success message when user makes changes
    if (successMessage) {
      setSuccessMessage("");
    }
  };

  // Handle password form input changes
  const handlePasswordChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setPasswordForm((prev) => ({
      ...prev,
      [name]: value,
    }));

    // Clear error for this field when user types
    if (passwordErrors[name as keyof typeof passwordErrors]) {
      setPasswordErrors((prev) => ({
        ...prev,
        [name]: undefined,
      }));
    }

    // Clear success message when user makes changes
    if (passwordSuccess) {
      setPasswordSuccess("");
    }
  };

  // Validate password form
  const validatePasswordForm = (): boolean => {
    const newErrors: Partial<PasswordForm> = {};

    if (!passwordForm.old_password) {
      newErrors.old_password = t("old_password_required");
    }

    if (!passwordForm.new_password) {
      newErrors.new_password = t("new_password_required");
    } else if (passwordForm.new_password.length < 8) {
      newErrors.new_password = t("password_too_short");
    }

    if (!passwordForm.confirm_password) {
      newErrors.confirm_password = t("confirm_password_required");
    } else if (passwordForm.new_password !== passwordForm.confirm_password) {
      newErrors.confirm_password = t("passwords_dont_match");
    }

    setPasswordErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  // Handle password form submission
  const handlePasswordSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!validatePasswordForm()) {
      return;
    }

    try {
      await authService.changePassword(
        passwordForm.old_password,
        passwordForm.new_password
      );

      setPasswordSuccess(t("password_changed_success"));

      // Clear form after successful submission
      setPasswordForm({
        old_password: "",
        new_password: "",
        confirm_password: "",
      });

      // Clear success message after 3 seconds
      setTimeout(() => {
        setPasswordSuccess("");
        setShowPasswordDialog(false);
      }, 3000);
    } catch (error) {
      console.error("Error changing password:", error);
      setPasswordErrors({
        old_password: t("password_change_error"),
      });
    }
  };

  // Validate form
  const validateForm = (): boolean => {
    const newErrors: Partial<ProfileForm> = {};

    if (!profileForm.email) {
      newErrors.email = t("email_required");
    } else if (!/\S+@\S+\.\S+/.test(profileForm.email)) {
      newErrors.email = t("email_invalid");
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  // Handle profile form submission
  const handleProfileSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!validateForm()) {
      return;
    }

    try {
      // Only send fields that can be updated
      const updateData = {
        email: profileForm.email,
        firstName: profileForm.first_name,
        lastName: profileForm.last_name,
      };

      await updateProfile.mutateAsync(updateData);
      setSuccessMessage(t("profile_update_success"));

      // Clear success message after 3 seconds
      setTimeout(() => {
        setSuccessMessage("");
      }, 3000);
    } catch (error) {
      console.error("Error updating profile:", error);
      setErrors({
        email: t("profile_update_error"),
      });
    }
  };

  // Handle connection toggle
  const toggleConnection = (name: string) => {
    setConnections((prev) => ({
      ...prev,
      [name]: !prev[name as keyof typeof prev],
    }));
  };

  // Filter tables based on search query
  const filteredTables = tables.filter((table) =>
    table.name.toLowerCase().includes(searchQuery.toLowerCase())
  );

  // Download mock function
  const handleDownload = (tableName: string) => {
    console.log(`Downloading ${tableName} as Excel`);
    // In a real implementation, this would call an API endpoint
  };

  // Handle advanced settings changes
  const handleAdvancedSettingChange = (setting: string, value: any) => {
    setAdvancedSettings((prev) => ({
      ...prev,
      [setting]: value,
    }));
  };

  // Handle advanced settings save
  const handleAdvancedSettingsSave = async () => {
    try {
      // TODO: Replace with actual API call
      console.log("Saving advanced settings:", advancedSettings);

      // Simulate API call
      await new Promise((resolve) => setTimeout(resolve, 1000));

      // Show success message using toast or other notification
      setSuccessMessage(t("configuration_saved"));

      // Clear success message after 3 seconds
      setTimeout(() => {
        setSuccessMessage("");
      }, 3000);
    } catch (error) {
      console.error("Error saving advanced settings:", error);
      setErrors({
        ...errors,
        advanced: t("configuration_save_error"),
      });
    }
  };

  return (
    <div className="container mx-auto py-10">
      <h1 className="text-3xl font-bold mb-6">
        {isAdmin ? t("admin_settings") : t("user_settings")}
      </h1>

      {/* Password change dialog */}
      {showPasswordDialog && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-lg max-w-md w-full">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-xl font-bold">{t("change_password")}</h2>
              <button
                onClick={() => setShowPasswordDialog(false)}
                className="text-gray-500 hover:text-gray-700"
              >
                <X className="h-5 w-5" />
              </button>
            </div>

            <form onSubmit={handlePasswordSubmit} className="space-y-4">
              <div className="flex flex-col space-y-1.5">
                <Label htmlFor="old_password">{t("old_password")}</Label>
                <Input
                  id="old_password"
                  name="old_password"
                  type="password"
                  value={passwordForm.old_password}
                  onChange={handlePasswordChange}
                  className={
                    passwordErrors.old_password ? "border-red-500" : ""
                  }
                />
                {passwordErrors.old_password && (
                  <p className="text-sm text-red-500">
                    {passwordErrors.old_password}
                  </p>
                )}
              </div>

              <div className="flex flex-col space-y-1.5">
                <Label htmlFor="new_password">{t("new_password")}</Label>
                <Input
                  id="new_password"
                  name="new_password"
                  type="password"
                  value={passwordForm.new_password}
                  onChange={handlePasswordChange}
                  className={
                    passwordErrors.new_password ? "border-red-500" : ""
                  }
                />
                {passwordErrors.new_password && (
                  <p className="text-sm text-red-500">
                    {passwordErrors.new_password}
                  </p>
                )}
              </div>

              <div className="flex flex-col space-y-1.5">
                <Label htmlFor="confirm_password">
                  {t("confirm_password")}
                </Label>
                <Input
                  id="confirm_password"
                  name="confirm_password"
                  type="password"
                  value={passwordForm.confirm_password}
                  onChange={handlePasswordChange}
                  className={
                    passwordErrors.confirm_password ? "border-red-500" : ""
                  }
                />
                {passwordErrors.confirm_password && (
                  <p className="text-sm text-red-500">
                    {passwordErrors.confirm_password}
                  </p>
                )}
              </div>

              {passwordSuccess && (
                <div className="p-3 bg-green-100 text-green-800 rounded-md">
                  {passwordSuccess}
                </div>
              )}

              <div className="flex justify-end space-x-2">
                <Button
                  type="button"
                  variant="outline"
                  onClick={() => setShowPasswordDialog(false)}
                >
                  {t("cancel")}
                </Button>
                <Button type="submit">{t("change_password")}</Button>
              </div>
            </form>
          </div>
        </div>
      )}

      <Tabs
        defaultValue="account"
        value={activeTab}
        onValueChange={setActiveTab}
        className="w-full"
      >
        <TabsList className="mb-4">
          <TabsTrigger value="account">{t("account")}</TabsTrigger>
          <TabsTrigger value="preferences">{t("preferences")}</TabsTrigger>
          {isAdmin && (
            <>
              <TabsTrigger value="user-management">
                <Users className="h-4 w-4 mr-2" />
                {t("user_management")}
              </TabsTrigger>
              <TabsTrigger value="system">
                <Sliders className="h-4 w-4 mr-2" />
                {t("system")}
              </TabsTrigger>
              <TabsTrigger value="data-viewer">
                <Database className="h-4 w-4 mr-2" />
                {t("data_viewer")}
              </TabsTrigger>
              <TabsTrigger value="advanced-settings">
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  className="h-4 w-4 mr-2"
                  width="24"
                  height="24"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="2"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                >
                  <path d="M12 20a8 8 0 1 0 0-16 8 8 0 0 0 0 16Z" />
                  <path d="M12 14a2 2 0 1 0 0-4 2 2 0 0 0 0 4Z" />
                  <path d="M12 2v2" />
                  <path d="M12 22v-2" />
                  <path d="m17 20.66-1-1.73" />
                  <path d="M11 10.27 7 3.34" />
                  <path d="m20.66 17-1.73-1" />
                  <path d="m3.34 7 1.73 1" />
                  <path d="M14 12h8" />
                  <path d="M2 12h2" />
                  <path d="m20.66 7-1.73 1" />
                  <path d="m3.34 17 1.73-1" />
                  <path d="m17 3.34-1 1.73" />
                  <path d="m11 13.73-4 6.93" />
                </svg>
                {t("advanced_settings")}
              </TabsTrigger>
              <TabsTrigger value="currency-management">
                {t("currency_management")}
              </TabsTrigger>
            </>
          )}
        </TabsList>

        {/* Account Settings */}
        <TabsContent value="account" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>{t("profile_information")}</CardTitle>
              <CardDescription>
                {t("update_your_profile_details")}
              </CardDescription>
            </CardHeader>
            <CardContent>
              <form onSubmit={handleProfileSubmit} className="space-y-4">
                <div className="flex flex-col space-y-1.5">
                  <Label htmlFor="username">{t("username")}</Label>
                  <Input
                    id="username"
                    name="username"
                    value={profileForm.username}
                    disabled
                    className="bg-muted"
                  />
                  <p className="text-sm text-muted-foreground">
                    {t("username_cannot_change")}
                  </p>
                </div>

                <div className="flex flex-col space-y-1.5">
                  <Label htmlFor="email">{t("email")}</Label>
                  <Input
                    id="email"
                    name="email"
                    value={profileForm.email}
                    onChange={handleInputChange}
                    placeholder="email@example.com"
                    className={errors.email ? "border-red-500" : ""}
                  />
                  {errors.email && (
                    <p className="text-sm text-red-500">{errors.email}</p>
                  )}
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div className="flex flex-col space-y-1.5">
                    <Label htmlFor="first_name">{t("first_name")}</Label>
                    <Input
                      id="first_name"
                      name="first_name"
                      value={profileForm.first_name}
                      onChange={handleInputChange}
                      placeholder={t("first_name")}
                    />
                  </div>

                  <div className="flex flex-col space-y-1.5">
                    <Label htmlFor="last_name">{t("last_name")}</Label>
                    <Input
                      id="last_name"
                      name="last_name"
                      value={profileForm.last_name}
                      onChange={handleInputChange}
                      placeholder={t("last_name")}
                    />
                  </div>
                </div>

                <div className="flex justify-end">
                  <Button type="submit" disabled={updateProfile.isPending}>
                    <Save className="h-4 w-4 mr-2" />
                    {t("save_changes")}
                  </Button>
                </div>

                {successMessage && (
                  <div className="p-3 bg-green-100 text-green-800 rounded-md">
                    {successMessage}
                  </div>
                )}
              </form>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>{t("account_security")}</CardTitle>
              <CardDescription>{t("manage_account_security")}</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <Button
                variant="outline"
                onClick={() => setShowPasswordDialog(true)}
              >
                {t("change_password")}
              </Button>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Preferences Settings */}
        <TabsContent value="preferences" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>{t("preferences")}</CardTitle>
              <CardDescription>
                {t("customize_your_experience")}
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-center justify-between">
                <div className="space-y-0.5">
                  <Label htmlFor="email_notifications">
                    {t("email_notifications")}
                  </Label>
                  <p className="text-sm text-muted-foreground">
                    {t("email_notifications_description")}
                  </p>
                </div>
                <Switch id="email_notifications" defaultChecked={true} />
              </div>

              <div className="flex items-center justify-between">
                <div className="space-y-0.5">
                  <Label htmlFor="dashboard_welcome">
                    {t("dashboard_welcome")}
                  </Label>
                  <p className="text-sm text-muted-foreground">
                    {t("dashboard_welcome_description")}
                  </p>
                </div>
                <Switch id="dashboard_welcome" defaultChecked={true} />
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Admin Only: User Management */}
        {isAdmin && (
          <TabsContent value="user-management" className="space-y-4">
            <div className="container py-6 md:py-10">
              <h1 className="text-3xl font-bold mb-6">User Management</h1>

              <Tabs defaultValue="users" className="w-full">
                <TabsList className="grid grid-cols-4 mb-8">
                  <TabsTrigger value="users">Users</TabsTrigger>
                  <TabsTrigger value="groups">Groups</TabsTrigger>
                  <TabsTrigger value="permissions">Permissions</TabsTrigger>
                  <TabsTrigger value="password-policy">Password Policy</TabsTrigger>
                </TabsList>

                <TabsContent value="users" className="space-y-4">
                  <UserManagement />
                </TabsContent>

                <TabsContent value="groups" className="space-y-4">
                  <GroupManagement />
                </TabsContent>

                <TabsContent value="permissions" className="space-y-4">
                  <PermissionManagement />
                </TabsContent>

                <TabsContent value="password-policy" className="space-y-4">
                  <PasswordPolicyManagement />
                </TabsContent>
              </Tabs>
            </div>
          </TabsContent>
        )}

        {/* Admin Only: System Settings */}
        {isAdmin && (
          <TabsContent value="system" className="space-y-4">
            <IntegrationDashboard />
            <SyncWorkflows />
            {/* <Card>
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
            </Card> */}
          </TabsContent>
        )}

        {/* Admin Only: Data Viewer */}
        {isAdmin && (
          <TabsContent value="data-viewer" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle>{t("database_viewer")}</CardTitle>
                <CardDescription>
                  {t("view_and_export_database_tables")}
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="flex mb-4">
                  <div className="relative flex-1">
                    <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
                    <Input
                      placeholder={t("search_tables")}
                      className="pl-8"
                      value={searchQuery}
                      onChange={(e) => setSearchQuery(e.target.value)}
                    />
                  </div>
                </div>

                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>{t("table_name")}</TableHead>
                      <TableHead>{t("row_count")}</TableHead>
                      <TableHead>{t("last_updated")}</TableHead>
                      <TableHead className="text-right">
                        {t("actions")}
                      </TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {filteredTables.map((table) => (
                      <TableRow key={table.name}>
                        <TableCell className="font-medium">
                          {table.name}
                        </TableCell>
                        <TableCell>{table.rows}</TableCell>
                        <TableCell>{table.last_updated}</TableCell>
                        <TableCell className="text-right">
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => handleDownload(table.name)}
                          >
                            <Download className="h-4 w-4 mr-2" />
                            {t("export_excel")}
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

        {/* Admin Only: Advanced Settings */}
        {isAdmin && (
          <TabsContent
            value="advanced-settings"
            className="space-y-4 border-2 border-blue-500 p-4"
          >
            <Card className="border-2 border-red-500">
              <CardHeader>
                <CardTitle>{t("system_configuration")}</CardTitle>
                <CardDescription>
                  {t("configure_advanced_system_settings")}
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                <div className="flex items-center justify-between">
                  <div className="space-y-0.5">
                    <Label htmlFor="maintenance-mode">
                      {t("maintenance_mode")}
                    </Label>
                    <p className="text-sm text-muted-foreground">
                      {t("maintenance_mode_description")}
                    </p>
                  </div>
                  <Switch
                    id="maintenance-mode"
                    checked={advancedSettings.maintenanceMode}
                    onCheckedChange={(checked) =>
                      handleAdvancedSettingChange("maintenanceMode", checked)
                    }
                  />
                </div>

                <div className="flex items-center justify-between">
                  <div className="space-y-0.5">
                    <Label htmlFor="debug-mode">{t("debug_mode")}</Label>
                    <p className="text-sm text-muted-foreground">
                      {t("debug_mode_description")}
                    </p>
                  </div>
                  <Switch
                    id="debug-mode"
                    checked={advancedSettings.debugMode}
                    onCheckedChange={(checked) =>
                      handleAdvancedSettingChange("debugMode", checked)
                    }
                  />
                </div>

                <div className="space-y-1.5">
                  <Label htmlFor="cache-lifetime">{t("cache_lifetime")}</Label>
                  <div className="flex items-center space-x-2">
                    <Input
                      id="cache-lifetime"
                      type="number"
                      value={advancedSettings.cacheLifetime}
                      onChange={(e) =>
                        handleAdvancedSettingChange(
                          "cacheLifetime",
                          parseInt(e.target.value)
                        )
                      }
                      className="max-w-[180px]"
                    />
                    <span className="text-sm text-muted-foreground">
                      {t("seconds")}
                    </span>
                  </div>
                  <p className="text-sm text-muted-foreground">
                    {t("cache_lifetime_description")}
                  </p>
                </div>

                <div className="space-y-1.5">
                  <Label htmlFor="log-level">{t("log_level")}</Label>
                  <select
                    id="log-level"
                    value={advancedSettings.logLevel}
                    onChange={(e) =>
                      handleAdvancedSettingChange("logLevel", e.target.value)
                    }
                    className="w-full rounded-md border border-input bg-background px-3 py-2"
                  >
                    <option value="debug">Debug</option>
                    <option value="info">Info</option>
                    <option value="warning">Warning</option>
                    <option value="error">Error</option>
                  </select>
                  <p className="text-sm text-muted-foreground">
                    {t("log_level_description")}
                  </p>
                </div>

                <div className="flex justify-end">
                  <Button onClick={handleAdvancedSettingsSave}>
                    <Save className="h-4 w-4 mr-2" />
                    {t("save_configuration")}
                  </Button>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>{t("system_information")}</CardTitle>
                <CardDescription>{t("view_system_details")}</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <p className="text-sm font-medium">{t("system_version")}</p>
                    <p className="text-sm text-muted-foreground">
                      {systemInfo.version}
                    </p>
                  </div>
                  <div>
                    <p className="text-sm font-medium">
                      {t("database_version")}
                    </p>
                    <p className="text-sm text-muted-foreground">
                      {systemInfo.databaseVersion}
                    </p>
                  </div>
                  <div>
                    <p className="text-sm font-medium">
                      {t("server_environment")}
                    </p>
                    <p className="text-sm text-muted-foreground">
                      {systemInfo.environment}
                    </p>
                  </div>
                  <div>
                    <p className="text-sm font-medium">
                      {t("last_system_update")}
                    </p>
                    <p className="text-sm text-muted-foreground">
                      {systemInfo.lastUpdate}
                    </p>
                  </div>
                </div>

                <div className="mt-6 border-t pt-6">
                  <h3 className="text-sm font-medium mb-4">
                    {t("user_debug_info")}
                  </h3>
                  <div className="space-y-3">
                    <div>
                      <p className="text-sm font-medium">{t("username")}</p>
                      <p className="text-sm text-muted-foreground">
                        {user?.username || "N/A"}
                      </p>
                    </div>
                    <div>
                      <p className="text-sm font-medium">{t("user_group")}</p>
                      <p className="text-sm text-muted-foreground">{"N/A"}</p>
                    </div>
                    <div>
                      <p className="text-sm font-medium">{t("admin_status")}</p>
                      <p className="text-sm text-muted-foreground">
                        {user?.isAdmin ? t("admin_yes") : t("admin_no")}
                      </p>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        )}

        {/* Admin only: Currency Management */}
        {isAdmin && (
          <TabsContent value="currency-management" className="space-y-4">
            {/* <div>Hi currency management</div> */}
            <CurrencyProvider>
              <CurrencyList />
            </CurrencyProvider>
          </TabsContent>
        )}
      </Tabs>
    </div>
  );
}
