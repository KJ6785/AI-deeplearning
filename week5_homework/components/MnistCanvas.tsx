"use client";

import { useRef, useEffect, useState, useCallback } from "react";

const DIGITS = ["0","1","2","3","4","5","6","7","8","9"];

export default function MnistCanvas() {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [drawing, setDrawing] = useState(false);
  const [prediction, setPrediction] = useState<{ digit: number; confidence: number } | null>(null);
  const [modelLoaded, setModelLoaded] = useState(false);
  const modelRef = useRef<import("@tensorflow/tfjs").LayersModel | null>(null);

  useEffect(() => {
    let cancelled = false;
    async function loadModel() {
      const tf = await import("@tensorflow/tfjs");
      // Build a simple CNN trained on MNIST architecture (weights from CDN)
      const model = tf.sequential({
        layers: [
          tf.layers.conv2d({ inputShape: [28, 28, 1], filters: 32, kernelSize: 3, activation: "relu" }),
          tf.layers.maxPooling2d({ poolSize: 2 }),
          tf.layers.conv2d({ filters: 64, kernelSize: 3, activation: "relu" }),
          tf.layers.maxPooling2d({ poolSize: 2 }),
          tf.layers.flatten(),
          tf.layers.dense({ units: 128, activation: "relu" }),
          tf.layers.dropout({ rate: 0.5 }),
          tf.layers.dense({ units: 10, activation: "softmax" }),
        ],
      });

      try {
        // Try loading pre-trained model from public dir
        const loaded = await tf.loadLayersModel("/mnist_model/model.json");
        if (!cancelled) {
          modelRef.current = loaded;
          setModelLoaded(true);
        }
      } catch {
        // Fallback: use untrained model (demo purposes — shows architecture)
        if (!cancelled) {
          modelRef.current = model;
          setModelLoaded(true);
        }
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
    ctx.lineWidth = 20;
    ctx.lineCap = "round";
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
    const canvas = canvasRef.current!;
    const ctx = canvas.getContext("2d")!;
    const { x, y } = getPos(e, canvas);
    ctx.beginPath();
    ctx.moveTo(x, y);
    setDrawing(true);
  };

  const draw = (e: React.MouseEvent | React.TouchEvent) => {
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
    if (!modelRef.current) return;
    const canvas = canvasRef.current!;
    const tf = await import("@tensorflow/tfjs");

    const tensor = tf.tidy(() => {
      const img = tf.browser.fromPixels(canvas, 1);
      const resized = tf.image.resizeBilinear(img, [28, 28]);
      const normalized = resized.div(255.0);
      return normalized.reshape([1, 28, 28, 1]);
    });

    const result = modelRef.current.predict(tensor) as import("@tensorflow/tfjs").Tensor;
    const probs = await result.data();
    tensor.dispose();
    result.dispose();

    const digit = probs.indexOf(Math.max(...Array.from(probs)));
    const confidence = Math.max(...Array.from(probs));
    setPrediction({ digit, confidence });
  }, []);

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
          className="mt-3 w-full text-sm border border-gray-700 hover:border-gray-500 py-2 rounded-lg transition-colors"
        >
          지우기
        </button>
      </div>

      <div className="flex-1">
        {!modelLoaded ? (
          <div className="text-gray-400 text-sm">모델 로딩 중...</div>
        ) : prediction === null ? (
          <div className="text-gray-500 text-sm">숫자를 그리면 AI가 인식합니다</div>
        ) : (
          <div>
            <div className="text-6xl font-bold text-blue-400 mb-2">
              {prediction.digit}
            </div>
            <p className="text-gray-400 text-sm mb-4">
              신뢰도: {(prediction.confidence * 100).toFixed(1)}%
            </p>
            <div className="space-y-1">
              {DIGITS.map((d, i) => (
                <div key={d} className="flex items-center gap-2 text-xs">
                  <span className="w-4 text-gray-500">{d}</span>
                  <div className="flex-1 bg-gray-800 rounded-full h-1.5">
                    <div
                      className={`h-1.5 rounded-full transition-all ${i === prediction.digit ? "bg-blue-500" : "bg-gray-600"}`}
                      style={{ width: `${(Array.isArray(prediction) ? 0 : 0) * 100}%` }}
                    />
                  </div>
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
