"use client"

import { useState, useEffect } from "react"
import { useMutation, useQueryClient } from "@tanstack/react-query"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert"
import { Card, CardContent } from "@/components/ui/card"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { AlertTriangle, Copy, CheckCircle2, Smartphone, Key } from "lucide-react"
import { setupTwoFactor, enableTwoFactor } from "@/lib/api/profile"
import type { TwoFactorSetup, User } from "@/lib/types"
import Image from 'next/image'

interface TwoFactorSetupDialogProps {
  user: User
  open: boolean
  onOpenChange: (open: boolean) => void
  onSuccess?: () => void
}

export function TwoFactorSetupDialog({ user, open, onOpenChange, onSuccess }: TwoFactorSetupDialogProps) {
  const queryClient = useQueryClient()
  const [setupData, setSetupData] = useState<TwoFactorSetup | null>(null)
  const [verificationCode, setVerificationCode] = useState("")
  const [activeTab, setActiveTab] = useState("app")
  const [errorMessage, setErrorMessage] = useState("")
  const [successMessage, setSuccessMessage] = useState("")
  const [copiedSecret, setCopiedSecret] = useState(false)
  const [copiedBackupCodes, setCopiedBackupCodes] = useState(false)
  const [setupStep, setSetupStep] = useState<"setup" | "verify" | "backup" | "complete">("setup")

  const setupMutation = useMutation({
    mutationFn: () => setupTwoFactor(user.id),
    onSuccess: (data) => {
      setSetupData(data)
      setSetupStep("verify")
    },
    onError: () => {
      setErrorMessage("Failed to setup two-factor authentication")
    },
  })

  const enableMutation = useMutation({
    mutationFn: (token: string) => enableTwoFactor(user.id, token),
    onSuccess: (response) => {
      if (response.success) {
        setSuccessMessage(response.message)
        setSetupStep("backup")
        // Aktualisiere den Cache für den spezifischen Benutzer und die allgemeine Benutzerliste
        queryClient.invalidateQueries({ queryKey: ["users", user.id] })
        queryClient.invalidateQueries({ queryKey: ["users"] })
      } else {
        setErrorMessage(response.message)
      }
    },
  })

  useEffect(() => {
    if (open && !setupData) {
      setupMutation.mutate()
    }
  }, [open, setupData, setupMutation])

  const handleVerify = () => {
    setErrorMessage("")
    setSuccessMessage("")
    enableMutation.mutate(verificationCode)
  }

  const handleCopySecret = () => {
    if (setupData?.secret) {
      navigator.clipboard.writeText(setupData.secret)
      setCopiedSecret(true)
      setTimeout(() => setCopiedSecret(false), 2000)
    }
  }

  const handleCopyBackupCodes = () => {
    if (setupData?.backupCodes) {
      navigator.clipboard.writeText(setupData.backupCodes.join("\n"))
      setCopiedBackupCodes(true)
      setTimeout(() => setCopiedBackupCodes(false), 2000)
    }
  }

  const handleComplete = () => {
    onOpenChange(false)
    if (onSuccess) onSuccess()
  }

  const handleClose = () => {
    setSetupData(null)
    setVerificationCode("")
    setErrorMessage("")
    setSuccessMessage("")
    setSetupStep("setup")
    onOpenChange(false)
  }

  return (
    <Dialog open={open} onOpenChange={handleClose}>
      <DialogContent className="sm:max-w-[500px]">
        <DialogHeader>
          <DialogTitle>
            {setupStep === "setup" && "Setting up Two-Factor Authentication..."}
            {setupStep === "verify" && "Verify Two-Factor Authentication"}
            {setupStep === "backup" && "Save Your Backup Codes"}
            {setupStep === "complete" && "Setup Complete"}
          </DialogTitle>
          <DialogDescription>
            {setupStep === "setup" && "Preparing your two-factor authentication setup..."}
            {setupStep === "verify" && "Scan the QR code with your authenticator app and enter the verification code"}
            {setupStep === "backup" &&
              "Store these backup codes in a safe place. You can use them to access your account if you lose your device."}
            {setupStep === "complete" && "Two-factor authentication has been successfully enabled for your account."}
          </DialogDescription>
        </DialogHeader>

        {errorMessage && (
          <Alert variant="destructive" className="mt-2">
            <AlertTriangle className="h-4 w-4" />
            <AlertTitle>Error</AlertTitle>
            <AlertDescription>{errorMessage}</AlertDescription>
          </Alert>
        )}

        {successMessage && (
          <Alert variant="default" className="mt-2">
            <CheckCircle2 className="h-4 w-4" />
            <AlertTitle>Success</AlertTitle>
            <AlertDescription>{successMessage}</AlertDescription>
          </Alert>
        )}

        {setupStep === "setup" && (
          <div className="flex justify-center py-8">
            <div className="animate-pulse flex flex-col items-center">
              <Smartphone className="h-16 w-16 mb-4 text-primary" />
              <p>Setting up two-factor authentication...</p>
            </div>
          </div>
        )}

        {setupStep === "verify" && setupData && (
          <div className="py-4">
            <Tabs value={activeTab} onValueChange={setActiveTab}>
              <TabsList className="grid grid-cols-2 mb-4">
                <TabsTrigger value="app">Authenticator App</TabsTrigger>
                <TabsTrigger value="manual">Manual Setup</TabsTrigger>
              </TabsList>

              <TabsContent value="app" className="space-y-4">
                <div className="flex justify-center">
                  <Card className="border p-4 rounded bg-white">
                    <CardContent className="p-0">
                      <Image
                        src={setupData.qrCodeUrl || "/placeholder.svg"}
                        alt="QR Code for two-factor authentication setup"
                        width={200}
                        height={200}
                        className="mx-auto"
                      />
                    </CardContent>
                  </Card>
                </div>
                <p className="text-sm text-center text-muted-foreground">
                  Scan this QR code with your authenticator app (Google Authenticator, Authy, etc.)
                </p>
              </TabsContent>

              <TabsContent value="manual" className="space-y-4">
                <div className="space-y-2">
                  <Label>Secret Key</Label>
                  <div className="flex">
                    <Input value={setupData.secret} readOnly className="font-mono text-sm" />
                    <Button variant="outline" size="icon" className="ml-2" onClick={handleCopySecret}>
                      {copiedSecret ? <CheckCircle2 className="h-4 w-4" /> : <Copy className="h-4 w-4" />}
                    </Button>
                  </div>
                </div>
                <div className="space-y-2">
                  <Label>Manual Entry URI</Label>
                  <p className="text-xs text-muted-foreground break-all font-mono">{setupData.verificationUrl}</p>
                </div>
              </TabsContent>
            </Tabs>

            <div className="space-y-2 mt-6">
              <Label htmlFor="verificationCode">Verification Code</Label>
              <Input
                id="verificationCode"
                placeholder="Enter 6-digit code"
                value={verificationCode}
                onChange={(e) => setVerificationCode(e.target.value)}
                className="font-mono text-center text-lg tracking-widest"
                maxLength={6}
              />
            </div>
          </div>
        )}

        {setupStep === "backup" && setupData && (
          <div className="py-4">
            <div className="space-y-4">
              <Alert>
                <Key className="h-4 w-4" />
                <AlertTitle>Important</AlertTitle>
                <AlertDescription>
                  These backup codes can only be used once each. Store them somewhere safe and accessible.
                </AlertDescription>
              </Alert>

              <div className="bg-muted p-4 rounded-md">
                <div className="flex justify-between items-center mb-2">
                  <Label>Backup Codes</Label>
                  <Button variant="outline" size="sm" className="h-8" onClick={handleCopyBackupCodes}>
                    {copiedBackupCodes ? (
                      <>
                        <CheckCircle2 className="h-4 w-4 mr-2" />
                        Copied
                      </>
                    ) : (
                      <>
                        <Copy className="h-4 w-4 mr-2" />
                        Copy All
                      </>
                    )}
                  </Button>
                </div>
                <div className="grid grid-cols-2 gap-2">
                  {setupData.backupCodes.map((code, index) => (
                    <code key={index} className="block font-mono text-sm bg-background p-2 rounded">
                      {code}
                    </code>
                  ))}
                </div>
              </div>

              <p className="text-sm text-muted-foreground">
                Each backup code can be used once to sign in if you don't have access to your authenticator app.
              </p>
            </div>
          </div>
        )}

        <DialogFooter className="mt-4">
          {setupStep === "setup" && (
            <Button type="button" variant="outline" onClick={handleClose}>
              Cancel
            </Button>
          )}

          {setupStep === "verify" && (
            <>
              <Button type="button" variant="outline" onClick={handleClose}>
                Cancel
              </Button>
              <Button
                type="button"
                onClick={handleVerify}
                disabled={enableMutation.isPending || verificationCode.length !== 6}
              >
                {enableMutation.isPending ? "Verifying..." : "Verify"}
              </Button>
            </>
          )}

          {setupStep === "backup" && (
            <Button type="button" onClick={() => setSetupStep("complete")}>
              I've saved my backup codes
            </Button>
          )}

          {setupStep === "complete" && (
            <Button type="button" onClick={handleComplete}>
              Done
            </Button>
          )}
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}

