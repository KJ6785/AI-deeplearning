import { RegisterForm } from '@/components/auth/register-form'
import Link from 'next/link'

export default function RegisterPage() {
  return (
    <div className="container mx-auto px-4 py-16">
      <RegisterForm />
      <p className="mt-4 text-center text-sm text-muted-foreground">
        이미 계정이 있으신가요?{' '}
        <Link href="/auth/login" className="text-primary hover:underline">
          로그인
        </Link>
      </p>
    </div>
  )
}
