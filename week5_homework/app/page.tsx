import Link from "next/link";
import { auth } from "@/lib/auth";
import MnistCanvas from "@/components/MnistCanvas";

export default async function Home() {
  const session = await auth();

  return (
    <main className="min-h-screen bg-gray-950">
      {/* Nav */}
      <nav className="border-b border-gray-800 px-6 py-4 flex items-center justify-between">
        <span className="font-bold text-xl text-blue-400">Week5 ML Lab</span>
        <div className="flex gap-4 items-center">
          {session ? (
            <>
              <Link href="/dashboard" className="text-sm text-gray-300 hover:text-white">
                대시보드
              </Link>
              <Link
                href="/api/auth/signout"
                className="text-sm bg-gray-800 px-3 py-1.5 rounded hover:bg-gray-700"
              >
                로그아웃
              </Link>
            </>
          ) : (
            <>
              <Link href="/login" className="text-sm text-gray-300 hover:text-white">
                로그인
              </Link>
              <Link
                href="/signup"
                className="text-sm bg-blue-600 px-3 py-1.5 rounded hover:bg-blue-500"
              >
                회원가입
              </Link>
            </>
          )}
        </div>
      </nav>

      {/* Hero */}
      <section className="max-w-4xl mx-auto px-6 py-16 text-center">
        <div className="inline-block bg-blue-900/30 text-blue-300 text-xs px-3 py-1 rounded-full mb-4 border border-blue-700">
          부산대 전산물리 Week 5 — AI & Deep Learning
        </div>
        <h1 className="text-4xl font-bold mb-4">
          딥러닝을 <span className="text-blue-400">브라우저</span>에서 직접 체험
        </h1>
        <p className="text-gray-400 text-lg mb-8">
          MNIST 손글씨 인식 · 정규화/과적합 시각화 · 전이학습 실험실
        </p>
        <div className="flex gap-3 justify-center">
          <Link
            href="/signup"
            className="bg-blue-600 hover:bg-blue-500 px-6 py-3 rounded-lg font-medium transition-colors"
          >
            무료로 시작하기
          </Link>
          <Link
            href="/dashboard"
            className="border border-gray-700 hover:border-gray-500 px-6 py-3 rounded-lg font-medium transition-colors"
          >
            데모 보기
          </Link>
        </div>
      </section>

      {/* Free MNIST Demo */}
      <section className="max-w-4xl mx-auto px-6 py-8">
        <div className="bg-gray-900 rounded-2xl border border-gray-800 p-8">
          <div className="flex items-center gap-2 mb-2">
            <span className="bg-green-500/20 text-green-400 text-xs px-2 py-0.5 rounded">무료</span>
            <h2 className="text-xl font-semibold">MNIST 손글씨 인식</h2>
          </div>
          <p className="text-gray-400 text-sm mb-6">
            캔버스에 숫자를 그리면 CNN이 실시간으로 인식합니다 (TensorFlow.js)
          </p>
          <MnistCanvas />
        </div>
      </section>

      {/* Premium Preview */}
      <section className="max-w-4xl mx-auto px-6 py-8">
        <div className="bg-gray-900 rounded-2xl border border-gray-800 p-8 relative overflow-hidden">
          <div className="absolute inset-0 backdrop-blur-sm bg-gray-950/60 flex flex-col items-center justify-center z-10 rounded-2xl">
            <span className="text-4xl mb-3">🔒</span>
            <p className="font-semibold text-lg mb-1">프리미엄 전용</p>
            <p className="text-gray-400 text-sm mb-4">₩9,900으로 전체 기능 잠금 해제</p>
            <Link
              href={session ? "/dashboard" : "/signup"}
              className="bg-yellow-500 hover:bg-yellow-400 text-black px-5 py-2 rounded-lg font-semibold text-sm transition-colors"
            >
              {session ? "업그레이드" : "회원가입 후 결제"}
            </Link>
          </div>
          <div className="flex items-center gap-2 mb-2">
            <span className="bg-yellow-500/20 text-yellow-400 text-xs px-2 py-0.5 rounded">프리미엄</span>
            <h2 className="text-xl font-semibold">정규화 & 과적합 시각화</h2>
          </div>
          <p className="text-gray-400 text-sm mb-6">L1/L2 Regularization, Dropout 효과를 인터랙티브하게 비교</p>
          <div className="h-40 bg-gray-800 rounded-lg" />
        </div>
      </section>

      {/* Features */}
      <section className="max-w-4xl mx-auto px-6 py-12 grid grid-cols-3 gap-4">
        {[
          { icon: "🧠", title: "MNIST CNN", desc: "브라우저에서 실시간 숫자 인식", free: true },
          { icon: "📊", title: "정규화 시각화", desc: "L1/L2/Dropout 효과 비교", free: false },
          { icon: "🔬", title: "전이학습 실험실", desc: "사전학습 모델 파인튜닝 데모", free: false },
        ].map((f) => (
          <div key={f.title} className="bg-gray-900 border border-gray-800 rounded-xl p-5">
            <div className="text-2xl mb-2">{f.icon}</div>
            <div className="flex items-center gap-2 mb-1">
              <span className="font-medium text-sm">{f.title}</span>
              <span className={`text-xs px-1.5 py-0.5 rounded ${f.free ? "bg-green-500/20 text-green-400" : "bg-yellow-500/20 text-yellow-400"}`}>
                {f.free ? "무료" : "프리미엄"}
              </span>
            </div>
            <p className="text-gray-500 text-xs">{f.desc}</p>
          </div>
        ))}
      </section>

      <footer className="border-t border-gray-800 text-center py-6 text-gray-600 text-sm">
        부산대학교 물리학과 전산물리 2026 · Week 5 과제
      </footer>
    </main>
  );
}
