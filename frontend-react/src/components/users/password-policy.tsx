"use client"

import type React from "react"

import { useState, useEffect } from "react"
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query"
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Label } from "@/components/ui/label"
import { Switch } from "@/components/ui/switch"
import { Slider } from "@/components/ui/slider"
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert"
import { AlertTriangle, CheckCircle2 } from "lucide-react"
import { fetchPasswordPolicy, updatePasswordPolicy } from "@/lib/api/profile"
import type { PasswordPolicy } from "@/lib/types"

export function PasswordPolicyManagement() {
  const queryClient = useQueryClient()
  const [formData, setFormData] = useState<PasswordPolicy>({
    minLength: 8,
    requireUppercase: true,
    requireLowercase: true,
    requireNumbers: true,
    requireSpecialChars: true,
  })
  const [errorMessage, setErrorMessage] = useState("")
  const [successMessage, setSuccessMessage] = useState("")

  const { data: policy, isLoading } = useQuery({
    queryKey: ["password-policy"],
    queryFn: fetchPasswordPolicy,
  })

  useEffect(() => {
    if (policy) {
      setFormData(policy)
    }
  }, [policy])

  const updatePolicyMutation = useMutation({
    mutationFn: updatePasswordPolicy,
    onSuccess: () => {
      setSuccessMessage("Password policy updated successfully")
      queryClient.invalidateQueries({ queryKey: ["password-policy"] })
    },
    onError: () => {
      setErrorMessage("Failed to update password policy")
    },
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    setErrorMessage("")
    setSuccessMessage("")
    updatePolicyMutation.mutate(formData)
  }

  const handleSwitchChange = (field: keyof PasswordPolicy) => {
    setFormData({
      ...formData,
      [field]: !formData[field as keyof PasswordPolicy],
    })
  }

  const handleNumberChange = (field: keyof PasswordPolicy, value: number) => {
    setFormData({
      ...formData,
      [field]: value,
    })
  }

  if (isLoading) {
    return <div className="flex justify-center p-4">Loading password policy...</div>
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Password Policy Settings</CardTitle>
        <CardDescription>Configure organization-wide password requirements</CardDescription>
      </CardHeader>
      <form onSubmit={handleSubmit}>
        <CardContent className="space-y-6">
          {(errorMessage || successMessage) && (
            <Alert variant={errorMessage ? "destructive" : "default"}>
              {errorMessage ? <AlertTriangle className="h-4 w-4" /> : <CheckCircle2 className="h-4 w-4" />}
              <AlertTitle>{errorMessage ? "Error" : "Success"}</AlertTitle>
              <AlertDescription>{errorMessage || successMessage}</AlertDescription>
            </Alert>
          )}

          <div className="space-y-4">
            <div>
              <Label htmlFor="minLength">Minimum Password Length</Label>
              <div className="flex items-center gap-4 mt-2">
                <Slider
                  id="minLength"
                  min={6}
                  max={24}
                  step={1}
                  value={[formData.minLength]}
                  onValueChange={(value) => handleNumberChange("minLength", value[0])}
                  className="flex-1"
                />
                <span className="w-8 text-center">{formData.minLength}</span>
              </div>
            </div>

            <div className="flex items-center justify-between">
              <Label htmlFor="requireUppercase">Require Uppercase Letters</Label>
              <Switch
                id="requireUppercase"
                checked={formData.requireUppercase}
                onCheckedChange={() => handleSwitchChange("requireUppercase")}
              />
            </div>

            <div className="flex items-center justify-between">
              <Label htmlFor="requireLowercase">Require Lowercase Letters</Label>
              <Switch
                id="requireLowercase"
                checked={formData.requireLowercase}
                onCheckedChange={() => handleSwitchChange("requireLowercase")}
              />
            </div>

            <div className="flex items-center justify-between">
              <Label htmlFor="requireNumbers">Require Numbers</Label>
              <Switch
                id="requireNumbers"
                checked={formData.requireNumbers}
                onCheckedChange={() => handleSwitchChange("requireNumbers")}
              />
            </div>

            <div className="flex items-center justify-between">
              <Label htmlFor="requireSpecialChars">Require Special Characters</Label>
              <Switch
                id="requireSpecialChars"
                checked={formData.requireSpecialChars}
                onCheckedChange={() => handleSwitchChange("requireSpecialChars")}
              />
            </div>
          </div>
        </CardContent>
        <CardFooter>
          <Button type="submit" disabled={updatePolicyMutation.isPending}>
            {updatePolicyMutation.isPending ? "Saving..." : "Save Changes"}
          </Button>
        </CardFooter>
      </form>
    </Card>
  )
}

