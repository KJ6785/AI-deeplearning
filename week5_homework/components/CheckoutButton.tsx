"use client";

import { useState } from "react";

export default function CheckoutButton() {
  const [loading, setLoading] = useState(false);

  async function handleClick() {
    setLoading(true);
    const res = await fetch("/api/checkout", { method: "POST" });
    const { url } = await res.json();
    if (url) window.location.href = url;
    else setLoading(false);
  }

  return (
    <button
      onClick={handleClick}
      disabled={loading}
      className="bg-yellow-500 hover:bg-yellow-400 disabled:opacity-50 text-black px-6 py-2.5 rounded-lg font-semibold text-sm transition-colors"
    >
      {loading ? "처리 중..." : "₩9,900 으로 업그레이드"}
    </button>
  );
}
