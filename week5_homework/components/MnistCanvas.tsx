"use client";

import { useRef, useEffect, useState, useCallback } from "react";

// Pre-trained MNIST model (TF.js official examples)
const MODEL_URL =
  "https://storage.googleapis.com/tfjs-examples/mnist-transfer-cnn/model/model.json";

export default function MnistCanvas() {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [drawing, setDrawing] = useState(false);
  const [prediction, setPrediction] = useState<{ digit: number; probs: number[] } | null>(null);
  const [modelStatus, setModelStatus] = useState<"loading" | "ready" | "error">("loading");
  const modelRef = useRef<import("@tensorflow/tfjs").LayersModel | null>(null);

  useEffect(() => {
    let cancelled = false;
    async function loadModel() {
      try {
        const tf = await import("@tensorflow/tfjs");
        const model = await tf.loadLayersModel(MODEL_URL);
        if (!cancelled) {
          modelRef.current = model;
          setModelStatus("ready");
        }
      } catch {
        if (!cancelled) setModelStatus("error");
      }
    }
    loadModel();
    return () => { cancelled = true; };
  }, []);

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

  const getPos = (e: React.MouseEvent | React.TouchEvent, canvas: HTMLCanvasElement) => {
    const rect = canvas.getBoundingClientRect();
    const scaleX = canvas.width / rect.width;
    const scaleY = canvas.height / rect.height;
    if ("touches" in e) {
      return {
        x: (e.touches[0].clientX - rect.left) * scaleX,
        y: (e.touches[0].clientY - rect.top) * scaleY,
      };
    }
    return {
      x: (e.clientX - rect.left) * scaleX,
      y: (e.clientY - rect.top) * scaleY,
    };
  };

  const startDraw = (e: React.MouseEvent | React.TouchEvent) => {
    e.preventDefault();
    const canvas = canvasRef.current!;
    const ctx = canvas.getContext("2d")!;
    const { x, y } = getPos(e, canvas);
    ctx.beginPath();
    ctx.moveTo(x, y);
    setDrawing(true);
  };

  const draw = (e: React.MouseEvent | React.TouchEvent) => {
    e.preventDefault();
    if (!drawing) return;
    const canvas = canvasRef.current!;
    const ctx = canvas.getContext("2d")!;
    const { x, y } = getPos(e, canvas);
    ctx.lineTo(x, y);
    ctx.stroke();
  };

  const stopDraw = () => {
    setDrawing(false);
    predict();
  };

  const predict = useCallback(async () => {
    if (!modelRef.current || modelStatus !== "ready") return;
    const canvas = canvasRef.current!;
    const tf = await import("@tensorflow/tfjs");

    const probsArray = tf.tidy(() => {
      const img = tf.browser.fromPixels(canvas, 1);
      const resized = tf.image.resizeBilinear(img, [28, 28]);
      const normalized = resized.div(255.0).reshape([1, 28, 28, 1]);
      const output = modelRef.current!.predict(normalized) as import("@tensorflow/tfjs").Tensor;
      return Array.from(output.dataSync());
    });

    const digit = probsArray.indexOf(Math.max(...probsArray));
    setPrediction({ digit, probs: probsArray });
  }, [modelStatus]);

  const clear = () => {
    const canvas = canvasRef.current!;
    const ctx = canvas.getContext("2d")!;
    ctx.fillStyle = "#000";
    ctx.fillRect(0, 0, 280, 280);
    setPrediction(null);
  };

  return (
    <div className="flex flex-col sm:flex-row gap-8 items-start">
      <div>
        <canvas
          ref={canvasRef}
          width={280}
          height={280}
          className="rounded-xl border border-gray-700 cursor-crosshair touch-none"
          style={{ width: 280, height: 280 }}
          onMouseDown={startDraw}
          onMouseMove={draw}
          onMouseUp={stopDraw}
          onMouseLeave={stopDraw}
          onTouchStart={startDraw}
          onTouchMove={draw}
          onTouchEnd={stopDraw}
        />
        <button
          onClick={clear}
          className="mt-3 w-full text-sm border border-gray-700 hover:border-gray-500 py-2 rounded-lg transition-colors text-gray-300"
        >
          지우기
        </button>
      </div>

      <div className="flex-1">
        {modelStatus === "loading" && (
          <div className="text-gray-400 text-sm flex items-center gap-2">
            <span className="animate-spin">⏳</span> 모델 로딩 중...
          </div>
        )}
        {modelStatus === "error" && (
          <div className="text-red-400 text-sm">모델 로드 실패. 새로고침 해주세요.</div>
        )}
        {modelStatus === "ready" && prediction === null && (
          <div className="text-gray-500 text-sm">숫자를 그리면 AI가 인식합니다</div>
        )}
        {modelStatus === "ready" && prediction !== null && (
          <div>
            <div className="text-7xl font-bold text-blue-400 mb-1">
              {prediction.digit}
            </div>
            <p className="text-gray-400 text-sm mb-4">
              신뢰도: {(Math.max(...prediction.probs) * 100).toFixed(1)}%
            </p>
            <div className="space-y-1.5">
              {prediction.probs.map((p, i) => (
                <div key={i} className="flex items-center gap-2 text-xs">
                  <span className="w-4 text-gray-400 font-mono">{i}</span>
                  <div className="flex-1 bg-gray-800 rounded-full h-2">
                    <div
                      className={`h-2 rounded-full transition-all duration-300 ${
                        i === prediction.digit ? "bg-blue-500" : "bg-gray-600"
                      }`}
                      style={{ width: `${Math.max(p * 100, 0.5)}%` }}
                    />
                  </div>
                  <span className="w-10 text-right text-gray-500">
                    {(p * 100).toFixed(1)}%
                  </span>
                </div>
              ))}
            </div>
          </div>
        )}
        <div className="mt-4 text-xs text-gray-600 bg-gray-800/50 rounded-lg p-3">
          <p className="font-medium text-gray-400 mb-1">Week5 CNN 아키텍처</p>
          <p>Conv2D(32) → MaxPool → Conv2D(64) → MaxPool → Dense(128) → Dropout(0.5) → Softmax(10)</p>
        </div>
      </div>
    </div>
  );
}
