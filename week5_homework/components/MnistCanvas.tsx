"use client";

import { useRef, useEffect, useState, useCallback } from "react";

const MNIST_IMAGES_SPRITE =
  "https://storage.googleapis.com/tfjs-examples/mnist/data/mnist_images.png";
const MNIST_LABELS_PATH =
  "https://storage.googleapis.com/tfjs-examples/mnist/data/mnist_labels_uint8";
const IMAGE_SIZE = 784;
const NUM_CLASSES = 10;
const NUM_TRAIN = 5000;
const NUM_TEST = 500;

async function loadMnistData() {
  const [imgResponse, labelResponse] = await Promise.all([
    fetch(MNIST_IMAGES_SPRITE),
    fetch(MNIST_LABELS_PATH),
  ]);

  const imgBlob = await imgResponse.blob();
  const labelBuffer = await labelResponse.arrayBuffer();

  const tf = await import("@tensorflow/tfjs");

  const imgBitmap = await createImageBitmap(imgBlob);
  const canvas = document.createElement("canvas");
  canvas.width = imgBitmap.width;
  canvas.height = imgBitmap.height;
  const ctx = canvas.getContext("2d")!;
  ctx.drawImage(imgBitmap, 0, 0);
  const imageData = ctx.getImageData(0, 0, imgBitmap.width, imgBitmap.height);
  const totalImages = Math.floor(imageData.data.length / 4 / IMAGE_SIZE);

  const flat = new Float32Array(totalImages * IMAGE_SIZE);
  for (let i = 0; i < totalImages * IMAGE_SIZE; i++) {
    flat[i] = imageData.data[i * 4] / 255.0;
  }

  const labels = new Uint8Array(labelBuffer);
  const oneHot = new Float32Array(totalImages * NUM_CLASSES);
  for (let i = 0; i < totalImages; i++) {
    oneHot[i * NUM_CLASSES + labels[i]] = 1;
  }

  const xTrain = tf.tensor2d(flat.slice(0, NUM_TRAIN * IMAGE_SIZE), [NUM_TRAIN, IMAGE_SIZE]);
  const yTrain = tf.tensor2d(oneHot.slice(0, NUM_TRAIN * NUM_CLASSES), [NUM_TRAIN, NUM_CLASSES]);

  return { xTrain, yTrain };
}

function buildModel() {
  return import("@tensorflow/tfjs").then((tf) => {
    const model = tf.sequential({
      layers: [
        tf.layers.dense({ inputShape: [IMAGE_SIZE], units: 128, activation: "relu" }),
        tf.layers.dropout({ rate: 0.2 }),
        tf.layers.dense({ units: 64, activation: "relu" }),
        tf.layers.dense({ units: NUM_CLASSES, activation: "softmax" }),
      ],
    });
    model.compile({ optimizer: "adam", loss: "categoricalCrossentropy", metrics: ["accuracy"] });
    return model;
  });
}

export default function MnistCanvas() {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [drawing, setDrawing] = useState(false);
  const [prediction, setPrediction] = useState<{ digit: number; probs: number[] } | null>(null);
  const [status, setStatus] = useState<"idle" | "loading" | "training" | "ready" | "error">("idle");
  const [trainProgress, setTrainProgress] = useState(0);
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
    try {
      setStatus("loading");
      setTrainProgress(0);
      const { xTrain, yTrain } = await loadMnistData();

      setStatus("training");
      const model = await buildModel();
      const EPOCHS = 8;

      await model.fit(xTrain, yTrain, {
        epochs: EPOCHS,
        batchSize: 256,
        shuffle: true,
        callbacks: {
          onEpochEnd: (epoch) => {
            setTrainProgress(Math.round(((epoch + 1) / EPOCHS) * 100));
          },
        },
      });

      xTrain.dispose();
      yTrain.dispose();
      modelRef.current = model;
      setStatus("ready");
    } catch (e) {
      console.error(e);
      setStatus("error");
    }
  }

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

  const stopDraw = () => {
    setDrawing(false);
    predict();
  };

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

    const digit = probsArray.indexOf(Math.max(...probsArray));
    setPrediction({ digit, probs: probsArray });
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
          width={280}
          height={280}
          className={`rounded-xl border border-gray-700 touch-none ${status === "ready" ? "cursor-crosshair" : "opacity-40"}`}
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
          disabled={status !== "ready"}
          className="mt-3 w-full text-sm border border-gray-700 hover:border-gray-500 disabled:opacity-30 py-2 rounded-lg transition-colors text-gray-300"
        >
          지우기
        </button>
      </div>

      <div className="flex-1 space-y-4">
        {status === "idle" && (
          <div>
            <p className="text-gray-400 text-sm mb-3">
              먼저 모델을 학습시켜야 합니다 (약 30초).
            </p>
            <button
              onClick={trainModel}
              className="bg-blue-600 hover:bg-blue-500 px-4 py-2 rounded-lg text-sm font-medium transition-colors"
            >
              모델 학습 시작
            </button>
          </div>
        )}

        {status === "loading" && (
          <div className="text-gray-400 text-sm">
            <span className="animate-pulse">📥</span> MNIST 데이터 로딩 중...
          </div>
        )}

        {status === "training" && (
          <div>
            <p className="text-gray-400 text-sm mb-2">
              🧠 브라우저에서 CNN 학습 중... {trainProgress}%
            </p>
            <div className="w-full bg-gray-800 rounded-full h-2">
              <div
                className="bg-blue-500 h-2 rounded-full transition-all duration-500"
                style={{ width: `${trainProgress}%` }}
              />
            </div>
            <p className="text-gray-600 text-xs mt-2">Week5 핵심: 실제 학습이 브라우저에서 진행됩니다</p>
          </div>
        )}

        {status === "error" && (
          <div className="text-red-400 text-sm">
            로드 실패.{" "}
            <button onClick={trainModel} className="underline">다시 시도</button>
          </div>
        )}

        {status === "ready" && prediction === null && (
          <div className="text-gray-500 text-sm">✅ 학습 완료! 숫자를 그리면 AI가 인식합니다</div>
        )}

        {status === "ready" && prediction !== null && (
          <div>
            <div className="text-7xl font-bold text-blue-400 mb-1">{prediction.digit}</div>
            <p className="text-gray-400 text-sm mb-4">
              신뢰도: {(Math.max(...prediction.probs) * 100).toFixed(1)}%
            </p>
            <div className="space-y-1.5">
              {prediction.probs.map((p, i) => (
                <div key={i} className="flex items-center gap-2 text-xs">
                  <span className="w-4 text-gray-400 font-mono">{i}</span>
                  <div className="flex-1 bg-gray-800 rounded-full h-2">
                    <div
                      className={`h-2 rounded-full transition-all duration-300 ${i === prediction.digit ? "bg-blue-500" : "bg-gray-600"}`}
                      style={{ width: `${Math.max(p * 100, 0.5)}%` }}
                    />
                  </div>
                  <span className="w-10 text-right text-gray-500">{(p * 100).toFixed(1)}%</span>
                </div>
              ))}
            </div>
          </div>
        )}

        <div className="text-xs text-gray-600 bg-gray-800/50 rounded-lg p-3">
          <p className="font-medium text-gray-400 mb-1">Week5 아키텍처</p>
          <p>Dense(128, relu) → Dropout(0.2) → Dense(64, relu) → Softmax(10)</p>
        </div>
      </div>
    </div>
  );
}
