import React from 'react'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"

export default function UmsatzeTab() {
  return (
    <div className="p-4">
      <h3 className="text-lg font-medium mb-4">Umsätze</h3>
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>Datum</TableHead>
            <TableHead>Beleg</TableHead>
            <TableHead>Menge</TableHead>
            <TableHead>Betrag</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          <TableRow>
            <TableCell className="font-medium">15.03.2023</TableCell>
            <TableCell>RE-2023-0125</TableCell>
            <TableCell>2</TableCell>
            <TableCell>€ 49,90</TableCell>
          </TableRow>
          <TableRow>
            <TableCell className="font-medium">02.02.2023</TableCell>
            <TableCell>RE-2023-0089</TableCell>
            <TableCell>1</TableCell>
            <TableCell>€ 24,95</TableCell>
          </TableRow>
        </TableBody>
      </Table>
    </div>
  )
} 