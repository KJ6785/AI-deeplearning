import { LoginForm } from '@/components/auth/login-form'
import Link from 'next/link'

export default function LoginPage() {
  return (
    <div className="container mx-auto px-4 py-16">
      <LoginForm />
      <p className="mt-4 text-center text-sm text-muted-foreground">
        계정이 없으신가요?{' '}
        <Link href="/auth/register" className="text-primary hover:underline">
          회원가입
        </Link>
      </p>
    </div>
  )
}
