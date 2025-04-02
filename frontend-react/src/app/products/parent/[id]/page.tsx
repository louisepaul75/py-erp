import ProductsPageContainer from '@/components/ui/products';

export default function Page({ params }: { params: { id: string } }) {
  return <ProductsPageContainer initialParentId={params.id} />;
} 