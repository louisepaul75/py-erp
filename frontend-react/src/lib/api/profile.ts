import type { User, PasswordPolicy, TwoFactorSetup } from "../types"
import { users } from "./users"

// Simulate API calls with delays
const delay = (ms: number) => new Promise((resolve) => setTimeout(resolve, ms))

// Default password policy
let passwordPolicy: PasswordPolicy = {
  minLength: 8,
  requireUppercase: true,
  requireLowercase: true,
  requireNumbers: true,
  requireSpecialChars: true,
}

export async function fetchPasswordPolicy(): Promise<PasswordPolicy> {
  await delay(300)
  return passwordPolicy
}

export async function updatePasswordPolicy(policy: PasswordPolicy): Promise<PasswordPolicy> {
  await delay(500)
  passwordPolicy = { ...policy }
  return passwordPolicy
}

export async function validatePassword(password: string): Promise<{ valid: boolean; issues: string[] }> {
  await delay(300)
  const issues: string[] = []

  if (password.length < passwordPolicy.minLength) {
    issues.push(`Password must be at least ${passwordPolicy.minLength} characters`)
  }

  if (passwordPolicy.requireUppercase && !/[A-Z]/.test(password)) {
    issues.push("Password must contain at least one uppercase letter")
  }

  if (passwordPolicy.requireLowercase && !/[a-z]/.test(password)) {
    issues.push("Password must contain at least one lowercase letter")
  }

  if (passwordPolicy.requireNumbers && !/[0-9]/.test(password)) {
    issues.push("Password must contain at least one number")
  }

  if (passwordPolicy.requireSpecialChars && !/[!@#$%^&*(),.?":{}|<>]/.test(password)) {
    issues.push("Password must contain at least one special character")
  }

  return { valid: issues.length === 0, issues }
}

export async function changePassword(
  userId: string,
  currentPassword: string,
  newPassword: string,
): Promise<{ success: boolean; message: string }> {
  await delay(500)

  // In a real app, you would verify the current password
  const validation = await validatePassword(newPassword)

  if (!validation.valid) {
    return { success: false, message: validation.issues.join(". ") }
  }

  // Update the user's password
  const userIndex = users.findIndex((u) => u.id === userId)
  if (userIndex >= 0) {
    users[userIndex] = {
      ...users[userIndex],
      passwordLastChanged: new Date(),
      requirePasswordChange: false,
    }
    return { success: true, message: "Password changed successfully" }
  }

  return { success: false, message: "User not found" }
}

export async function resetPassword(userId: string): Promise<{ success: boolean; message: string }> {
  await delay(500)

  // Find and update the user
  const userIndex = users.findIndex((u) => u.id === userId)
  if (userIndex >= 0) {
    users[userIndex] = {
      ...users[userIndex],
      requirePasswordChange: true,
    }

    // In a real app, you would generate a temporary password and send an email
    return { success: true, message: "Password reset link sent to user's email" }
  }

  return { success: false, message: "User not found" }
}

export async function updateUserProfile(
  userId: string,
  profileData: Partial<User>,
): Promise<{ success: boolean; user?: User; message: string }> {
  await delay(500)

  const userIndex = users.findIndex((u) => u.id === userId)
  if (userIndex >= 0) {
    // Only allow updating certain fields
    const allowedFields: (keyof User)[] = ["name", "email", "phone"]
    const updatedUser = { ...users[userIndex] }

    for (const field of allowedFields) {
      if (field in profileData) {
        updatedUser[field] = profileData[field] as any
      }
    }

    users[userIndex] = updatedUser
    return { success: true, user: updatedUser, message: "Profile updated successfully" }
  }

  return { success: false, message: "User not found" }
}

export async function toggleUserActive(userId: string, isActive: boolean): Promise<User> {
  await delay(500)

  const userIndex = users.findIndex((u) => u.id === userId)
  if (userIndex >= 0) {
    users[userIndex] = {
      ...users[userIndex],
      isActive,
    }
    return users[userIndex]
  }

  throw new Error("User not found")
}

// Verbesserte 2FA-Funktionen mit QR-Code
export async function setupTwoFactor(userId: string): Promise<TwoFactorSetup> {
  await delay(700)

  // In einer echten App würde hier ein Secret generiert und ein QR-Code erstellt werden
  // Für dieses Beispiel verwenden wir ein statisches QR-Code-Bild
  return {
    secret: "JBSWY3DPEHPK3PXP",
    qrCodeUrl: "https://v0.blob.com/qrcode-example.png",
    verificationUrl: "otpauth://totp/ERP:john@example.com?secret=JBSWY3DPEHPK3PXP&issuer=ERP",
    backupCodes: [
      "12345-67890",
      "abcde-fghij",
      "klmno-pqrst",
      "uvwxy-zabcd",
      "98765-43210",
      "mnbvc-xzlkj",
      "poiuy-trewq",
      "asdfg-hjkl",
    ],
  }
}

export async function verifyTwoFactorToken(token: string): Promise<boolean> {
  await delay(300)

  // In einer echten App würde der Token gegen das Secret geprüft werden
  // Für dieses Beispiel akzeptieren wir "123456" als gültigen Token
  return token === "123456"
}

export async function enableTwoFactor(userId: string, token: string): Promise<{ success: boolean; message: string }> {
  await delay(500)

  // Verifiziere den Token
  const isValid = await verifyTwoFactorToken(token)

  if (!isValid) {
    return { success: false, message: "Invalid verification code" }
  }

  // Aktiviere 2FA für den Benutzer
  const userIndex = users.findIndex((u) => u.id === userId)
  if (userIndex >= 0) {
    users[userIndex] = {
      ...users[userIndex],
      twoFactorEnabled: true,
    }
    return { success: true, message: "Two-factor authentication enabled" }
  }

  return { success: false, message: "Failed to enable two-factor authentication" }
}

export async function disableTwoFactor(userId: string): Promise<{ success: boolean; message: string }> {
  await delay(500)

  const userIndex = users.findIndex((u) => u.id === userId)
  if (userIndex >= 0) {
    users[userIndex] = {
      ...users[userIndex],
      twoFactorEnabled: false,
    }
    return { success: true, message: "Two-factor authentication disabled" }
  }

  return { success: false, message: "Failed to disable two-factor authentication" }
}

