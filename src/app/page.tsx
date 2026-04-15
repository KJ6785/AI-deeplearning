import { Button } from "@/components/ui/button";
import Link from "next/link";

export default function Home() {
  return (
    <div className="container mx-auto px-4 py-24">
      <section className="flex flex-col items-center text-center space-y-8">
        <h1 className="text-5xl font-extrabold tracking-tight sm:text-6xl">
          가장 쉬운 디지털 상점 구축, <span className="text-primary">ShopEasy</span>
        </h1>
        <p className="text-xl text-muted-foreground max-w-[42rem] leading-normal">
          Polar.sh와 Supabase를 활용하여 며칠이 아닌 몇 시간 만에 유료 구독과 디지털 상품 판매 시스템을 구축하세요.
        </p>
        <div className="flex gap-4">
          <Link href="/products">
            <Button size="lg" className="px-8">
              상품 둘러보기
            </Button>
          </Link>
          <Link href="/auth/register">
            <Button size="lg" variant="outline" className="px-8">
              무료로 시작하기
            </Button>
          </Link>
        </div>
      </section>
    </div>
  );
}
