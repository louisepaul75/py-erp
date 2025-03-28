"use client"

import type React from "react"

import { useState } from "react"
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query"
import { User, AlertTriangle, BadgeCheck, Shield } from "lucide-react"
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Avatar, AvatarFallback } from "@/components/ui/avatar"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog"
import { updateUserProfile, changePassword, disableTwoFactor } from "@/lib/api/profile"
import { fetchUserById } from "@/lib/api/users"
import { TwoFactorSetupDialog } from "./two-factor-setup"
import type { User as UserType } from "@/lib/types"

interface ProfileManagementProps {
  user: UserType
}

export function ProfileManagement({ user }: ProfileManagementProps) {
  const queryClient = useQueryClient()
  const [profileForm, setProfileForm] = useState({
    name: user.name || "",
    email: user.email || "",
    phone: user.phone || "",
  })
  const [passwordForm, setPasswordForm] = useState({
    currentPassword: "",
    newPassword: "",
    confirmPassword: "",
  })
  const [showTwoFactorSetupDialog, setShowTwoFactorSetupDialog] = useState(false)
  const [showDisableTwoFactorDialog, setShowDisableTwoFactorDialog] = useState(false)
  const [errorMessage, setErrorMessage] = useState("")
  const [successMessage, setSuccessMessage] = useState("")

  // Hole den aktuellen Benutzerstatus, um sicherzustellen, dass wir immer den neuesten 2FA-Status haben
  const { data: currentUser } = useQuery({
    queryKey: ["users", user.id],
    queryFn: () => fetchUserById(user.id),
    initialData: user,
  })

  const updateProfileMutation = useMutation({
    mutationFn: (data: Partial<UserType>) => updateUserProfile(user.id, data),
    onSuccess: (response) => {
      if (response.success) {
        setSuccessMessage("Profile updated successfully")
        queryClient.invalidateQueries({ queryKey: ["users"] })
      } else {
        setErrorMessage(response.message)
      }
    },
  })

  const changePasswordMutation = useMutation({
    mutationFn: (data: { currentPassword: string; newPassword: string }) =>
      changePassword(user.id, data.currentPassword, data.newPassword),
    onSuccess: (response) => {
      if (response.success) {
        setSuccessMessage("Password changed successfully")
        setPasswordForm({
          currentPassword: "",
          newPassword: "",
          confirmPassword: "",
        })
      } else {
        setErrorMessage(response.message)
      }
    },
  })

  const disableTwoFactorMutation = useMutation({
    mutationFn: () => disableTwoFactor(user.id),
    onSuccess: (response) => {
      if (response.success) {
        setSuccessMessage("Two-factor authentication disabled")
        setShowDisableTwoFactorDialog(false)
        // Wichtig: Invalidiere die Benutzerabfrage, um den aktuellen Status zu erhalten
        queryClient.invalidateQueries({ queryKey: ["users", user.id] })
        queryClient.invalidateQueries({ queryKey: ["users"] })
      } else {
        setErrorMessage(response.message)
      }
    },
  })

  const handleProfileSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    setErrorMessage("")
    setSuccessMessage("")
    updateProfileMutation.mutate(profileForm)
  }

  const handlePasswordSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    setErrorMessage("")
    setSuccessMessage("")

    if (passwordForm.newPassword !== passwordForm.confirmPassword) {
      setErrorMessage("Passwords do not match")
      return
    }

    changePasswordMutation.mutate({
      currentPassword: passwordForm.currentPassword,
      newPassword: passwordForm.newPassword,
    })
  }

  const handleTwoFactorSetup = () => {
    setErrorMessage("")
    setSuccessMessage("")
    setShowTwoFactorSetupDialog(true)
  }

  const handleDisableTwoFactor = () => {
    setShowDisableTwoFactorDialog(true)
  }

  const confirmDisableTwoFactor = () => {
    setErrorMessage("")
    disableTwoFactorMutation.mutate()
  }

  return (
    <>
      <div className="grid gap-6">
        <Card>
          <CardHeader className="space-y-1">
            <div className="flex items-center space-x-4">
              <Avatar className="h-16 w-16">
                <AvatarFallback className="text-lg">
                  {currentUser.name
                    .split(" ")
                    .map((n) => n[0])
                    .join("")}
                </AvatarFallback>
              </Avatar>
              <div>
                <CardTitle className="text-2xl">{currentUser.name}</CardTitle>
                <CardDescription>{currentUser.email}</CardDescription>
              </div>
            </div>
          </CardHeader>
        </Card>

        {(errorMessage || successMessage) && (
          <Alert variant={errorMessage ? "destructive" : "default"}>
            <AlertTriangle className="h-4 w-4" />
            <AlertTitle>{errorMessage ? "Error" : "Success"}</AlertTitle>
            <AlertDescription>{errorMessage || successMessage}</AlertDescription>
          </Alert>
        )}

        <Tabs defaultValue="profile" className="w-full">
          <TabsList className="grid grid-cols-3 mb-8">
            <TabsTrigger value="profile">
              <User className="mr-2 h-4 w-4" />
              Profile
            </TabsTrigger>
            <TabsTrigger value="password">
              <Shield className="mr-2 h-4 w-4" />
              Password
            </TabsTrigger>
            <TabsTrigger value="security">
              <BadgeCheck className="mr-2 h-4 w-4" />
              Security
            </TabsTrigger>
          </TabsList>

          <TabsContent value="profile">
            <Card>
              <CardHeader>
                <CardTitle>Personal Information</CardTitle>
                <CardDescription>Update your personal details</CardDescription>
              </CardHeader>
              <form onSubmit={handleProfileSubmit}>
                <CardContent className="space-y-4">
                  <div className="space-y-2">
                    <Label htmlFor="name">Full Name</Label>
                    <Input
                      id="name"
                      value={profileForm.name}
                      onChange={(e) => setProfileForm({ ...profileForm, name: e.target.value })}
                      required
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="email">Email</Label>
                    <Input
                      id="email"
                      type="email"
                      value={profileForm.email}
                      onChange={(e) => setProfileForm({ ...profileForm, email: e.target.value })}
                      required
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="phone">Phone Number</Label>
                    <Input
                      id="phone"
                      value={profileForm.phone}
                      onChange={(e) => setProfileForm({ ...profileForm, phone: e.target.value })}
                    />
                  </div>
                </CardContent>
                <CardFooter>
                  <Button type="submit" disabled={updateProfileMutation.isPending}>
                    {updateProfileMutation.isPending ? "Saving..." : "Save Changes"}
                  </Button>
                </CardFooter>
              </form>
            </Card>
          </TabsContent>

          <TabsContent value="password">
            <Card>
              <CardHeader>
                <CardTitle>Password</CardTitle>
                <CardDescription>Change your password</CardDescription>
              </CardHeader>
              <form onSubmit={handlePasswordSubmit}>
                <CardContent className="space-y-4">
                  <div className="space-y-2">
                    <Label htmlFor="current-password">Current Password</Label>
                    <Input
                      id="current-password"
                      type="password"
                      value={passwordForm.currentPassword}
                      onChange={(e) => setPasswordForm({ ...passwordForm, currentPassword: e.target.value })}
                      required
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="new-password">New Password</Label>
                    <Input
                      id="new-password"
                      type="password"
                      value={passwordForm.newPassword}
                      onChange={(e) => setPasswordForm({ ...passwordForm, newPassword: e.target.value })}
                      required
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="confirm-password">Confirm New Password</Label>
                    <Input
                      id="confirm-password"
                      type="password"
                      value={passwordForm.confirmPassword}
                      onChange={(e) => setPasswordForm({ ...passwordForm, confirmPassword: e.target.value })}
                      required
                    />
                  </div>
                  {currentUser.passwordLastChanged && (
                    <div className="pt-2 text-sm text-muted-foreground">
                      Last changed: {currentUser.passwordLastChanged.toLocaleDateString()}
                    </div>
                  )}
                </CardContent>
                <CardFooter>
                  <Button type="submit" disabled={changePasswordMutation.isPending}>
                    {changePasswordMutation.isPending ? "Changing..." : "Change Password"}
                  </Button>
                </CardFooter>
              </form>
            </Card>
          </TabsContent>

          <TabsContent value="security">
            <Card>
              <CardHeader>
                <CardTitle>Two-Factor Authentication</CardTitle>
                <CardDescription>Add an extra layer of security to your account</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex items-center justify-between">
                  <div>
                    <h3 className="font-medium">Two-Factor Authentication</h3>
                    <p className="text-sm text-muted-foreground">
                      {currentUser.twoFactorEnabled
                        ? "Two-factor authentication is enabled"
                        : "Enable two-factor authentication for enhanced security"}
                    </p>
                  </div>
                  {currentUser.twoFactorEnabled ? (
                    <Button
                      variant="destructive"
                      onClick={handleDisableTwoFactor}
                      disabled={disableTwoFactorMutation.isPending}
                    >
                      Disable 2FA
                    </Button>
                  ) : (
                    <Button onClick={handleTwoFactorSetup}>Enable 2FA</Button>
                  )}
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>

      {/* Two-Factor Setup Dialog */}
      <TwoFactorSetupDialog
        user={currentUser}
        open={showTwoFactorSetupDialog}
        onOpenChange={setShowTwoFactorSetupDialog}
        onSuccess={() => {
          setSuccessMessage("Two-factor authentication enabled successfully")
          // Wichtig: Invalidiere die Benutzerabfrage, um den aktuellen Status zu erhalten
          queryClient.invalidateQueries({ queryKey: ["users", user.id] })
          queryClient.invalidateQueries({ queryKey: ["users"] })
        }}
      />

      {/* Disable Two-Factor Dialog */}
      <Dialog open={showDisableTwoFactorDialog} onOpenChange={setShowDisableTwoFactorDialog}>
        <DialogContent className="sm:max-w-[425px]">
          <DialogHeader>
            <DialogTitle>Disable Two-Factor Authentication</DialogTitle>
            <DialogDescription>
              Are you sure you want to disable two-factor authentication? This will make your account less secure.
            </DialogDescription>
          </DialogHeader>
          <DialogFooter>
            <Button type="button" variant="outline" onClick={() => setShowDisableTwoFactorDialog(false)}>
              Cancel
            </Button>
            <Button
              type="button"
              variant="destructive"
              onClick={confirmDisableTwoFactor}
              disabled={disableTwoFactorMutation.isPending}
            >
              {disableTwoFactorMutation.isPending ? "Disabling..." : "Disable 2FA"}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </>
  )
}

