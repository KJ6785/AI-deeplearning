import { NextResponse } from "next/server";

export async function GET() {
  const res = await fetch(
    "https://storage.googleapis.com/tfjs-examples/mnist/data/mnist_labels_uint8",
    { next: { revalidate: 86400 } }
  );
  const buf = await res.arrayBuffer();
  return new NextResponse(buf, {
    headers: {
      "Content-Type": "application/octet-stream",
      "Cache-Control": "public, max-age=86400",
    },
  });
}
