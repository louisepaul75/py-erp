import { InventoryManagement } from "@/components/ui/products";

export default function Page({ params }: { params: { id: string } }) {
  return <InventoryManagement initialVariantId={params.id} />;
} 