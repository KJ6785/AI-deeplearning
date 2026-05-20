'use client'

import { useMemo } from 'react'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Card, CardContent } from '@/components/ui/card'
import type { Product } from '@polar-sh/sdk/models/components'

interface ProductDetailProps {
  product: Product
}

export function ProductDetail({ product }: ProductDetailProps) {
  const firstPrice = product.prices[0]

  const priceDisplay = useMemo(() => {
    if (!firstPrice) return '가격 문의'
    switch (firstPrice.amountType) {
      case 'fixed':
        return new Intl.NumberFormat('ko-KR', {
          style: 'currency',
          currency: firstPrice.priceCurrency || 'usd',
        }).format(firstPrice.priceAmount / 100)
      case 'free':
        return '무료'
      default:
        return '자유 금액'
    }
  }, [firstPrice])

  const isSubscription = firstPrice?.type === 'recurring'

  return (
    <div className="container mx-auto px-4 py-16">
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-start">
        <div className="space-y-6">
          <Badge variant={isSubscription ? 'default' : 'secondary'} className="px-3 py-1 text-sm">
            {isSubscription ? '정기 구독' : '일회성 구매'}
          </Badge>
          <h1 className="text-4xl font-bold tracking-tight">{product.name}</h1>
          <p className="text-xl text-muted-foreground whitespace-pre-wrap leading-relaxed">
            {product.description}
          </p>
        </div>

        <Card className="shadow-xl border-2">
          <CardContent className="p-8 space-y-8">
            <div className="flex items-baseline gap-2">
              <span className="text-4xl font-extrabold">{priceDisplay}</span>
              {isSubscription && <span className="text-muted-foreground">/ 월</span>}
            </div>

            <div className="space-y-4">
              <h3 className="font-bold text-lg">포함된 혜택</h3>
              <ul className="space-y-3">
                {product.benefits.map((benefit) => (
                  <li key={benefit.id} className="flex items-start gap-3">
                    <span className="text-green-500 font-bold mt-0.5">✓</span>
                    <span className="text-muted-foreground">{benefit.description}</span>
                  </li>
                ))}
              </ul>
            </div>

            <a href={`/api/checkout?products=${product.id}`}>
              <Button size="lg" className="w-full text-lg h-14 mt-4">
                지금 구매하기
              </Button>
            </a>
            
            <p className="text-center text-xs text-muted-foreground mt-4">
              안전한 Polar.sh 결제 시스템을 통해 처리됩니다.
            </p>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
