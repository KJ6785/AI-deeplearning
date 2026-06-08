import { auth } from "@/lib/auth";
import { redirect } from "next/navigation";
import Link from "next/link";
import MnistCanvas from "@/components/MnistCanvas";
import RegularizationChart from "@/components/RegularizationChart";
import CheckoutButton from "@/components/CheckoutButton";
import { prisma } from "@/lib/db";

export default async function DashboardPage({
  searchParams,
}: {
  searchParams: Promise<{ success?: string; canceled?: string }>;
}) {
  const session = await auth();
  if (!session?.user?.email) redirect("/login");

  const params = await searchParams;

  const user = await prisma.user.findUnique({
    where: { email: session.user.email },
  });
  const isPremium = user?.isPremium ?? false;

  return (
    <main className="min-h-screen bg-gray-950">
      <nav className="border-b border-gray-800 px-6 py-4 flex items-center justify-between">
        <Link href="/" className="font-bold text-xl text-blue-400">
          Week5 ML Lab
        </Link>
        <div className="flex items-center gap-4">
          <span className="text-sm text-gray-400">
            {session.user.email}
          </span>
          {isPremium && (
            <span className="bg-yellow-500/20 text-yellow-400 text-xs px-2 py-1 rounded border border-yellow-700">
              ⭐ Premium
            </span>
          )}
          <Link
            href="/api/auth/signout"
            className="text-sm bg-gray-800 px-3 py-1.5 rounded hover:bg-gray-700"
          >
            로그아웃
          </Link>
        </div>
      </nav>

      <div className="max-w-4xl mx-auto px-6 py-8">
        {params.success && (
          <div className="mb-6 bg-green-900/30 border border-green-700 text-green-300 rounded-lg px-4 py-3 text-sm">
            결제 완료! 프리미엄 기능이 활성화되었습니다.
          </div>
        )}
        {params.canceled && (
          <div className="mb-6 bg-yellow-900/30 border border-yellow-700 text-yellow-300 rounded-lg px-4 py-3 text-sm">
            결제가 취소되었습니다.
          </div>
        )}

        <h1 className="text-2xl font-bold mb-8">대시보드</h1>

        {/* Free: MNIST */}
        <section className="mb-8">
          <div className="bg-gray-900 rounded-2xl border border-gray-800 p-8">
            <div className="flex items-center gap-2 mb-2">
              <span className="bg-green-500/20 text-green-400 text-xs px-2 py-0.5 rounded">무료</span>
              <h2 className="text-lg font-semibold">MNIST 손글씨 인식</h2>
            </div>
            <p className="text-gray-400 text-sm mb-6">
              캔버스에 0~9 숫자를 그리세요. CNN이 실시간으로 인식합니다.
            </p>
            <MnistCanvas />
          </div>
        </section>

        {/* Premium: Regularization */}
        <section className="mb-8">
          <div className="bg-gray-900 rounded-2xl border border-gray-800 p-8 relative overflow-hidden">
            {!isPremium && (
              <div className="absolute inset-0 backdrop-blur-sm bg-gray-950/70 flex flex-col items-center justify-center z-10 rounded-2xl">
                <span className="text-4xl mb-3">🔒</span>
                <p className="font-semibold text-lg mb-1">프리미엄 전용</p>
                <p className="text-gray-400 text-sm mb-4">₩9,900 (테스트 결제)</p>
                <CheckoutButton />
                <p className="text-gray-600 text-xs mt-3">
                  테스트 카드: 4242 4242 4242 4242 · CVC: 임의 · 날짜: 미래
                </p>
              </div>
            )}
            <div className="flex items-center gap-2 mb-2">
              <span className="bg-yellow-500/20 text-yellow-400 text-xs px-2 py-0.5 rounded">프리미엄</span>
              <h2 className="text-lg font-semibold">정규화 & 과적합 시각화</h2>
            </div>
            <p className="text-gray-400 text-sm mb-6">
              L1/L2 Regularization, Dropout 효과를 인터랙티브 차트로 비교합니다.
            </p>
            <RegularizationChart isPremium={isPremium} />
          </div>
        </section>
      </div>
    </main>
  );
}
