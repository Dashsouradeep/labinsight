import Link from 'next/link'

export default function Home() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-24">
      <div className="text-center">
        <h1 className="text-4xl font-bold text-primary-dark mb-4">
          LabInsight
        </h1>
        <p className="text-xl text-gray-700 mb-8">
          Health Intelligence Platform
        </p>
        <p className="text-gray-600 mb-12">
          AI-powered medical lab report analysis
        </p>
        
        <div className="flex gap-4 justify-center">
          <Link 
            href="/auth/login"
            className="px-6 py-3 bg-primary text-white rounded-lg hover:bg-primary-dark transition-colors font-medium"
          >
            Login
          </Link>
          <Link 
            href="/auth/signup"
            className="px-6 py-3 bg-white text-primary border-2 border-primary rounded-lg hover:bg-gray-50 transition-colors font-medium"
          >
            Sign Up
          </Link>
        </div>
      </div>
    </main>
  )
}
