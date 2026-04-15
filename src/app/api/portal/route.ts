// src/app/api/portal/route.ts
import { CustomerPortal } from '@polar-sh/nextjs'

export const GET = CustomerPortal({
  accessToken: process.env.POLAR_ACCESS_TOKEN!,
  // 고객 ID가 없을 경우 공백으로 두면, Polar가 사용자에게 이메일(매직 링크)을 보냅니다.
  getCustomerId: async () => '',
  server: (process.env.POLAR_SERVER as 'sandbox' | 'production') || 'sandbox',
})
