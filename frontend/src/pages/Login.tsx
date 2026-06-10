import { SignIn } from '@clerk/clerk-react'

export default function Login() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-100 dark:bg-gray-900">
      <div className="flex flex-col lg:flex-row gap-8 items-center">
        {/* Branding */}
        <div className="text-center lg:text-left lg:pr-12">
          <h1 className="text-4xl font-bold text-gray-900 dark:text-white mb-2">
            Xeno AI
          </h1>
          <p className="text-lg text-gray-600 dark:text-gray-400">
            Campaign Intelligence Platform
          </p>
          <p className="mt-4 text-sm text-gray-500 dark:text-gray-500 max-w-xs">
            AI-native marketing CRM for discovering audiences, creating campaigns, and tracking engagement.
          </p>
        </div>

        {/* Clerk Sign In / Sign Up */}
        <div className="bg-white dark:bg-gray-800 p-6 rounded-xl shadow-lg">
          <SignIn 
            routing="path"
            path="/login"
            signUpUrl="/login?mode=sign-up"
            afterSignInUrl="/"
          />
        </div>
      </div>
    </div>
  )
}