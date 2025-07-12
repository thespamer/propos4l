'use client'

import React from 'react'
import { useEffect, useState } from 'react'

type ProcessStep = {
  id: string
  name: string
  description: string
  percentageOfTotal: number // What percentage of the total process this step represents
  status: 'waiting' | 'processing' | 'success' | 'error' | 'skipped'
  details?: string
}

type ProcessingProgressProps = {
  steps: ProcessStep[]
  currentStepId: string | null
  overallProgress: number // 0-100
  onComplete?: () => void
  processingComplete: boolean
  fileName: string
}

export default function ProcessingProgress({
  steps,
  currentStepId,
  overallProgress,
  onComplete,
  processingComplete,
  fileName
}: ProcessingProgressProps) {
  const [animatedProgress, setAnimatedProgress] = useState(0)

  // Animate progress bar
  useEffect(() => {
    const animationDuration = 300 // ms
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

  // Call onComplete when processing is done
  useEffect(() => {
    if (processingComplete && onComplete) {
      onComplete()
    }
  }, [processingComplete, onComplete])

  const getStepIcon = (step: ProcessStep) => {
    switch (step.status) {
      case 'waiting':
        return (
          <div className="w-6 h-6 rounded-full border-2 border-gray-300 flex items-center justify-center">
            <span className="text-xs text-gray-500">{steps.findIndex(s => s.id === step.id) + 1}</span>
          </div>
        )
      case 'processing':
        return (
          <div className="w-6 h-6 rounded-full bg-blue-500 flex items-center justify-center animate-pulse">
            <svg className="w-4 h-4 text-white animate-spin" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
          </div>
        )
      case 'success':
        return (
          <div className="w-6 h-6 rounded-full bg-green-500 flex items-center justify-center">
            <svg className="w-4 h-4 text-white" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
              <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
            </svg>
          </div>
        )
      case 'error':
        return (
          <div className="w-6 h-6 rounded-full bg-red-500 flex items-center justify-center">
            <svg className="w-4 h-4 text-white" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
              <path fillRule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clipRule="evenodd" />
            </svg>
          </div>
        )
      case 'skipped':
        return (
          <div className="w-6 h-6 rounded-full bg-gray-400 flex items-center justify-center">
            <svg className="w-4 h-4 text-white" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
              <path fillRule="evenodd" d="M10.293 3.293a1 1 0 011.414 0l6 6a1 1 0 010 1.414l-6 6a1 1 0 01-1.414-1.414L14.586 11H3a1 1 0 110-2h11.586l-4.293-4.293a1 1 0 010-1.414z" clipRule="evenodd" />
            </svg>
          </div>
        )
      default:
        return (
          <div className="w-6 h-6 rounded-full border-2 border-gray-300 flex items-center justify-center">
            <span className="text-xs text-gray-500">{steps.findIndex(s => s.id === step.id) + 1}</span>
          </div>
        )
    }
  }

  return (
    <div className="w-full max-w-3xl mx-auto bg-white rounded-lg shadow-md p-6 my-4">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-medium text-gray-900">Processando: {fileName}</h3>
        <span className="text-sm font-medium text-gray-700">{Math.round(animatedProgress)}%</span>
      </div>
      
      {/* Overall progress bar */}
      <div className="w-full bg-gray-200 rounded-full h-2.5 mb-6">
        <div 
          className="bg-blue-600 h-2.5 rounded-full transition-all duration-300" 
          style={{ width: `${animatedProgress}%` }}
        ></div>
      </div>
      
      {/* Steps list */}
      <div className="space-y-4">
        {steps.map((step) => (
          <div key={step.id} className="flex items-start">
            <div className="flex-shrink-0 mt-1">
              {getStepIcon(step)}
            </div>
            <div className="ml-3 flex-1">
              <div className="flex items-center justify-between">
                <h4 className={`text-sm font-medium ${
                  step.status === 'processing' ? 'text-blue-700' :
                  step.status === 'success' ? 'text-green-700' :
                  step.status === 'error' ? 'text-red-700' :
                  step.status === 'skipped' ? 'text-gray-500' :
                  'text-gray-700'
                }`}>
                  {step.name}
                </h4>
                <span className="text-xs text-gray-500">{step.percentageOfTotal}%</span>
              </div>
              <p className="text-xs text-gray-500 mt-1">{step.description}</p>
              
              {step.details && (
                <div className="mt-1 text-xs bg-gray-50 p-2 rounded border border-gray-200">
                  {step.details}
                </div>
              )}
            </div>
          </div>
        ))}
      </div>
      
      {/* Summary when complete */}
      {processingComplete && (
        <div className={`mt-6 p-3 rounded-md ${
          steps.some(s => s.status === 'error') ? 'bg-red-50 border border-red-200' : 'bg-green-50 border border-green-200'
        }`}>
          <p className={`text-sm font-medium ${
            steps.some(s => s.status === 'error') ? 'text-red-700' : 'text-green-700'
          }`}>
            {steps.some(s => s.status === 'error') 
              ? 'Processamento concluído com erros' 
              : 'Processamento concluído com sucesso'}
          </p>
          <p className="text-xs mt-1 text-gray-600">
            {steps.filter(s => s.status === 'success').length} de {steps.length} etapas concluídas com sucesso
          </p>
        </div>
      )}
    </div>
  )
}
