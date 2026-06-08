"use client";

import { useState, useEffect } from "react";

type Curve = { epoch: number; train: number; val: number };

function generateCurves(type: "none" | "l2" | "dropout"): Curve[] {
  const curves: Curve[] = [];
  for (let e = 1; e <= 50; e++) {
    const t = e / 50;
    let trainLoss: number, valLoss: number;

    if (type === "none") {
      trainLoss = 2.0 * Math.exp(-4 * t) + 0.05;
      valLoss = 2.0 * Math.exp(-2.5 * t) + 0.4 + 0.3 * t;
    } else if (type === "l2") {
      trainLoss = 2.0 * Math.exp(-3.5 * t) + 0.15;
      valLoss = 2.0 * Math.exp(-3 * t) + 0.2 + 0.05 * t;
    } else {
      trainLoss = 2.0 * Math.exp(-3 * t) + 0.18;
      valLoss = 2.0 * Math.exp(-2.8 * t) + 0.22 + 0.02 * t;
    }

    trainLoss += (Math.random() - 0.5) * 0.04;
    valLoss += (Math.random() - 0.5) * 0.06;

    curves.push({ epoch: e, train: Math.max(0, trainLoss), val: Math.max(0, valLoss) });
  }
  return curves;
}

const W = 500, H = 260, PAD = { top: 20, right: 20, bottom: 40, left: 50 };

function toSvgX(epoch: number) {
  return PAD.left + ((epoch - 1) / 49) * (W - PAD.left - PAD.right);
}
function toSvgY(loss: number) {
  const maxLoss = 2.1;
  return PAD.top + (1 - loss / maxLoss) * (H - PAD.top - PAD.bottom);
}

function polyline(data: Curve[], key: "train" | "val") {
  return data.map((d) => `${toSvgX(d.epoch)},${toSvgY(d[key])}`).join(" ");
}

export default function RegularizationChart({ isPremium }: { isPremium: boolean }) {
  const [mode, setMode] = useState<"none" | "l2" | "dropout">("none");
  const [data, setData] = useState<Curve[]>([]);

  useEffect(() => {
    setData(generateCurves(mode));
  }, [mode]);

  if (!isPremium) {
    return (
      <div className="h-48 bg-gray-800 rounded-xl flex items-center justify-center text-gray-500 text-sm">
        차트 미리보기
      </div>
    );
  }

  const labels = { none: "규제 없음 (과적합)", l2: "L2 Regularization", dropout: "Dropout (0.5)" };

  return (
    <div>
      <div className="flex gap-2 mb-6 flex-wrap">
        {(["none", "l2", "dropout"] as const).map((m) => (
          <button
            key={m}
            onClick={() => setMode(m)}
            className={`text-xs px-3 py-1.5 rounded-lg border transition-colors ${
              mode === m
                ? "bg-blue-600 border-blue-500 text-white"
                : "border-gray-700 text-gray-400 hover:border-gray-500"
            }`}
          >
            {labels[m]}
          </button>
        ))}
      </div>

      <div className="overflow-x-auto">
        <svg width={W} height={H} className="text-xs">
          {/* Grid lines */}
          {[0, 0.5, 1.0, 1.5, 2.0].map((v) => (
            <g key={v}>
              <line
                x1={PAD.left}
                y1={toSvgY(v)}
                x2={W - PAD.right}
                y2={toSvgY(v)}
                stroke="#374151"
                strokeDasharray="4,4"
              />
              <text x={PAD.left - 6} y={toSvgY(v) + 4} textAnchor="end" fill="#6b7280" fontSize="10">
                {v.toFixed(1)}
              </text>
            </g>
          ))}

          {/* X axis labels */}
          {[1, 10, 20, 30, 40, 50].map((e) => (
            <text key={e} x={toSvgX(e)} y={H - 8} textAnchor="middle" fill="#6b7280" fontSize="10">
              {e}
            </text>
          ))}

          {/* Axes */}
          <line x1={PAD.left} y1={PAD.top} x2={PAD.left} y2={H - PAD.bottom} stroke="#4b5563" />
          <line x1={PAD.left} y1={H - PAD.bottom} x2={W - PAD.right} y2={H - PAD.bottom} stroke="#4b5563" />

          {/* Curves */}
          {data.length > 0 && (
            <>
              <polyline points={polyline(data, "train")} fill="none" stroke="#3b82f6" strokeWidth="2" />
              <polyline
                points={polyline(data, "val")}
                fill="none"
                stroke={mode === "none" ? "#ef4444" : "#22c55e"}
                strokeWidth="2"
                strokeDasharray={mode === "none" ? "6,3" : "0"}
              />
            </>
          )}

          {/* Labels */}
          <text x={PAD.left + 8} y={PAD.top + 14} fill="#3b82f6" fontSize="11">— Train Loss</text>
          <text x={PAD.left + 100} y={PAD.top + 14} fill={mode === "none" ? "#ef4444" : "#22c55e"} fontSize="11">
            {mode === "none" ? "- - Val Loss (과적합!)" : "— Val Loss"}
          </text>
          <text x={W / 2} y={H - 2} textAnchor="middle" fill="#6b7280" fontSize="10">Epoch</text>
        </svg>
      </div>

      <div className="mt-4 grid grid-cols-3 gap-3 text-xs">
        {[
          {
            title: "규제 없음",
            desc: "Train Loss↓ Val Loss↑\n→ 과적합(Overfitting)",
            color: "border-red-800",
          },
          {
            title: "L2 Regularization",
            desc: "가중치 크기에 패널티\n→ 과적합 완화",
            color: "border-blue-800",
          },
          {
            title: "Dropout (0.5)",
            desc: "50% 뉴런 랜덤 비활성화\n→ 앙상블 효과",
            color: "border-green-800",
          },
        ].map((item) => (
          <div key={item.title} className={`bg-gray-800 border ${item.color} rounded-lg p-3`}>
            <p className="font-medium text-gray-300 mb-1">{item.title}</p>
            <p className="text-gray-500 whitespace-pre-line">{item.desc}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
