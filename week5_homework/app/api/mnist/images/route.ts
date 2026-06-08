import { NextResponse } from "next/server";

export async function GET() {
  const res = await fetch(
    "https://storage.googleapis.com/tfjs-examples/mnist/data/mnist_images.png",
    { next: { revalidate: 86400 } }
  );
  const buf = await res.arrayBuffer();
  return new NextResponse(buf, {
    headers: {
      "Content-Type": "image/png",
      "Cache-Control": "public, max-age=86400",
    },
  });
}
