"use client"

import { useState } from "react"
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { fetchCustomerNotes, addCustomerNote, deleteCustomerNote } from "@/lib/api/customers"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Textarea } from "@/components/ui/textarea"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import { formatDate } from "@/lib/utils"
import { PlusCircle, Trash2, AlertCircle, StickyNote, Edit, Check, X } from "lucide-react"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { NoteType } from "@/lib/definitions"
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from "@/components/ui/alert-dialog"

/**
 * Komponente zur Anzeige und Verwaltung von Kundennotizen im Sidebar-Block
 */
export default function CustomerNotesBlock({
  customerId,
}: {
  customerId: string
}) {
  const [newNote, setNewNote] = useState("")
  const [isAddingNote, setIsAddingNote] = useState(false)
  const [noteType, setNoteType] = useState<NoteType>(NoteType.INTERNAL)
  const [deleteNoteId, setDeleteNoteId] = useState<string | null>(null)
  const [editingNoteId, setEditingNoteId] = useState<string | null>(null)
  const [editingNoteContent, setEditingNoteContent] = useState("")
  const queryClient = useQueryClient()

  // Fetch customer notes using TanStack Query
  const { data: allNotes, isLoading } = useQuery({
    queryKey: ["customerNotes", customerId],
    queryFn: () => fetchCustomerNotes(customerId),
  })

  // Mutation for adding a new note
  const addNoteMutation = useMutation({
    mutationFn: ({ content, type }: { content: string; type: NoteType }) => addCustomerNote(customerId, content, type),
    onMutate: async ({ content, type }) => {
      // Optimistische Aktualisierung
      // 1. Abfrage-Cache für die aktuelle Notizliste abrufen
      const previousNotes = queryClient.getQueryData<any[]>(["customerNotes", customerId]) || []

      // 2. Optimistisch eine temporäre ID erstellen (wird später durch die echte ersetzt)
      const tempId = `temp-${Date.now()}`

      // 3. Optimistisch die neue Notiz zum Cache hinzufügen
      const newNote: any = {
        id: tempId,
        content,
        timestamp: new Date().toISOString(),
        noteType: type,
        user: {
          id: "user-1",
          name: "John Doe",
          avatar: "/placeholder.svg?height=32&width=32",
        },
      }

      // 4. Cache aktualisieren
      queryClient.setQueryData(["customerNotes", customerId], [...previousNotes, newNote])

      // 5. Formular zurücksetzen
      setNewNote("")
      setIsAddingNote(false)

      // 6. Kontext für onError zurückgeben
      return { previousNotes }
    },
    onError: (err, variables, context) => {
      // Bei Fehler den vorherigen Zustand wiederherstellen
      if (context?.previousNotes) {
        queryClient.setQueryData(["customerNotes", customerId], context.previousNotes)
      }
    },
    onSuccess: (newNote) => {
      // Erfolgreiche Mutation - wir ersetzen die temporäre ID mit der echten
      const currentNotes = queryClient.getQueryData<any[]>(["customerNotes", customerId]) || []

      // Wir filtern die temporäre Notiz heraus und fügen die echte hinzu
      const updatedNotes = currentNotes.filter((note) => !note.id.startsWith("temp-")).concat(newNote)

      queryClient.setQueryData(["customerNotes", customerId], updatedNotes)
    },
  })

  // Mutation for deleting a note
  const deleteNoteMutation = useMutation({
    mutationFn: (noteId: string) => deleteCustomerNote(noteId),
    onSuccess: (_, noteId) => {
      // Aktualisiere den Cache direkt, indem die gelöschte Notiz entfernt wird
      const currentNotes = queryClient.getQueryData<any[]>(["customerNotes", customerId]) || []
      queryClient.setQueryData(
        ["customerNotes", customerId],
        currentNotes.filter((note) => note.id !== noteId),
      )

      setDeleteNoteId(null)
    },
  })

  // Mutation for editing a note (in a real app, this would be a separate API call)
  const editNoteMutation = useMutation({
    mutationFn: ({ noteId, content }: { noteId: string; content: string }) => {
      // Simulate API call
      return new Promise<void>((resolve) => {
        setTimeout(() => {
          resolve()
        }, 500)
      })
    },
    onSuccess: (_, { noteId, content }) => {
      // Aktualisiere den Cache direkt mit der bearbeiteten Notiz
      const currentNotes = queryClient.getQueryData<any[]>(["customerNotes", customerId]) || []
      queryClient.setQueryData(
        ["customerNotes", customerId],
        currentNotes.map((note) => (note.id === noteId ? { ...note, content } : note)),
      )

      setEditingNoteId(null)
      setEditingNoteContent("")
    },
  })

  const handleAddNote = () => {
    if (newNote.trim()) {
      addNoteMutation.mutate({ content: newNote, type: noteType })
    }
  }

  const handleDeleteNote = (noteId: string) => {
    setDeleteNoteId(noteId)
  }

  const confirmDeleteNote = () => {
    if (deleteNoteId) {
      deleteNoteMutation.mutate(deleteNoteId)
    }
  }

  const handleEditNote = (noteId: string, content: string) => {
    setEditingNoteId(noteId)
    setEditingNoteContent(content)
  }

  const saveEditedNote = () => {
    if (editingNoteId && editingNoteContent.trim()) {
      editNoteMutation.mutate({ noteId: editingNoteId, content: editingNoteContent })
    }
  }

  const cancelEditNote = () => {
    setEditingNoteId(null)
    setEditingNoteContent("")
  }

  // Filtern der Notizen nach Typ
  const shippingTypeNotes = allNotes?.filter((note) => note.noteType === NoteType.SHIPPING) || []
  const internalNotes = allNotes?.filter((note) => note.noteType === NoteType.INTERNAL) || []
  const printableNotes = allNotes?.filter((note) => note.noteType === NoteType.PRINTABLE) || []

  return (
    <>
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <StickyNote className="h-5 w-5" />
            Notizen
          </CardTitle>
        </CardHeader>
        <CardContent>
          <Tabs defaultValue="shipping" className="space-y-4">
            <TabsList className="grid w-full grid-cols-3">
              <TabsTrigger value="shipping" className="text-xs sm:text-sm">
                Versand
              </TabsTrigger>
              <TabsTrigger value="internal" className="text-xs sm:text-sm">
                Intern
              </TabsTrigger>
              <TabsTrigger value="printable" className="text-xs sm:text-sm">
                Druckbar
              </TabsTrigger>
            </TabsList>

            {/* Versand & Verpackung Tab */}
            <TabsContent value="shipping" className="space-y-4">
              {isAddingNote && noteType === NoteType.SHIPPING ? (
                <div className="space-y-2">
                  <Textarea
                    placeholder="Versandnotiz eingeben..."
                    value={newNote}
                    onChange={(e) => setNewNote(e.target.value)}
                    rows={3}
                  />
                  <div className="flex justify-end gap-2">
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => {
                        setIsAddingNote(false)
                        setNewNote("")
                      }}
                    >
                      <X className="mr-2 h-4 w-4" />
                      Abbrechen
                    </Button>
                    <Button size="sm" onClick={handleAddNote} disabled={!newNote.trim() || addNoteMutation.isPending}>
                      <Check className="mr-2 h-4 w-4" />
                      {addNoteMutation.isPending ? "Wird hinzugefügt..." : "Hinzufügen"}
                    </Button>
                  </div>
                </div>
              ) : (
                <Button
                  variant="outline"
                  className="w-full"
                  onClick={() => {
                    setIsAddingNote(true)
                    setNoteType(NoteType.SHIPPING)
                  }}
                >
                  <PlusCircle className="mr-2 h-4 w-4" />
                  Versandnotiz hinzufügen
                </Button>
              )}

              <div className="space-y-3 mt-4">
                {isLoading ? (
                  <div className="text-center py-4">Notizen werden geladen...</div>
                ) : shippingTypeNotes.length === 0 ? (
                  <div className="text-center py-4 text-muted-foreground">Keine Versandnotizen vorhanden.</div>
                ) : (
                  shippingTypeNotes.map((note) => (
                    <div key={note.id} className="rounded-lg border p-3 space-y-2">
                      {editingNoteId === note.id ? (
                        <div className="space-y-2">
                          <Textarea
                            value={editingNoteContent}
                            onChange={(e) => setEditingNoteContent(e.target.value)}
                            rows={3}
                          />
                          <div className="flex justify-end gap-2">
                            <Button variant="outline" size="sm" onClick={cancelEditNote}>
                              <X className="mr-2 h-4 w-4" />
                              Abbrechen
                            </Button>
                            <Button
                              size="sm"
                              onClick={saveEditedNote}
                              disabled={!editingNoteContent.trim() || editNoteMutation.isPending}
                            >
                              <Check className="mr-2 h-4 w-4" />
                              {editNoteMutation.isPending ? "Wird gespeichert..." : "Speichern"}
                            </Button>
                          </div>
                        </div>
                      ) : (
                        <>
                          <div className="flex items-center justify-between">
                            <div className="flex items-center gap-2">
                              <Avatar className="h-6 w-6">
                                <AvatarImage src={note.user.avatar || "/placeholder.svg"} />
                                <AvatarFallback>
                                  {note.user.name
                                    .split(" ")
                                    .map((n) => n[0])
                                    .join("")}
                                </AvatarFallback>
                              </Avatar>
                              <span className="text-xs font-medium">{note.user.name}</span>
                            </div>
                            <div className="flex items-center gap-1">
                              <span className="text-xs text-muted-foreground">{formatDate(note.timestamp)}</span>
                              <div className="flex">
                                <Button
                                  variant="ghost"
                                  size="icon"
                                  className="h-6 w-6"
                                  onClick={() => handleEditNote(note.id, note.content)}
                                >
                                  <Edit className="h-3 w-3" />
                                </Button>
                                <Button
                                  variant="ghost"
                                  size="icon"
                                  className="h-6 w-6 text-destructive"
                                  onClick={() => handleDeleteNote(note.id)}
                                >
                                  <Trash2 className="h-3 w-3" />
                                </Button>
                              </div>
                            </div>
                          </div>
                          <p className="text-sm">{note.content}</p>
                        </>
                      )}
                    </div>
                  ))
                )}
              </div>
            </TabsContent>

            {/* Interne Notizen Tab */}
            <TabsContent value="internal" className="space-y-4">
              {isAddingNote && noteType === NoteType.INTERNAL ? (
                <div className="space-y-2">
                  <Textarea
                    placeholder="Interne Notiz eingeben..."
                    value={newNote}
                    onChange={(e) => setNewNote(e.target.value)}
                    rows={3}
                  />
                  <div className="flex justify-end gap-2">
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => {
                        setIsAddingNote(false)
                        setNewNote("")
                      }}
                    >
                      <X className="mr-2 h-4 w-4" />
                      Abbrechen
                    </Button>
                    <Button size="sm" onClick={handleAddNote} disabled={!newNote.trim() || addNoteMutation.isPending}>
                      <Check className="mr-2 h-4 w-4" />
                      {addNoteMutation.isPending ? "Wird hinzugefügt..." : "Hinzufügen"}
                    </Button>
                  </div>
                </div>
              ) : (
                <Button
                  variant="outline"
                  className="w-full"
                  onClick={() => {
                    setIsAddingNote(true)
                    setNoteType(NoteType.INTERNAL)
                  }}
                >
                  <PlusCircle className="mr-2 h-4 w-4" />
                  Interne Notiz hinzufügen
                </Button>
              )}

              <div className="space-y-3">
                {isLoading ? (
                  <div className="text-center py-4">Notizen werden geladen...</div>
                ) : internalNotes.length === 0 ? (
                  <div className="text-center py-4 text-muted-foreground">Keine internen Notizen vorhanden.</div>
                ) : (
                  internalNotes.map((note) => (
                    <div key={note.id} className="rounded-lg border p-3 space-y-2">
                      {editingNoteId === note.id ? (
                        <div className="space-y-2">
                          <Textarea
                            value={editingNoteContent}
                            onChange={(e) => setEditingNoteContent(e.target.value)}
                            rows={3}
                          />
                          <div className="flex justify-end gap-2">
                            <Button variant="outline" size="sm" onClick={cancelEditNote}>
                              <X className="mr-2 h-4 w-4" />
                              Abbrechen
                            </Button>
                            <Button
                              size="sm"
                              onClick={saveEditedNote}
                              disabled={!editingNoteContent.trim() || editNoteMutation.isPending}
                            >
                              <Check className="mr-2 h-4 w-4" />
                              {editNoteMutation.isPending ? "Wird gespeichert..." : "Speichern"}
                            </Button>
                          </div>
                        </div>
                      ) : (
                        <>
                          <div className="flex items-center justify-between">
                            <div className="flex items-center gap-2">
                              <Avatar className="h-6 w-6">
                                <AvatarImage src={note.user.avatar || "/placeholder.svg"} />
                                <AvatarFallback>
                                  {note.user.name
                                    .split(" ")
                                    .map((n) => n[0])
                                    .join("")}
                                </AvatarFallback>
                              </Avatar>
                              <span className="text-xs font-medium">{note.user.name}</span>
                            </div>
                            <div className="flex items-center gap-1">
                              <span className="text-xs text-muted-foreground">{formatDate(note.timestamp)}</span>
                              <div className="flex">
                                <Button
                                  variant="ghost"
                                  size="icon"
                                  className="h-6 w-6"
                                  onClick={() => handleEditNote(note.id, note.content)}
                                >
                                  <Edit className="h-3 w-3" />
                                </Button>
                                <Button
                                  variant="ghost"
                                  size="icon"
                                  className="h-6 w-6 text-destructive"
                                  onClick={() => handleDeleteNote(note.id)}
                                >
                                  <Trash2 className="h-3 w-3" />
                                </Button>
                              </div>
                            </div>
                          </div>
                          <p className="text-sm">{note.content}</p>
                        </>
                      )}
                    </div>
                  ))
                )}
              </div>
            </TabsContent>

            {/* Druckbare Notizen Tab */}
            <TabsContent value="printable" className="space-y-4">
              {isAddingNote && noteType === NoteType.PRINTABLE ? (
                <div className="space-y-2">
                  <Textarea
                    placeholder="Druckbare Notiz eingeben..."
                    value={newNote}
                    onChange={(e) => setNewNote(e.target.value)}
                    rows={3}
                  />
                  <div className="flex justify-end gap-2">
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => {
                        setIsAddingNote(false)
                        setNewNote("")
                      }}
                    >
                      <X className="mr-2 h-4 w-4" />
                      Abbrechen
                    </Button>
                    <Button size="sm" onClick={handleAddNote} disabled={!newNote.trim() || addNoteMutation.isPending}>
                      <Check className="mr-2 h-4 w-4" />
                      {addNoteMutation.isPending ? "Wird hinzugefügt..." : "Hinzufügen"}
                    </Button>
                  </div>
                </div>
              ) : (
                <Button
                  variant="outline"
                  className="w-full"
                  onClick={() => {
                    setIsAddingNote(true)
                    setNoteType(NoteType.PRINTABLE)
                  }}
                >
                  <PlusCircle className="mr-2 h-4 w-4" />
                  Druckbare Notiz hinzufügen
                </Button>
              )}

              <div className="space-y-3">
                {isLoading ? (
                  <div className="text-center py-4">Notizen werden geladen...</div>
                ) : printableNotes.length === 0 ? (
                  <div className="text-center py-4 text-muted-foreground">Keine druckbaren Notizen vorhanden.</div>
                ) : (
                  printableNotes.map((note) => (
                    <div key={note.id} className="rounded-lg border p-3 space-y-2">
                      {editingNoteId === note.id ? (
                        <div className="space-y-2">
                          <Textarea
                            value={editingNoteContent}
                            onChange={(e) => setEditingNoteContent(e.target.value)}
                            rows={3}
                          />
                          <div className="flex justify-end gap-2">
                            <Button variant="outline" size="sm" onClick={cancelEditNote}>
                              <X className="mr-2 h-4 w-4" />
                              Abbrechen
                            </Button>
                            <Button
                              size="sm"
                              onClick={saveEditedNote}
                              disabled={!editingNoteContent.trim() || editNoteMutation.isPending}
                            >
                              <Check className="mr-2 h-4 w-4" />
                              {editNoteMutation.isPending ? "Wird gespeichert..." : "Speichern"}
                            </Button>
                          </div>
                        </div>
                      ) : (
                        <>
                          <div className="flex items-center justify-between">
                            <div className="flex items-center gap-2">
                              <Avatar className="h-6 w-6">
                                <AvatarImage src={note.user.avatar || "/placeholder.svg"} />
                                <AvatarFallback>
                                  {note.user.name
                                    .split(" ")
                                    .map((n) => n[0])
                                    .join("")}
                                </AvatarFallback>
                              </Avatar>
                              <span className="text-xs font-medium">{note.user.name}</span>
                            </div>
                            <div className="flex items-center gap-1">
                              <span className="text-xs text-muted-foreground">{formatDate(note.timestamp)}</span>
                              <div className="flex">
                                <Button
                                  variant="ghost"
                                  size="icon"
                                  className="h-6 w-6"
                                  onClick={() => handleEditNote(note.id, note.content)}
                                >
                                  <Edit className="h-3 w-3" />
                                </Button>
                                <Button
                                  variant="ghost"
                                  size="icon"
                                  className="h-6 w-6 text-destructive"
                                  onClick={() => handleDeleteNote(note.id)}
                                >
                                  <Trash2 className="h-3 w-3" />
                                </Button>
                              </div>
                            </div>
                          </div>
                          <p className="text-sm">{note.content}</p>
                        </>
                      )}
                    </div>
                  ))
                )}
              </div>
            </TabsContent>
          </Tabs>
        </CardContent>
      </Card>

      {/* Delete confirmation dialog */}
      <AlertDialog open={!!deleteNoteId} onOpenChange={(open) => !open && setDeleteNoteId(null)}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle className="flex items-center gap-2">
              <AlertCircle className="h-5 w-5 text-destructive" />
              Notiz löschen
            </AlertDialogTitle>
            <AlertDialogDescription>
              Sind Sie sicher, dass Sie diese Notiz löschen möchten? Diese Aktion kann nicht rückgängig gemacht werden.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Abbrechen</AlertDialogCancel>
            <AlertDialogAction
              onClick={confirmDeleteNote}
              disabled={deleteNoteMutation.isPending}
              className="bg-destructive text-destructive-foreground hover:bg-destructive/90"
            >
              {deleteNoteMutation.isPending ? "Wird gelöscht..." : "Löschen"}
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </>
  )
}
