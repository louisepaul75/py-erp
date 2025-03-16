import React from 'react'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"

export default function GewogenTab() {
  return (
    <div className="p-4">
      <h3 className="text-lg font-medium mb-4">Gewogen</h3>
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>Datum</TableHead>
            <TableHead>Gewicht</TableHead>
            <TableHead>Einheit</TableHead>
            <TableHead>Benutzer</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          <TableRow>
            <TableCell className="font-medium">12.03.2023</TableCell>
            <TableCell>125</TableCell>
            <TableCell>g</TableCell>
            <TableCell>admin</TableCell>
          </TableRow>
          <TableRow>
            <TableCell className="font-medium">05.01.2023</TableCell>
            <TableCell>127</TableCell>
            <TableCell>g</TableCell>
            <TableCell>admin</TableCell>
          </TableRow>
        </TableBody>
      </Table>
    </div>
  )
} 