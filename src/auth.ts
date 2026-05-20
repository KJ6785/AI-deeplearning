// src/auth.ts
import NextAuth from "next-auth"
import Credentials from "next-auth/providers/credentials"
import { prisma } from "@/lib/prisma/client"
import bcrypt from "bcryptjs"
import { loginSchema } from "@/lib/validations/auth"

export const { handlers, signIn, signOut, auth } = NextAuth({
  providers: [
    Credentials({
      async authorize(credentials) {
        const parsedCredentials = loginSchema.safeParse(credentials)

        if (parsedCredentials.success) {
          const { email, password } = parsedCredentials.data
          // 로컬 SQLite DB에서 사용자 정보를 정석적으로 조회합니다.
          const user = await prisma.user.findUnique({ where: { email } })
          
          if (!user || !user.password) return null
          
          // 보안을 위해 비밀번호의 해시 값을 비교합니다.
          const passwordsMatch = await bcrypt.compare(password, user.password)
          
          if (passwordsMatch) return {
            id: user.id,
            email: user.email,
            name: user.name,
          }
        }

        return null
      },
    }),
  ],
  callbacks: {
    authorized({ auth, request: { nextUrl } }) {
      const isLoggedIn = !!auth?.user
      const isOnAccount = nextUrl.pathname.startsWith('/account')
      const isOnCheckout = nextUrl.pathname.startsWith('/checkout')
      
      if (isOnAccount || isOnCheckout) {
        if (isLoggedIn) return true
        return false // 로그인 페이지로 리다이렉트
      }
      return true
    },
    jwt({ token, user }) {
      if (user) {
        token.id = user.id
      }
      return token
    },
    session({ session, token }) {
      if (session.user) {
        session.user.id = token.id as string
      }
      return session
    }
  },
  pages: {
    signIn: '/auth/login',
  },
})
