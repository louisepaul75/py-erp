'use client'

import React, { useState, useEffect } from 'react'
import { File, Home, Settings } from 'lucide-react' // Example icons
import { cn } from "@/lib/utils";
import {
  CommandDialog,
  CommandEmpty,
  CommandGroup,
  CommandInput,
  CommandItem,
  CommandList,
} from "@/components/ui/command"
import { DialogTitle, DialogDescription } from "@/components/ui/dialog";

export function CommandMenu() {
  const [open, setOpen] = useState(false)

  // Toggle the menu when ⌘K is pressed
  useEffect(() => {
    const down = (e: KeyboardEvent) => {
      if (e.key === 'k' && (e.metaKey || e.ctrlKey)) {
        e.preventDefault()
        setOpen((open) => !open)
      }
    }

    document.addEventListener('keydown', down)
    return () => document.removeEventListener('keydown', down)
  }, [])

  return (
    <CommandDialog open={open} onOpenChange={setOpen}>
      <DialogTitle className="sr-only">Command Menu</DialogTitle>
      <DialogDescription className="sr-only">
        Type a command or search to navigate or perform actions.
      </DialogDescription>
      <CommandInput placeholder="Type a command or search..." />
      <CommandList>
        <CommandEmpty>No results found.</CommandEmpty>
        <CommandGroup heading="General">
          <CommandItem
            onSelect={() => { console.log('Home selected'); setOpen(false); }}
          >
            <Home className="mr-2 h-4 w-4" />
            <span>Home</span>
          </CommandItem>
          <CommandItem
            onSelect={() => { console.log('Settings selected'); setOpen(false); }}
          >
            <Settings className="mr-2 h-4 w-4" />
            <span>Settings</span>
          </CommandItem>
        </CommandGroup>
        <CommandGroup heading="Documents">
           <CommandItem
             onSelect={() => { console.log('New Doc selected'); setOpen(false); }}
           >
             <File className="mr-2 h-4 w-4" />
             <span>New Document</span>
           </CommandItem>
        </CommandGroup>
      </CommandList>
    </CommandDialog>
  )
} 