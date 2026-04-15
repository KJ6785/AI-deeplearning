import { polar } from '@/lib/polar'
import { ProductDetail } from '@/components/products/product-detail'
import { notFound } from 'next/navigation'

interface Props {
  params: Promise<{ id: string }>
}

export default async function ProductDetailPage({ params }: Props) {
  const { id } = await params

  try {
    const product = await polar.products.get({ id })
    return <ProductDetail product={product} />
  } catch (error) {
    console.error('Polar Get Product Error:', error)
    notFound()
  }
}
