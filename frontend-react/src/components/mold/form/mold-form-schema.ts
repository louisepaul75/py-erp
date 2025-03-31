import { z } from "zod"
import { validateMoldNumber } from "@/lib/mold/validation"
import { MoldActivityStatus } from "@/types/mold/mold"

/**
 * Schema for mold form validation
 */
export const moldFormSchema = z.object({
  legacyMoldNumber: z.string().min(1, "Legacy mold number is required"),
  moldNumber: z.string().min(1, "Mold number is required").refine(validateMoldNumber, {
    message: "Mold number must be in format F1xxxx (F1 followed by 4 digits)",
  }),
  technology: z.string().min(1, "Technology is required"),
  alloy: z.string().min(1, "Alloy is required"),
  warehouseLocation: z.string().min(1, "Warehouse location is required"),
  numberOfArticles: z.coerce
    .number()
    .int("Number of articles must be an integer")
    .min(0, "Number of articles must be positive"),
  isActive: z.boolean().default(true),
  activityStatus: z.nativeEnum(MoldActivityStatus).optional(),
  tags: z.array(z.string()).default([]),

  // Neue Felder
  startDate: z.string().optional(),
  endDate: z.string().optional(),
  imageUrl: z.string().optional(),
  moldSize: z.string().optional(),
})

/**
 * Type for the form values
 */
export type MoldFormValues = z.infer<typeof moldFormSchema>

