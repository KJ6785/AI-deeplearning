// src/app/api/webhooks/polar/route.ts
import { Webhooks } from '@polar-sh/nextjs'

export const POST = Webhooks({
  webhookSecret: process.env.POLAR_WEBHOOK_SECRET || '',

  // 결제 완료 (일회성 구매 등)
  onOrderCreated: async (payload) => {
    const order = payload.data
    console.log('💰 [ORDER SUCCESS]:', {
      orderId: order.id,
      amount: order.amount,
      currency: order.currency,
      email: order.customer?.email,
      productName: order.product?.name
    })
  },

  // 구독 시작
  onSubscriptionCreated: async (payload) => {
    const subscription = payload.data
    console.log('🔄 [SUBSCRIPTION STARTED]:', {
      subId: subscription.id,
      status: subscription.status,
      email: subscription.customer?.email,
      productName: subscription.product?.name
    })
  },

  // 구독 수정/취소
  onSubscriptionUpdated: async (payload) => {
    const subscription = payload.data
    console.log('🔄 [SUBSCRIPTION UPDATED]:', {
      subId: subscription.id,
      status: subscription.status,
      nextPayment: subscription.currentPeriodEnd
    })
  },

  // 체크아웃 확인 (결제 시도 시)
  onCheckoutUpdated: async (payload) => {
    const checkout = payload.data
    if (checkout.status === 'confirmed') {
      console.log('💳 [CHECKOUT CONFIRMED]:', checkout.id)
    }
  }
})
