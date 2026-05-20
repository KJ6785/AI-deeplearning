// src/app/auth/callback/route.ts
import { createClient } from '@/lib/supabase/server'
import { prisma } from '@/lib/prisma/client'
import { NextResponse } from 'next/server'

export async function GET(request: Request) {
  const { searchParams, origin } = new URL(request.url)
  const code = searchParams.get('code')
  const next = searchParams.get('next') ?? '/'

  if (code) {
    const supabase = await createClient()
    const { data, error } = await supabase.auth.exchangeCodeForSession(code)

    if (!error && data.user) {
      // users 테이블에 레코드 확인/생성 (Prisma)
      await prisma.user.upsert({
        where: { id: data.user.id },
        update: { email: data.user.email! },
        create: {
          id: data.user.id,
          email: data.user.email!,
          name: data.user.user_metadata?.full_name || null,
        },
      })

      return NextResponse.redirect(`${origin}${next}`)
    }
  }

  // 에러 발생 시 로그인 페이지로 리다이렉트
  return NextResponse.redirect(`${origin}/auth/login?error=auth_failed`)
}
