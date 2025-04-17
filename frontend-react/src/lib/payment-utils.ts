import type { Document, PaymentStatus } from "@/types/document/document";

/**
 * Calculates the number of days an invoice is overdue.
 * @param document The document object (must be an INVOICE).
 * @returns Number of days overdue, or null if not applicable or not overdue.
 */
export function calculateDaysOverdue(document: Document): number | null {
  if (document.type !== "INVOICE" || !document.paymentInfo?.dueDate) {
    return null;
  }

  try {
    const dueDate = new Date(document.paymentInfo.dueDate);
    const today = new Date();
    // Reset time portion to compare dates only
    today.setHours(0, 0, 0, 0);
    dueDate.setHours(0, 0, 0, 0);

    if (isNaN(dueDate.getTime())) {
      console.warn("Invalid due date provided:", document.paymentInfo.dueDate);
      return null;
    }

    if (today > dueDate) {
      const diffTime = Math.abs(today.getTime() - dueDate.getTime());
      const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
      return diffDays;
    }

    return 0; // Not overdue yet
  } catch (error) {
    console.error("Error calculating days overdue:", error);
    return null;
  }
}


/**
 * Calculates the payment status of an invoice based on due date and reminders.
 * @param document The document object (must be an INVOICE).
 * @returns The calculated PaymentStatus or null if not applicable.
 */
export function calculatePaymentStatus(document: Document): PaymentStatus | null {
  if (document.type !== "INVOICE" || !document.paymentInfo) {
    return null;
  }

  // If already marked as PAID in the data, respect that.
  if (document.paymentInfo.status === "PAID" || document.paymentInfo.paymentDate) {
    return "PAID";
  }

  // If status is already set to collection, respect that.
  if (document.paymentInfo.status === "COLLECTION") {
      return "COLLECTION";
  }

  const daysOverdue = calculateDaysOverdue(document);

  if (daysOverdue === null) {
    // If we can't calculate days overdue (e.g., missing due date), assume OPEN
    return "OPEN";
  }

  if (daysOverdue > 0) {
    const remindersSent = document.paymentInfo.remindersSent ?? 0;
    if (remindersSent >= 3) { // Assuming 3 reminders before collection
        return "COLLECTION";
    } else if (remindersSent === 2) {
        return "REMINDER_3"; // Status after 2nd reminder sent
    } else if (remindersSent === 1) {
        return "REMINDER_2"; // Status after 1st reminder sent
    } else if (remindersSent === 0) {
        // Check if a reminder status was manually set previously
        if (document.paymentInfo.status === "REMINDER_1") return "REMINDER_1";
        return "OVERDUE"; // Overdue but no reminders sent yet
    }
    // Fallback if remindersSent is somehow negative or logic is inconsistent
    return "OVERDUE";
  } else {
    return "OPEN"; // Not overdue
  }
}


/**
 * Gets the user-friendly text representation of a PaymentStatus.
 * @param status The PaymentStatus enum value.
 * @returns Localized string for the status.
 */
export function getPaymentStatusText(status: PaymentStatus): string {
  switch (status) {
    case "PAID": return "Bezahlt";
    case "OPEN": return "Offen";
    case "OVERDUE": return "Überfällig";
    case "REMINDER_1": return "1. Mahnung";
    case "REMINDER_2": return "2. Mahnung";
    case "REMINDER_3": return "3. Mahnung";
    case "COLLECTION": return "Inkasso";
    default: return "Unbekannt";
  }
}

/**
 * Gets the Tailwind CSS class string for badge color based on PaymentStatus.
 * @param status The PaymentStatus enum value.
 * @returns Tailwind CSS class string.
 */
export function getPaymentStatusColor(status: PaymentStatus): string {
  switch (status) {
    case "PAID":
      return "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200";
    case "OPEN":
      return "bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200"; // Using blue for open/pending state
    case "OVERDUE":
      return "bg-amber-100 text-amber-800 dark:bg-amber-900 dark:text-amber-200";
    case "REMINDER_1":
    case "REMINDER_2":
    case "REMINDER_3":
      return "bg-orange-100 text-orange-800 dark:bg-orange-900 dark:text-orange-200"; // Orange for reminders
    case "COLLECTION":
      return "bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200"; // Red for collection
    default:
      return "bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-200";
  }
} 