'use client'

import React, { useEffect, useState, useRef } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Brain, Cpu, FileText, Database, ChevronRight, CheckCircle2, AlertCircle, Clock, Play } from 'lucide-react'
import ProcessingStepCard from './ProcessingStepCard'

type ProcessStep = {
  id: string
  name: string
  description: string
  percentageOfTotal: number
  status: 'waiting' | 'processing' | 'success' | 'error' | 'skipped' | 'initializing'
  details?: string
  startTime?: string
  endTime?: string
  isInitStep?: boolean
}

type ProcessingMetrics = {
  elapsedTime: number
  estimatedTimeRemaining: number
  processingSpeed: number // blocks per second
  successRate: number
}

type EnhancedProcessingProgressProps = {
  steps: ProcessStep[]
  currentStepId: string | null
  overallProgress: number
  onComplete?: () => void
  processingComplete: boolean
  fileName: string
}

export default function EnhancedProcessingProgress({
  steps,
  currentStepId,
  overallProgress,
  onComplete,
  processingComplete,
  fileName
}: EnhancedProcessingProgressProps) {
  const [animatedProgress, setAnimatedProgress] = useState(0)
  const [showTechDetails, setShowTechDetails] = useState(false)
  const [metrics, setMetrics] = useState<ProcessingMetrics>({
    elapsedTime: 0,
    estimatedTimeRemaining: 0,
    processingSpeed: 0,
    successRate: 100
  })
  const startTimeRef = useRef<Date | null>(null)
  const progressHistory = useRef<Array<{ time: number; progress: number }>>([])

  // Initialize start time
  useEffect(() => {
    if (!startTimeRef.current && steps.some(s => s.status === 'processing')) {
      startTimeRef.current = new Date()
    }
  }, [steps])

  // Update metrics
  useEffect(() => {
    if (!startTimeRef.current) return

    const updateMetrics = () => {
      const now = new Date()
      const startTime = startTimeRef.current
      if (!startTime) return
      
      const elapsedTime = (now.getTime() - startTime.getTime()) / 1000
      
      // Update progress history
      progressHistory.current.push({
        time: elapsedTime,
        progress: overallProgress
      })

      // Keep only last 10 seconds of history
      const recentHistory = progressHistory.current.filter(
        entry => entry.time > elapsedTime - 10
      )
      progressHistory.current = recentHistory

      // Calculate processing speed (progress per second)
      let speedSample = 0
      if (recentHistory.length > 1) {
        const latestEntry = recentHistory[recentHistory.length - 1]
        const oldestEntry = recentHistory[0]
        if (latestEntry && oldestEntry) {
          speedSample = (latestEntry.progress - oldestEntry.progress) /
                       (latestEntry.time - oldestEntry.time)
        }
      }

      // Estimate remaining time
      const remainingProgress = 100 - overallProgress
      const estimatedTimeRemaining = speedSample > 0 ? remainingProgress / speedSample : 0

      // Calculate success rate
      const completedSteps = steps.filter(s => s.status !== 'waiting' && s.status !== 'processing')
      const successRate = completedSteps.length > 0
        ? (completedSteps.filter(s => s.status === 'success').length / completedSteps.length) * 100
        : 100

      setMetrics({
        elapsedTime,
        estimatedTimeRemaining,
        processingSpeed: speedSample,
        successRate
      })
    }

    const interval = setInterval(updateMetrics, 1000)
    return () => clearInterval(interval)
  }, [overallProgress, steps])

  // Animate progress bar
  useEffect(() => {
    const animationDuration = 300
    const interval = 10
    const step = (overallProgress - animatedProgress) / (animationDuration / interval)
    
    if (Math.abs(overallProgress - animatedProgress) < 0.5) {
      setAnimatedProgress(overallProgress)
      return
    }
    
    const timer = setTimeout(() => {
      setAnimatedProgress(prev => Math.min(prev + step, overallProgress))
    }, interval)
    
    return () => clearTimeout(timer)
  }, [overallProgress, animatedProgress])

  // Trigger completion callback
  useEffect(() => {
    if (processingComplete && onComplete) {
      onComplete()
    }
  }, [processingComplete, onComplete])

  const formatTime = (seconds: number): string => {
    if (!isFinite(seconds) || seconds < 0) return '--:--'
    const mins = Math.floor(seconds / 60)
    const secs = Math.floor(seconds % 60)
    return `${mins}:${secs.toString().padStart(2, '0')}`
  }

  const getStepIcon = (step: ProcessStep) => {
    const baseClasses = "w-8 h-8 rounded-full flex items-center justify-center"
    const variants = {
      initial: { scale: 0.8, opacity: 0 },
      animate: { scale: 1, opacity: 1 },
      exit: { scale: 0.8, opacity: 0 }
    }

    switch (step.status) {
      case 'waiting':
        return (
          <motion.div
            className={`${baseClasses} border-2 border-gray-300`}
            variants={variants}
            initial="initial"
            animate="animate"
            exit="exit"
          >
            <span className="text-sm text-gray-500">
              {steps.findIndex(s => s.id === step.id) + 1}
            </span>
          </motion.div>
        )
      case 'processing':
        return (
          <motion.div
            className={`${baseClasses} bg-blue-500`}
            variants={variants}
            initial="initial"
            animate="animate"
            exit="exit"
            whileHover={{ scale: 1.1 }}
          >
            <svg className="w-5 h-5 text-white animate-spin" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
              <path
                className="opacity-75"
                fill="currentColor"
                d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
              />
            </svg>
          </motion.div>
        )
      case 'success':
        return (
          <motion.div
            className={`${baseClasses} bg-green-500`}
            variants={variants}
            initial="initial"
            animate="animate"
            exit="exit"
            whileHover={{ scale: 1.1 }}
          >
            <svg className="w-5 h-5 text-white" viewBox="0 0 20 20" fill="currentColor">
              <path
                fillRule="evenodd"
                d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"
                clipRule="evenodd"
              />
            </svg>
          </motion.div>
        )
      case 'error':
        return (
          <motion.div
            className={`${baseClasses} bg-red-500`}
            variants={variants}
            initial="initial"
            animate="animate"
            exit="exit"
            whileHover={{ scale: 1.1 }}
          >
            <svg className="w-5 h-5 text-white" viewBox="0 0 20 20" fill="currentColor">
              <path
                fillRule="evenodd"
                d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z"
                clipRule="evenodd"
              />
            </svg>
          </motion.div>
        )
      default:
        return null
    }
  }

  return (
    <div className="w-full max-w-4xl mx-auto bg-white rounded-xl shadow-lg p-6 my-4">
      {/* Header with file info and overall progress */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h3 className="text-xl font-semibold text-gray-900">
            Processando: {fileName}
          </h3>
          <p className="text-sm text-gray-500 mt-1">
            {processingComplete ? 'Concluído' : 'Em andamento...'}
          </p>
        </div>
        <div className="text-right">
          <div className="text-2xl font-bold text-blue-600">
            {Math.round(animatedProgress)}%
          </div>
          <div className="text-sm text-gray-500">Progresso total</div>
        </div>
      </div>

      {/* Metrics Dashboard */}
      <div className="grid grid-cols-4 gap-4 mb-6">
        <motion.div
          className="bg-blue-50 p-4 rounded-lg"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
        >
          <div className="text-sm text-blue-600 font-medium">Tempo Decorrido</div>
          <div className="text-2xl font-semibold">{formatTime(metrics.elapsedTime)}</div>
        </motion.div>

        <motion.div
          className="bg-green-50 p-4 rounded-lg"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
        >
          <div className="text-sm text-green-600 font-medium">Tempo Restante</div>
          <div className="text-2xl font-semibold">
            {formatTime(metrics.estimatedTimeRemaining)}
          </div>
        </motion.div>

        <motion.div
          className="bg-purple-50 p-4 rounded-lg"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
        >
          <div className="text-sm text-purple-600 font-medium">Velocidade</div>
          <div className="text-2xl font-semibold">
            {metrics.processingSpeed.toFixed(1)}x
          </div>
        </motion.div>

        <motion.div
          className="bg-yellow-50 p-4 rounded-lg"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
        >
          <div className="text-sm text-yellow-600 font-medium">Taxa de Sucesso</div>
          <div className="text-2xl font-semibold">
            {Math.round(metrics.successRate)}%
          </div>
        </motion.div>
      </div>

      {/* Progress bar */}
      <div className="relative w-full h-3 bg-gray-200 rounded-full overflow-hidden mb-8">
        <motion.div
          className="absolute top-0 left-0 h-full bg-gradient-to-r from-blue-500 to-blue-600"
          style={{ width: `${animatedProgress}%` }}
          initial={{ x: '-100%' }}
          animate={{ x: 0 }}
          transition={{ type: 'spring', stiffness: 50, damping: 20 }}
        />
      </div>

      {/* Initialization steps */}
      <div className="space-y-6 mb-8">
        <AnimatePresence>
          {steps.filter(step => step.isInitStep).map((step) => (
            <motion.div
              key={step.id}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: 20 }}
              className={`flex items-start p-3 rounded-lg ${
                step.status === 'initializing' ? 'bg-indigo-50 border border-indigo-100' :
                step.status === 'success' ? 'bg-green-50 border border-green-100' :
                'bg-gray-50 border border-gray-100'
              }`}
            >
              <div className="flex-shrink-0">
                {step.status === 'initializing' ? (
                  <motion.div
                    animate={{ rotate: 360 }}
                    transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
                    className="w-5 h-5 text-indigo-600"
                  >
                    <svg xmlns="http://www.w3.org/2000/svg" className="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                    </svg>
                  </motion.div>
                ) : (
                  <div className="w-5 h-5 text-green-600">
                    <svg xmlns="http://www.w3.org/2000/svg" className="w-5 h-5" viewBox="0 0 20 20" fill="currentColor">
                      <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                    </svg>
                  </div>
                )}
              </div>
              <div className="ml-3">
                <p className="text-sm font-medium text-gray-900">{step.description}</p>
              </div>
            </motion.div>
          ))}
        </AnimatePresence>
      </div>

      {/* AI/NLP Tech Details Toggle */}
      <div className="mb-6">
        <button
          onClick={() => setShowTechDetails(!showTechDetails)}
          className="flex items-center space-x-2 text-sm text-gray-600 hover:text-gray-900 transition-colors"
        >
          <Brain className="w-4 h-4" />
          <span>{showTechDetails ? 'Ocultar' : 'Mostrar'} detalhes técnicos</span>
          <motion.div
            animate={{ rotate: showTechDetails ? 90 : 0 }}
            transition={{ duration: 0.2 }}
          >
            <ChevronRight className="w-4 h-4" />
          </motion.div>
        </button>
      </div>

      {/* Tech Details Panel */}
      <AnimatePresence>
        {showTechDetails && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            className="mb-6 overflow-hidden"
          >
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 p-4 bg-gray-50 rounded-lg border border-gray-200">
              <div className="flex items-center space-x-3">
                <Cpu className="w-5 h-5 text-purple-500" />
                <div>
                  <div className="text-sm font-medium text-gray-900">Velocidade de Processamento</div>
                  <div className="text-sm text-gray-500">{metrics.processingSpeed.toFixed(1)} blocos/s</div>
                </div>
              </div>
              <div className="flex items-center space-x-3">
                <FileText className="w-5 h-5 text-blue-500" />
                <div>
                  <div className="text-sm font-medium text-gray-900">Taxa de Sucesso</div>
                  <div className="text-sm text-gray-500">{metrics.successRate.toFixed(1)}%</div>
                </div>
              </div>
              <div className="flex items-center space-x-3">
                <Database className="w-5 h-5 text-green-500" />
                <div>
                  <div className="text-sm font-medium text-gray-900">Tempo Estimado Restante</div>
                  <div className="text-sm text-gray-500">{formatTime(metrics.estimatedTimeRemaining)}</div>
                </div>
              </div>
              <div className="flex items-center space-x-3">
                <Brain className="w-5 h-5 text-indigo-500" />
                <div>
                  <div className="text-sm font-medium text-gray-900">Modelos em Uso</div>
                  <div className="text-sm text-gray-500">Spacy, BERT, YAKE, FAISS</div>
                </div>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Processing steps list with animations */}
      <div className="space-y-4">
        <AnimatePresence>
          {steps.filter(step => !step.isInitStep).map((step) => (
            <motion.div
              key={step.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
            >
              <ProcessingStepCard
                name={step.name}
                description={step.description}
                status={step.status}
                percentageOfTotal={step.percentageOfTotal}
                isCurrentStep={step.id === currentStepId}
              />
            </motion.div>
          ))}
        </AnimatePresence>
      </div>

      {/* Completion summary */}
      <AnimatePresence>
        {processingComplete && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            className={`mt-8 p-4 rounded-lg ${
              steps.some(s => s.status === 'error')
                ? 'bg-red-50 border border-red-200'
                : 'bg-green-50 border border-green-200'
            }`}
          >
            <div className="flex items-center justify-between">
              <div>
                <h4 className={`text-lg font-semibold ${
                  steps.some(s => s.status === 'error')
                    ? 'text-red-700'
                    : 'text-green-700'
                }`}>
                  {steps.some(s => s.status === 'error')
                    ? 'Processamento concluído com erros'
                    : 'Processamento concluído com sucesso'}
                </h4>
                <p className="text-sm mt-1 text-gray-600">
                  {steps.filter(s => s.status === 'success').length} de {steps.length} etapas concluídas com sucesso
                </p>
              </div>
              <div className="text-right">
                <div className="text-3xl font-bold text-gray-900">
                  {formatTime(metrics.elapsedTime)}
                </div>
                <div className="text-sm text-gray-500">Tempo total</div>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}
