"use client";

import { useRef, useEffect, useState, useCallback } from "react";

const SPRITE_URL = "/api/mnist/images";
const LABELS_URL = "/api/mnist/labels";
const IMAGE_SIZE = 784;
const NUM_CLASSES = 10;
const NUM_TRAIN = 5500;

async function loadMnistData(tf: typeof import("@tensorflow/tfjs")) {
  // Load sprite image via Image element (handles CORS correctly)
  const imageData = await new Promise<ImageData>((resolve, reject) => {
    const img = new Image();
    img.crossOrigin = "anonymous";
    img.onload = () => {
      const canvas = document.createElement("canvas");
      canvas.width = img.width;
      canvas.height = img.height;
      const ctx = canvas.getContext("2d")!;
      ctx.drawImage(img, 0, 0);
      resolve(ctx.getImageData(0, 0, img.width, img.height));
    };
    img.onerror = () => reject(new Error("Failed to load MNIST images"));
    img.src = SPRITE_URL;
  });

  // Load labels
  const labelBuf = await fetch(LABELS_URL).then((r) => r.arrayBuffer());
  const labels = new Uint8Array(labelBuf);
  const totalImages = Math.floor(imageData.data.length / 4 / IMAGE_SIZE);
  const n = Math.min(NUM_TRAIN, totalImages);

  // Extract pixel values (R channel of RGBA, each row = one 28x28 image)
  const pixels = new Float32Array(n * IMAGE_SIZE);
  for (let i = 0; i < n * IMAGE_SIZE; i++) {
    pixels[i] = imageData.data[i * 4] / 255.0;
  }

  // One-hot labels
  const oneHot = new Float32Array(n * NUM_CLASSES);
  for (let i = 0; i < n; i++) {
    oneHot[i * NUM_CLASSES + labels[i]] = 1;
  }

  return {
    xTrain: tf.tensor2d(pixels, [n, IMAGE_SIZE]),
    yTrain: tf.tensor2d(oneHot, [n, NUM_CLASSES]),
  };
}

export default function MnistCanvas() {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [drawing, setDrawing] = useState(false);
  const [prediction, setPrediction] = useState<{ digit: number; probs: number[] } | null>(null);
  const [status, setStatus] = useState<"idle" | "loading" | "training" | "ready" | "error">("idle");
  const [trainProgress, setTrainProgress] = useState(0);
  const [errorMsg, setErrorMsg] = useState("");
  const modelRef = useRef<import("@tensorflow/tfjs").Sequential | null>(null);

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

  async function trainModel() {
    setStatus("loading");
    setTrainProgress(0);
    setErrorMsg("");
    try {
      const tf = await import("@tensorflow/tfjs");
      const { xTrain, yTrain } = await loadMnistData(tf);

      setStatus("training");

      const model = tf.sequential({
        layers: [
          tf.layers.dense({ inputShape: [IMAGE_SIZE], units: 128, activation: "relu" }),
          tf.layers.dropout({ rate: 0.2 }),
          tf.layers.dense({ units: 64, activation: "relu" }),
          tf.layers.dense({ units: NUM_CLASSES, activation: "softmax" }),
        ],
      });
      model.compile({ optimizer: "adam", loss: "categoricalCrossentropy", metrics: ["accuracy"] });

      const EPOCHS = 10;
      await model.fit(xTrain, yTrain, {
        epochs: EPOCHS,
        batchSize: 256,
        shuffle: true,
        callbacks: {
          onEpochEnd: (epoch) => setTrainProgress(Math.round(((epoch + 1) / EPOCHS) * 100)),
        },
      });

      xTrain.dispose();
      yTrain.dispose();
      modelRef.current = model;
      setStatus("ready");
    } catch (e) {
      console.error(e);
      setErrorMsg(e instanceof Error ? e.message : "알 수 없는 오류");
      setStatus("error");
    }
  }

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
    ctx.fillStyle = "#000";
    ctx.fillRect(0, 0, 280, 280);
    setPrediction(null);
  };

  return (
    <div className="flex flex-col sm:flex-row gap-8 items-start">
      <div>
        <canvas
          ref={canvasRef}
          width={280} height={280}
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
        {status === "idle" && (
          <div>
            <p className="text-gray-400 text-sm mb-3">모델 학습 후 사용 가능 (약 30~60초)</p>
            <button onClick={trainModel}
              className="bg-blue-600 hover:bg-blue-500 px-4 py-2 rounded-lg text-sm font-medium">
              모델 학습 시작
            </button>
          </div>
        )}
        {status === "loading" && <p className="text-gray-400 text-sm animate-pulse">📥 MNIST 데이터 로딩 중...</p>}
        {status === "training" && (
          <div>
            <p className="text-gray-400 text-sm mb-2">🧠 학습 중... {trainProgress}%</p>
            <div className="w-full bg-gray-800 rounded-full h-2">
              <div className="bg-blue-500 h-2 rounded-full transition-all" style={{ width: `${trainProgress}%` }} />
            </div>
          </div>
        )}
        {status === "error" && (
          <div className="text-red-400 text-sm">
            <p>오류: {errorMsg}</p>
            <button onClick={trainModel} className="mt-2 underline text-red-300">다시 시도</button>
          </div>
        )}
        {status === "ready" && !prediction && <p className="text-gray-500 text-sm">✅ 학습 완료! 숫자를 그리세요</p>}
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
          <p className="font-medium text-gray-400 mb-1">Week5 아키텍처</p>
          <p>Dense(128,relu) → Dropout(0.2) → Dense(64,relu) → Softmax(10)</p>
        </div>
      </div>
    </div>
  );
}
