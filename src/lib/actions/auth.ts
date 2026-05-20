"use server"

import { prisma } from "@/lib/prisma/client"
import bcrypt from "bcryptjs"
import { registerSchema, type RegisterInput } from "@/lib/validations/auth"

export async function registerUser(data: RegisterInput) {
  const parsedData = registerSchema.safeParse(data)

  if (!parsedData.success) {
    return { error: "유효하지 않은 입력값입니다." }
  }

  const { email, password, name } = parsedData.data

  try {
    const existingUser = await prisma.user.findUnique({
      where: { email },
    })

    if (existingUser) {
      return { error: "이미 가입된 이메일입니다." }
    }

    const hashedPassword = await bcrypt.hash(password, 10)

    await prisma.user.create({
      data: {
        email,
        password: hashedPassword,
        name,
      },
    })

    return { success: true }
  } catch (error: any) {
    console.error("❌ 회원가입 상세 에러:", {
      code: error?.code,
      message: error?.message,
      meta: error?.meta,
      clientVersion: error?.clientVersion,
      errorCode: error?.errorCode
    })
    return { error: `회원가입 에러: ${error?.message || 'DB 연결 확인 필요'}` }
  }
}
