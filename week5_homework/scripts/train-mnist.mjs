// Train MNIST using tfjs CPU backend (no native bindings needed)
import * as tf from "@tensorflow/tfjs";
import "@tensorflow/tfjs-backend-cpu";
import https from "https";
import { writeFileSync, mkdirSync } from "fs";
import path from "path";
import { fileURLToPath } from "url";
import { PNG } from "pngjs";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const OUTPUT_DIR = path.join(__dirname, "../public/mnist_model");

const SPRITE_URL = "https://storage.googleapis.com/learnjs-data/model-builder/mnist_images.png";
const LABELS_URL = "https://storage.googleapis.com/learnjs-data/model-builder/mnist_labels_uint8";
const IMAGE_SIZE = 784;
const NUM_CLASSES = 10;
const NUM_TRAIN = 6000;

function fetchBuffer(url) {
  return new Promise((resolve, reject) => {
    const chunks = [];
    https.get(url, (res) => {
      if (res.statusCode !== 200) { reject(new Error(`HTTP ${res.statusCode}`)); return; }
      res.on("data", (c) => chunks.push(c));
      res.on("end", () => resolve(Buffer.concat(chunks)));
      res.on("error", reject);
    }).on("error", reject);
  });
}

console.log("📥 데이터 다운로드 중...");
const [imgBuf, labelBuf] = await Promise.all([fetchBuffer(SPRITE_URL), fetchBuffer(LABELS_URL)]);

console.log("🖼️ PNG 파싱 중...");
const png = PNG.sync.read(imgBuf);
const labels = new Uint8Array(labelBuf);
const n = Math.min(NUM_TRAIN, Math.floor(png.data.length / 4 / IMAGE_SIZE));
console.log(`총 ${n}개 이미지 사용`);

const pixels = new Float32Array(n * IMAGE_SIZE);
for (let i = 0; i < n * IMAGE_SIZE; i++) pixels[i] = png.data[i * 4] / 255.0;

const oneHot = new Float32Array(n * NUM_CLASSES);
for (let i = 0; i < n; i++) oneHot[i * NUM_CLASSES + labels[i]] = 1;

await tf.setBackend("cpu");
const xTrain = tf.tensor2d(pixels, [n, IMAGE_SIZE]);
const yTrain = tf.tensor2d(oneHot, [n, NUM_CLASSES]);

console.log("🧠 모델 학습 시작...");
const model = tf.sequential({
  layers: [
    tf.layers.dense({ inputShape: [IMAGE_SIZE], units: 128, activation: "relu" }),
    tf.layers.dropout({ rate: 0.2 }),
    tf.layers.dense({ units: 64, activation: "relu" }),
    tf.layers.dense({ units: NUM_CLASSES, activation: "softmax" }),
  ],
});
model.compile({ optimizer: "adam", loss: "categoricalCrossentropy", metrics: ["accuracy"] });

await model.fit(xTrain, yTrain, {
  epochs: 15,
  batchSize: 256,
  shuffle: true,
  callbacks: {
    onEpochEnd: (e, logs) =>
      console.log(`  Epoch ${e + 1}/15 — acc: ${(logs.acc * 100).toFixed(1)}%`),
  },
});

console.log(`💾 저장 중: ${OUTPUT_DIR}`);
mkdirSync(OUTPUT_DIR, { recursive: true });

await model.save(tf.io.withSaveHandler(async (artifacts) => {
  const modelJson = {
    modelTopology: artifacts.modelTopology,
    weightsManifest: [{
      paths: ["group1-shard1of1.bin"],
      weights: artifacts.weightSpecs,
    }],
    format: "layers-model",
    generatedBy: "TensorFlow.js tfjs-layers",
    convertedBy: null,
  };
  writeFileSync(path.join(OUTPUT_DIR, "model.json"), JSON.stringify(modelJson));
  writeFileSync(
    path.join(OUTPUT_DIR, "group1-shard1of1.bin"),
    Buffer.from(artifacts.weightData)
  );
  return { modelArtifactsInfo: { dateSaved: new Date(), modelTopologyType: "JSON" } };
}));

console.log("✅ 완료! public/mnist_model/ 에 저장됨");
