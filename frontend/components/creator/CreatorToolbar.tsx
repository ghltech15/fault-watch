'use client'

import { useState, useCallback, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Camera, Maximize2, Share2, Code, Video, X, Check, Download, Copy, Twitter, MessageCircle } from 'lucide-react'
import html2canvas from 'html2canvas'
import copy from 'copy-to-clipboard'

interface CreatorToolbarProps {
  currentSection?: string
}

export function CreatorToolbar({ currentSection }: CreatorToolbarProps) {
  const [isOpen, setIsOpen] = useState(false)
  const [isFullscreen, setIsFullscreen] = useState(false)
  const [isRecordMode, setIsRecordMode] = useState(false)
  const [showShareModal, setShowShareModal] = useState(false)
  const [showEmbedModal, setShowEmbedModal] = useState(false)
  const [screenshotStatus, setScreenshotStatus] = useState<'idle' | 'capturing' | 'done'>('idle')
  const [copied, setCopied] = useState(false)

  // Toggle fullscreen
  const toggleFullscreen = useCallback(() => {
    if (!document.fullscreenElement) {
      document.documentElement.requestFullscreen()
      setIsFullscreen(true)
    } else {
      document.exitFullscreen()
      setIsFullscreen(false)
    }
  }, [])

  // Capture screenshot
  const captureScreenshot = useCallback(async () => {
    setScreenshotStatus('capturing')

    try {
      // Capture the main content area
      const element = document.getElementById('main-content') || document.body

      const canvas = await html2canvas(element, {
        backgroundColor: '#0a0a0a',
        scale: 2,
        logging: false,
        useCORS: true,
        allowTaint: true
      })

      // Add watermark
      const ctx = canvas.getContext('2d')
      if (ctx) {
        ctx.font = 'bold 16px Inter, sans-serif'
        ctx.fillStyle = 'rgba(255, 255, 255, 0.5)'
        ctx.fillText('fault.watch', canvas.width - 120, canvas.height - 20)
      }

      // Download
      const link = document.createElement('a')
      link.download = `fault-watch-${currentSection || 'dashboard'}-${Date.now()}.png`
      link.href = canvas.toDataURL('image/png')
      link.click()

      setScreenshotStatus('done')
      setTimeout(() => setScreenshotStatus('idle'), 2000)
    } catch (error) {
      console.error('Screenshot failed:', error)
      setScreenshotStatus('idle')
    }
  }, [currentSection])

  // Toggle record mode
  const toggleRecordMode = useCallback(() => {
    setIsRecordMode(prev => !prev)
    document.body.classList.toggle('record-mode')
  }, [])

  // Copy share link
  const copyShareLink = useCallback(() => {
    const url = window.location.href
    copy(url)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }, [])

  // Listen for keyboard shortcuts
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'f' && !e.ctrlKey && !e.metaKey) {
        toggleFullscreen()
      }
      if (e.key === 's' && (e.ctrlKey || e.metaKey)) {
        e.preventDefault()
        captureScreenshot()
      }
    }

    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [toggleFullscreen, captureScreenshot])

  // Generate embed code
  const embedCode = `<iframe
  src="https://fault.watch/embed/gauge"
  width="300"
  height="400"
  frameborder="0"
  style="border-radius: 12px; background: #0a0a0a;"
></iframe>`

  return (
    <>
      {/* Record Mode Overlay */}
      <AnimatePresence>
        {isRecordMode && (
          <motion.div
            className="fixed inset-0 pointer-events-none z-[9999]"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
          >
            {/* Red recording border */}
            <div className="absolute inset-0 border-4 border-red-500/50" />

            {/* Recording indicator */}
            <div className="absolute top-4 right-4 flex items-center gap-2 bg-black/80 px-3 py-2 rounded-full pointer-events-auto">
              <div className="w-3 h-3 bg-red-500 rounded-full animate-pulse" />
              <span className="text-white text-sm font-bold">REC</span>
              <button
                onClick={toggleRecordMode}
                className="ml-2 text-gray-400 hover:text-white"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            {/* Watermark */}
            <div className="absolute bottom-4 right-4 text-white/30 text-sm font-bold">
              fault.watch
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Main Toolbar */}
      <div className="fixed bottom-6 left-1/2 -translate-x-1/2 z-50">
        <motion.div
          className="bg-gray-900/95 backdrop-blur-xl border border-gray-700 rounded-2xl shadow-2xl overflow-hidden"
          initial={{ y: 100, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ delay: 1, duration: 0.5 }}
        >
          <div className="flex items-center gap-1 p-2">
            {/* Screenshot */}
            <ToolbarButton
              icon={screenshotStatus === 'done' ? <Check className="w-5 h-5" /> : <Camera className="w-5 h-5" />}
              label="Screenshot"
              shortcut="Ctrl+S"
              onClick={captureScreenshot}
              active={screenshotStatus === 'capturing'}
              success={screenshotStatus === 'done'}
            />

            {/* Fullscreen */}
            <ToolbarButton
              icon={<Maximize2 className="w-5 h-5" />}
              label="Fullscreen"
              shortcut="F"
              onClick={toggleFullscreen}
              active={isFullscreen}
            />

            {/* Share */}
            <ToolbarButton
              icon={<Share2 className="w-5 h-5" />}
              label="Share"
              onClick={() => setShowShareModal(true)}
            />

            {/* Embed */}
            <ToolbarButton
              icon={<Code className="w-5 h-5" />}
              label="Embed"
              onClick={() => setShowEmbedModal(true)}
            />

            {/* Record Mode */}
            <ToolbarButton
              icon={<Video className="w-5 h-5" />}
              label="Record"
              onClick={toggleRecordMode}
              active={isRecordMode}
              danger={isRecordMode}
            />
          </div>
        </motion.div>
      </div>

      {/* Share Modal */}
      <AnimatePresence>
        {showShareModal && (
          <Modal onClose={() => setShowShareModal(false)} title="Share fault.watch">
            <div className="space-y-4">
              {/* Share text */}
              <div className="bg-gray-800 rounded-lg p-4">
                <p className="text-gray-300 text-sm mb-3">
                  Check out the live crisis probability tracker on fault.watch - monitoring systemic banking risk from precious metals exposure in real-time.
                </p>
                <div className="flex gap-2">
                  <button
                    onClick={copyShareLink}
                    className="flex-1 flex items-center justify-center gap-2 bg-gray-700 hover:bg-gray-600 text-white py-2 px-4 rounded-lg transition"
                  >
                    {copied ? <Check className="w-4 h-4" /> : <Copy className="w-4 h-4" />}
                    {copied ? 'Copied!' : 'Copy Link'}
                  </button>
                </div>
              </div>

              {/* Social buttons */}
              <div className="grid grid-cols-2 gap-3">
                <a
                  href={`https://twitter.com/intent/tweet?text=${encodeURIComponent('Check out the live crisis probability tracker on fault.watch - monitoring systemic banking risk from precious metals exposure.')}&url=${encodeURIComponent('https://fault.watch')}`}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flex items-center justify-center gap-2 bg-blue-500 hover:bg-blue-600 text-white py-3 px-4 rounded-lg transition"
                >
                  <Twitter className="w-5 h-5" />
                  Twitter
                </a>
                <a
                  href={`https://reddit.com/submit?url=${encodeURIComponent('https://fault.watch')}&title=${encodeURIComponent('Live Crisis Probability Tracker - fault.watch')}`}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flex items-center justify-center gap-2 bg-orange-500 hover:bg-orange-600 text-white py-3 px-4 rounded-lg transition"
                >
                  <MessageCircle className="w-5 h-5" />
                  Reddit
                </a>
              </div>
            </div>
          </Modal>
        )}
      </AnimatePresence>

      {/* Embed Modal */}
      <AnimatePresence>
        {showEmbedModal && (
          <Modal onClose={() => setShowEmbedModal(false)} title="Embed Widget">
            <div className="space-y-4">
              <p className="text-gray-400 text-sm">
                Add a live crisis gauge to your website or stream overlay.
              </p>

              {/* Preview */}
              <div className="bg-gray-800 rounded-lg p-4 text-center">
                <div className="inline-block bg-black rounded-xl p-4 border border-gray-700">
                  <div className="text-5xl font-black text-amber-400">72%</div>
                  <div className="text-xs text-gray-400 mt-1">CRISIS PROBABILITY</div>
                  <div className="text-[10px] text-gray-600 mt-2">fault.watch</div>
                </div>
              </div>

              {/* Code */}
              <div className="relative">
                <pre className="bg-gray-800 rounded-lg p-4 text-xs text-gray-300 overflow-x-auto">
                  {embedCode}
                </pre>
                <button
                  onClick={() => {
                    copy(embedCode)
                    setCopied(true)
                    setTimeout(() => setCopied(false), 2000)
                  }}
                  className="absolute top-2 right-2 p-2 bg-gray-700 hover:bg-gray-600 rounded-lg transition"
                >
                  {copied ? <Check className="w-4 h-4 text-green-400" /> : <Copy className="w-4 h-4 text-gray-400" />}
                </button>
              </div>
            </div>
          </Modal>
        )}
      </AnimatePresence>
    </>
  )
}

