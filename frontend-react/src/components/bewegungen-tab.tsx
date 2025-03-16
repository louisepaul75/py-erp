import React from 'react'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"

export default function BewegungenTab() {
  return (
    <div className="p-4">
      <h3 className="text-lg font-medium mb-4">Bewegungen</h3>
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>Datum</TableHead>
            <TableHead>Typ</TableHead>
            <TableHead>Menge</TableHead>
            <TableHead>Von</TableHead>
            <TableHead>Nach</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          <TableRow>
            <TableCell className="font-medium">18.03.2023</TableCell>
            <TableCell>Einlagerung</TableCell>
            <TableCell>10</TableCell>
            <TableCell>Wareneingang</TableCell>
            <TableCell>Hauptlager</TableCell>
          </TableRow>
          <TableRow>
            <TableCell className="font-medium">16.03.2023</TableCell>
            <TableCell>Umlagerung</TableCell>
            <TableCell>5</TableCell>
            <TableCell>Hauptlager</TableCell>
            <TableCell>Außenlager</TableCell>
          </TableRow>
        </TableBody>
      </Table>
    </div>
  )
} 