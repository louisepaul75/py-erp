import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { UserManagement } from "@/components/users/user-management"
import { GroupManagement } from "@/components/users/group-management"
import { PermissionManagement } from "@/components/users/permission-management"
import { PasswordPolicyManagement } from "@/components/users/password-policy"

export default function UsersPage() {
  return (
    <div className="container py-6 md:py-10 h-full overflow-auto">
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
  )
}

