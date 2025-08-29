import '@/styles/globals.css'
import React from 'react'

export default function RootLayout({ children }: { children: React.ReactNode }) {
 return (
  <html lang="pt-br">
   <body className="min-h-screen bg-gray-50 text-gray-900">
    <div className="max-w-screen-2xl mx-auto p-4">{children}</div>
   </body>
  </html>
 )
}
