import { polar } from '@/lib/polar'
import { ProductGrid } from '@/components/products/product-grid'

export const dynamic = 'force-dynamic'

export default async function ProductsPage() {
  try {
    const { result: products } = await polar.products.list({
      organizationId: process.env.POLAR_ORGANIZATION_ID!,
    })

    return (
      <div className="container mx-auto px-4 py-16">
        <header className="mb-12 text-center">
          <h1 className="text-4xl font-bold mb-4 tracking-tight">상품 목록</h1>
          <p className="text-lg text-muted-foreground">당신에게 필요한 최적의 솔루션을 선택하세요.</p>
        </header>
        <ProductGrid products={products.items} />
      </div>
    )
  } catch (error: any) {
    console.error('❌ Polar API 상세 에러:', {
      status: error?.status,
      message: error?.message,
      details: error?.body || error,
      orgId: process.env.POLAR_ORGANIZATION_ID,
      server: process.env.POLAR_SERVER
    })
    return (
      <div className="container mx-auto px-4 py-16 text-center">
        <h1 className="text-2xl font-bold text-destructive mb-4">상품을 불러올 수 없습니다.</h1>
        <p className="text-muted-foreground">환경 변수(POLAR_ACCESS_TOKEN, POLAR_ORGANIZATION_ID) 설정을 확인해 주세요.</p>
      </div>
    )
  }
}
