"use client"
import { useForm } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"
import { z } from "zod"
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog"
import { Button } from "@/components/ui/button"
import { Form, FormControl, FormField, FormItem, FormLabel, FormMessage } from "@/components/ui/form"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { useCreateRelationship } from "@/hooks/document/use-document-relationships"
import { useDocuments } from "@/hooks/document/use-documents"

/**
 * Schema for relation creation form validation
 */
const formSchema = z.object({
  targetDocumentId: z.string().min(1, "Target document is required"),
  relationType: z.string().min(1, "Relation type is required"),
})

/**
 * Type for the form values
 */
type FormValues = z.infer<typeof formSchema>

/**
 * Props for the DocumentRelationCreateModal component
 */
interface DocumentRelationCreateModalProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  sourceDocumentId: string
}

/**
 * DocumentRelationCreateModal component that displays a modal for creating a document relationship
 */
export function DocumentRelationCreateModal({
  open,
  onOpenChange,
  sourceDocumentId,
}: DocumentRelationCreateModalProps) {
  // Fetch documents using TanStack Query
  const { data: documents } = useDocuments()

  // Mutation for creating a relationship
  const createRelationship = useCreateRelationship()

  // Initialize form with react-hook-form and zod validation
  const form = useForm<FormValues>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      targetDocumentId: "",
      relationType: "",
    },
  })

  // Handle form submission
  const onSubmit = (values: FormValues) => {
    createRelationship.mutate(
      {
        sourceDocumentId,
        targetDocumentId: values.targetDocumentId,
        relationType: values.relationType,
      },
      {
        onSuccess: () => {
          onOpenChange(false)
          form.reset()
        },
      },
    )
  }

  // Get relation type options
  const relationTypes = [
    { value: "BASED_ON", label: "Based On" },
    { value: "CANCELS", label: "Cancels" },
    { value: "PARTIAL", label: "Partial" },
  ]

  // Filter out the source document from the target document options
  const targetDocuments = documents?.filter((doc) => doc.id !== sourceDocumentId) || []

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[500px]">
        <DialogHeader>
          <DialogTitle>Create Document Relationship</DialogTitle>
        </DialogHeader>

        <Form {...form}>
          <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4 py-4">
            <FormField
              control={form.control}
              name="targetDocumentId"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Target Document</FormLabel>
                  <Select onValueChange={field.onChange} defaultValue={field.value}>
                    <FormControl>
                      <SelectTrigger>
                        <SelectValue placeholder="Select target document" />
                      </SelectTrigger>
                    </FormControl>
                    <SelectContent>
                      {targetDocuments.map((doc) => (
                        <SelectItem key={doc.id} value={doc.id}>
                          {doc.type} - {doc.number}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                  <FormMessage />
                </FormItem>
              )}
            />

            <FormField
              control={form.control}
              name="relationType"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Relation Type</FormLabel>
                  <Select onValueChange={field.onChange} defaultValue={field.value}>
                    <FormControl>
                      <SelectTrigger>
                        <SelectValue placeholder="Select relation type" />
                      </SelectTrigger>
                    </FormControl>
                    <SelectContent>
                      {relationTypes.map((type) => (
                        <SelectItem key={type.value} value={type.value}>
                          {type.label}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                  <FormMessage />
                </FormItem>
              )}
            />

            <div className="flex justify-end gap-2">
              <Button type="button" variant="outline" onClick={() => onOpenChange(false)}>
                Cancel
              </Button>
              <Button type="submit" disabled={createRelationship.isPending}>
                {createRelationship.isPending ? "Creating..." : "Create Relationship"}
              </Button>
            </div>
          </form>
        </Form>
      </DialogContent>
    </Dialog>
  )
}
