import React from 'react'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"

export default function TeileTab() {
  return (
    <div className="p-4">
      <h3 className="text-lg font-medium mb-4">Teile</h3>
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>Artikelnummer</TableHead>
            <TableHead>Bezeichnung</TableHead>
            <TableHead>Menge</TableHead>
            <TableHead>Einheit</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          <TableRow>
            <TableCell className="font-medium">310048</TableCell>
            <TableCell>"Adler"-Tender</TableCell>
            <TableCell>1</TableCell>
            <TableCell>Stk</TableCell>
          </TableRow>
          <TableRow>
            <TableCell className="font-medium">411430</TableCell>
            <TableCell>"Adler"-Wagen</TableCell>
            <TableCell>2</TableCell>
            <TableCell>Stk</TableCell>
          </TableRow>
        </TableBody>
      </Table>
    </div>
  )
} 