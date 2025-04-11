import type { Metadata } from "next";
import React from "react";

// Export metadata from the layout file (Server Component)
export const metadata: Metadata = {
  title: "Supplier Management",
  description: "Manage business suppliers.",
};

// Basic layout component that renders its children
export default function SuppliersLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return <>{children}</>; // Render the page content directly
} 