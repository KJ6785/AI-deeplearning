"use client";

import { useRef, useEffect, useState, useCallback } from "react";

const IMAGE_SIZE = 784;

export default function MnistCanvas() {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [drawing, setDrawing] = useState(false);
  const [prediction, setPrediction] = useState<{ digit: number; probs: number[] } | null>(null);
  const [status, setStatus] = useState<"loading" | "ready" | "error">("loading");
  const modelRef = useRef<import("@tensorflow/tfjs").LayersModel | null>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext("2d")!;
    ctx.fillStyle = "#000";
    ctx.fillRect(0, 0, 280, 280);
    ctx.strokeStyle = "#fff";
    ctx.lineWidth = 22;
    ctx.lineCap = "round";
    ctx.lineJoin = "round";
  }, []);

  useEffect(() => {
    let cancelled = false;
    async function load() {
      try {
        const tf = await import("@tensorflow/tfjs");
        const model = await tf.loadLayersModel("/mnist_model/model.json");
        if (!cancelled) { modelRef.current = model; setStatus("ready"); }
      } catch (e) {
        console.error(e);
        if (!cancelled) setStatus("error");
      }
    }
    load();
    return () => { cancelled = true; };
  }, []);

  const getPos = (e: React.MouseEvent | React.TouchEvent, canvas: HTMLCanvasElement) => {
    const rect = canvas.getBoundingClientRect();
    const scaleX = canvas.width / rect.width;
    const scaleY = canvas.height / rect.height;
    if ("touches" in e) {
      return { x: (e.touches[0].clientX - rect.left) * scaleX, y: (e.touches[0].clientY - rect.top) * scaleY };
    }
    return { x: (e.clientX - rect.left) * scaleX, y: (e.clientY - rect.top) * scaleY };
  };

  const startDraw = (e: React.MouseEvent | React.TouchEvent) => {
    e.preventDefault();
    if (status !== "ready") return;
    const canvas = canvasRef.current!;
    const ctx = canvas.getContext("2d")!;
    const { x, y } = getPos(e, canvas);
    ctx.beginPath(); ctx.moveTo(x, y);
    setDrawing(true);
  };

  const draw = (e: React.MouseEvent | React.TouchEvent) => {
    e.preventDefault();
    if (!drawing) return;
    const canvas = canvasRef.current!;
    const ctx = canvas.getContext("2d")!;
    const { x, y } = getPos(e, canvas);
    ctx.lineTo(x, y); ctx.stroke();
  };

  const stopDraw = () => { setDrawing(false); predict(); };

  const predict = useCallback(async () => {
    if (!modelRef.current || status !== "ready") return;
    const canvas = canvasRef.current!;
    const tf = await import("@tensorflow/tfjs");

    const probsArray = tf.tidy(() => {
      const img = tf.browser.fromPixels(canvas, 1);
      const resized = tf.image.resizeBilinear(img, [28, 28]);
      const flat = resized.div(255.0).reshape([1, IMAGE_SIZE]);
      const out = modelRef.current!.predict(flat) as import("@tensorflow/tfjs").Tensor;
      return Array.from(out.dataSync());
    });

    setPrediction({ digit: probsArray.indexOf(Math.max(...probsArray)), probs: probsArray });
  }, [status]);

  const clear = () => {
    const canvas = canvasRef.current!;
    const ctx = canvas.getContext("2d")!;
    ctx.fillStyle = "#000"; ctx.fillRect(0, 0, 280, 280);
    setPrediction(null);
  };

  return (
    <div className="flex flex-col sm:flex-row gap-8 items-start">
      <div>
        <canvas
          ref={canvasRef} width={280} height={280}
          className={`rounded-xl border border-gray-700 touch-none ${status === "ready" ? "cursor-crosshair" : "opacity-50"}`}
          style={{ width: 280, height: 280 }}
          onMouseDown={startDraw} onMouseMove={draw} onMouseUp={stopDraw} onMouseLeave={stopDraw}
          onTouchStart={startDraw} onTouchMove={draw} onTouchEnd={stopDraw}
        />
        <button onClick={clear} disabled={status !== "ready"}
          className="mt-3 w-full text-sm border border-gray-700 hover:border-gray-500 disabled:opacity-30 py-2 rounded-lg text-gray-300">
          지우기
        </button>
      </div>

      <div className="flex-1 space-y-4">
        {status === "loading" && <p className="text-gray-400 text-sm animate-pulse">🧠 모델 로딩 중...</p>}
        {status === "error" && <p className="text-red-400 text-sm">모델 로드 실패. 새로고침 해주세요.</p>}
        {status === "ready" && !prediction && <p className="text-gray-500 text-sm">숫자를 그리면 AI가 인식합니다</p>}
        {status === "ready" && prediction && (
          <div>
            <div className="text-7xl font-bold text-blue-400 mb-1">{prediction.digit}</div>
            <p className="text-gray-400 text-sm mb-3">신뢰도: {(Math.max(...prediction.probs) * 100).toFixed(1)}%</p>
            <div className="space-y-1.5">
              {prediction.probs.map((p, i) => (
                <div key={i} className="flex items-center gap-2 text-xs">
                  <span className="w-4 text-gray-400 font-mono">{i}</span>
                  <div className="flex-1 bg-gray-800 rounded-full h-2">
                    <div className={`h-2 rounded-full transition-all ${i === prediction.digit ? "bg-blue-500" : "bg-gray-600"}`}
                      style={{ width: `${Math.max(p * 100, 0.5)}%` }} />
                  </div>
                  <span className="w-10 text-right text-gray-500">{(p * 100).toFixed(1)}%</span>
                </div>
              ))}
            </div>
          </div>
        )}
        <div className="text-xs text-gray-600 bg-gray-800/50 rounded-lg p-3">
          <p className="font-medium text-gray-400 mb-1">Week5 아키텍처 (90% 정확도)</p>
          <p>Dense(128,relu) → Dropout(0.2) → Dense(64,relu) → Softmax(10)</p>
        </div>
      </div>
    </div>
  );
}
