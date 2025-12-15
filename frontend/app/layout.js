import { Inter } from 'next/font/google'
import './globals.css'
import { cn } from '@/utils/cn'

const inter = Inter({ subsets: ['latin'] })

export const metadata = {
  title: 'Todo App',
  description: 'A modern todo application with AI integration',
}

export default function RootLayout({ children }) {
  return (
    <html lang="en" className="dark">
      <body className={cn(inter.className, "antialiased min-h-screen")}>
        {children}
      </body>
    </html>
  )
}