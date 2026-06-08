import { NextRequest, NextResponse } from "next/server";
import { auth } from "@/lib/auth";
import { stripe } from "@/lib/stripe";
import { prisma } from "@/lib/db";

export async function POST(req: NextRequest) {
  const session = await auth();
  if (!session?.user?.email) {
    return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
  }

  const user = await prisma.user.findUnique({
    where: { email: session.user.email },
  });
  if (!user) return NextResponse.json({ error: "User not found" }, { status: 404 });

  const origin = req.headers.get("origin") ?? "http://localhost:3000";

  const checkoutSession = await stripe.checkout.sessions.create({
    payment_method_types: ["card"],
    mode: "payment",
    customer_email: user.email,
    line_items: [
      {
        price_data: {
          currency: "krw",
          product_data: {
            name: "Week5 ML Lab Premium",
            description: "정규화/과적합 시각화 + 전이학습 실험실 접근권",
          },
          unit_amount: 9900,
        },
        quantity: 1,
      },
    ],
    metadata: { userId: user.id },
    success_url: `${origin}/dashboard?success=true`,
    cancel_url: `${origin}/dashboard?canceled=true`,
  });

  return NextResponse.json({ url: checkoutSession.url });
}
