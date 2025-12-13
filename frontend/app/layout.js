import './globals.css'

export const metadata = {
  title: 'Todo App',
  description: 'A modern todo application with AI integration',
}

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body suppressHydrationWarning={true}>{children}</body>
    </html>
  )
}