import React from 'react'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"

export default function LagerorteTab() {
  return (
    <div className="p-4">
      <h3 className="text-lg font-medium mb-4">Lagerorte</h3>
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>Lagerort</TableHead>
            <TableHead>Bestand</TableHead>
            <TableHead>Einheit</TableHead>
            <TableHead>Status</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          <TableRow>
            <TableCell className="font-medium">Hauptlager</TableCell>
            <TableCell>15</TableCell>
            <TableCell>Stk</TableCell>
            <TableCell>Verfügbar</TableCell>
          </TableRow>
          <TableRow>
            <TableCell className="font-medium">Außenlager</TableCell>
            <TableCell>8</TableCell>
            <TableCell>Stk</TableCell>
            <TableCell>Verfügbar</TableCell>
          </TableRow>
        </TableBody>
      </Table>
    </div>
  )
} 