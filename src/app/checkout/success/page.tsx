import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import Link from 'next/link'
import { CheckCircle } from 'lucide-react'

export default function CheckoutSuccessPage() {
  return (
    <div className="container mx-auto px-4 py-32 flex justify-center">
      <Card className="max-w-md w-full text-center border-2 border-green-500 shadow-xl">
        <CardHeader>
          <div className="flex justify-center mb-6">
            <CheckCircle className="h-20 w-20 text-green-500" />
          </div>
          <CardTitle className="text-3xl font-extrabold">결제 성공!</CardTitle>
        </CardHeader>
        <CardContent className="space-y-6">
          <p className="text-muted-foreground text-lg">
            구매해 주셔서 대단히 감사합니다. <br />
            입력하신 이메일로 상품 정보를 보내드렸습니다.
          </p>
          <div className="flex flex-col gap-3">
            <Link href="/products">
              <Button size="lg" className="w-full">다른 상품 더 보기</Button>
            </Link>
            <p className="text-xs text-muted-foreground">
              구독 정보나 주문 내역은 이메일의 매직 링크를 통해 <br />
              Polar Customer Portal에서 확인하실 수 있습니다.
            </p>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
