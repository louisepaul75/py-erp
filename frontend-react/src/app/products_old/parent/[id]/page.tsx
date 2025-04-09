import ProductsPageContainer from '@/components/ui/products';
import { Suspense } from 'react';

export default async function Page({ params }: { params: { id: string } }) {
  const id = await Promise.resolve(params.id);
  
  return (
    <Suspense fallback={<div>Loading...</div>}>
      <ProductsPageContainer initialParentId={id} />
    </Suspense>
  );
} 