// Toolbar Button Component
function ToolbarButton({
  icon,
  label,
  shortcut,
  onClick,
  active,
  success,
  danger
}: {
  icon: React.ReactNode
  label: string
  shortcut?: string
  onClick: () => void
  active?: boolean
  success?: boolean
  danger?: boolean
}) {
  return (
    <button
      onClick={onClick}
      className={`relative group flex flex-col items-center justify-center w-16 h-14 rounded-xl transition ${
        success
          ? 'bg-green-500/20 text-green-400'
          : danger
          ? 'bg-red-500/20 text-red-400'
          : active
          ? 'bg-blue-500/20 text-blue-400'
          : 'hover:bg-gray-800 text-gray-400 hover:text-white'
      }`}
    >
      {icon}
      <span className="text-[10px] mt-1">{label}</span>

      {/* Tooltip with shortcut */}
      {shortcut && (
        <div className="absolute -top-10 left-1/2 -translate-x-1/2 bg-gray-800 text-white text-xs px-2 py-1 rounded opacity-0 group-hover:opacity-100 transition whitespace-nowrap pointer-events-none">
          {shortcut}
        </div>
      )}
    </button>
  )
}

// Modal Component
function Modal({
  onClose,
  title,
  children
}: {
  onClose: () => void
  title: string
  children: React.ReactNode
}) {
  return (
    <motion.div
      className="fixed inset-0 z-[100] flex items-center justify-center p-4"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
    >
      <div className="absolute inset-0 bg-black/80 backdrop-blur-sm" onClick={onClose} />
      <motion.div
        className="relative bg-gray-900 border border-gray-700 rounded-2xl w-full max-w-md overflow-hidden"
        initial={{ scale: 0.9, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        exit={{ scale: 0.9, opacity: 0 }}
      >
        <div className="flex items-center justify-between p-4 border-b border-gray-800">
          <h3 className="font-bold text-white">{title}</h3>
          <button onClick={onClose} className="p-2 hover:bg-gray-800 rounded-lg transition">
            <X className="w-5 h-5 text-gray-400" />
          </button>
        </div>
        <div className="p-4">{children}</div>
      </motion.div>
    </motion.div>
  )
}
