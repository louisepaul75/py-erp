import { useEffect } from 'react'
import { useRouter } from 'next/router'

export default function Home() {
  const router = useRouter()
  
  useEffect(() => {
    // Redirect to the root path which now renders the Dashboard in the App Router
    router.push('/')
  }, [router])
  
  return (
    <div className="flex items-center justify-center min-h-screen">
      <p>Redirecting...</p>
    </div>
  )
} 