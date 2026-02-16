import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import Script from 'next/script'
import './globals.css'
import { Providers } from './providers'

const inter = Inter({ subsets: ['latin'] })

const GA_MEASUREMENT_ID = 'G-J40XCP5K2S'

export const metadata: Metadata = {
  title: 'fault.watch – Live Silver Crisis Tracker',
  description: 'Track when silver stress could trigger a banking crisis. Real-time monitoring of bank exposure and systemic risk.',
  openGraph: {
    title: 'fault.watch – Live Silver Crisis Tracker',
    description: 'Track when silver stress could trigger a banking crisis. Real-time monitoring of bank exposure and systemic risk.',
    url: 'https://fault.watch',
    siteName: 'fault.watch',
    type: 'website',
  },
  twitter: {
    card: 'summary_large_image',
    title: 'fault.watch – Live Silver Crisis Tracker',
    description: 'Track when silver stress could trigger a banking crisis. Real-time monitoring of bank exposure and systemic risk.',
  },
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" suppressHydrationWarning>
      <head>
        <Script
          src={`https://www.googletagmanager.com/gtag/js?id=${GA_MEASUREMENT_ID}`}
          strategy="afterInteractive"
        />
        <Script id="google-analytics" strategy="afterInteractive">
          {`
            window.dataLayer = window.dataLayer || [];
            function gtag(){dataLayer.push(arguments);}
            gtag('js', new Date());
            gtag('config', '${GA_MEASUREMENT_ID}');
          `}
        </Script>
      </head>
      <body className={inter.className}>
        <Providers>
          {children}
          {/* Site-wide Footer */}
          <footer className="border-t border-gray-800 bg-gray-950 py-8 px-4">
            <div className="max-w-6xl mx-auto">
              <div className="text-center mb-6">
                <p className="text-gray-400 text-sm max-w-2xl mx-auto">
                  Fault.watch is speculative analysis, not financial advice. It helps you explore &quot;what if&quot; scenarios so you can think for yourself.
                </p>
              </div>
              <div className="border-t border-gray-800 pt-6">
                <div className="flex flex-col md:flex-row items-center justify-between gap-4">
                  <div className="text-gray-500 text-xs">
                    <span className="font-bold text-gray-400">How It Works:</span>{' '}
                    Data from real-time silver prices, COMEX inventory, bank stocks{' '}
                    <span className="text-gray-600">|</span>{' '}
                    Weighted risk model across precious metals, banking, credit sectors{' '}
                    <span className="text-gray-600">|</span>{' '}
                    5-stage cascade progression{' '}
                    <span className="text-gray-600">|</span>{' '}
                    Auto-refresh every 5 minutes
                  </div>
                  <div className="text-gray-600 text-xs">
                    fault.watch
                  </div>
                </div>
              </div>
            </div>
          </footer>
        </Providers>
      </body>
    </html>
  )
}
