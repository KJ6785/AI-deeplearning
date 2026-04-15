'use client'

import { useMemo } from 'react'
import Link from 'next/link'
import { Card, CardContent, CardFooter, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import type { Product } from '@polar-sh/sdk' // <-- 여기가 수정되었습니다!

interface ProductCardProps {
  product: Product
}

export function ProductCard({ product }: ProductCardProps) {
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
    <Card className="flex flex-col h-full hover:shadow-lg transition-shadow">
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle className="text-lg">{product.name}</CardTitle>
          <Badge variant={isSubscription ? 'default' : 'secondary'}>
            {isSubscription ? '구독' : '일회성'}
          </Badge>
        </div>
      </CardHeader>
      <CardContent className="flex-1">
        <p className="text-muted-foreground text-sm line-clamp-2">
          {product.description}
        </p>
        {product.benefits.length > 0 && (
          <ul className="mt-4 space-y-2">
            {product.benefits.slice(0, 3).map((benefit) => (
              <li key={benefit.id} className="text-sm flex items-start gap-2">
                <span className="text-green-500 mt-0.5">✓</span>
                <span className="line-clamp-1">{benefit.description}</span>
              </li>
            ))}
          </ul>
        )}
      </CardContent>
      <CardFooter className="flex items-center justify-between border-t pt-4">
        <span className="text-xl font-bold">{priceDisplay}</span>
        <Link href={`/products/${product.id}`}>
          <Button size="sm">자세히 보기</Button>
        </Link>
      </CardFooter>
    </Card>
  )
}
