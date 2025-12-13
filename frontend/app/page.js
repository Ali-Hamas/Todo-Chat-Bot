import Link from 'next/link';

export default function Home() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-24 bg-gray-50">
      <div className="z-10 w-full max-w-md items-center justify-center text-center">
        <h1 className="text-4xl font-bold text-gray-900 mb-6">
          Welcome to the <span className="text-blue-600">Todo App</span>
        </h1>
        <p className="text-lg text-gray-600 mb-8">
          A modern todo application with AI integration
        </p>
        <div className="space-y-4">
          <Link
            href="/login"
            className="inline-block bg-blue-500 hover:bg-blue-600 text-white font-medium py-3 px-6 rounded-lg transition duration-200 mb-2"
          >
            Get Started
          </Link>
          <p className="text-sm text-gray-500">
            Login or create an account to access the AI assistant
          </p>
        </div>
      </div>
    </main>
  )
}