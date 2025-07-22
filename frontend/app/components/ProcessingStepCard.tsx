'use client'

import React from 'react'
import { CheckCircle, Circle, AlertCircle, Clock, Play, Brain, Cpu, FileText, Database } from 'lucide-react'
import { motion, HTMLMotionProps } from 'framer-motion'

interface TechDetail {
  icon: React.ReactNode
  label: string
  value: string
}

interface ProcessingStepProps {
  name: string
  description: string
  status: string
  percentageOfTotal: number
  isCurrentStep: boolean
}

export default function ProcessingStepCard({
  name,
  description,
  status,
  percentageOfTotal,
  isCurrentStep,
}: ProcessingStepProps) {
  const getStatusIcon = () => {
    switch (status) {
      case 'success':
        return <CheckCircle className="w-6 h-6 text-green-500" />
      case 'error':
        return <AlertCircle className="w-6 h-6 text-red-500" />
      case 'processing':
        return (
          <div className="relative">
            <Circle className="w-6 h-6 text-blue-500" />
            <div className="absolute inset-0 flex items-center justify-center">
              <div className="w-3 h-3 border-2 border-blue-500 border-t-transparent rounded-full animate-spin"></div>
            </div>
          </div>
        )
      case 'waiting':
        return <Clock className="w-6 h-6 text-gray-400" />
      case 'skipped':
        return <Play className="w-6 h-6 text-yellow-500" />
      default:
        return <Circle className="w-6 h-6 text-gray-400" />
    }
  }

  const getStatusClass = () => {
    switch (status) {
      case 'success':
        return 'bg-green-50 border-green-200'
      case 'error':
        return 'bg-red-50 border-red-200'
      case 'processing':
        return 'bg-blue-50 border-blue-200'
      case 'skipped':
        return 'bg-yellow-50 border-yellow-200'
      default:
        return 'bg-gray-50 border-gray-200'
    }
  }

  const getTechDetails = (): TechDetail[] => {
    // Example tech details based on step name/description
    if (name.toLowerCase().includes('ocr')) {
      return [
        {
          icon: <Brain className="w-4 h-4 text-purple-500" />,
          label: 'Engine',
          value: 'Tesseract OCR',
        },
        {
          icon: <Cpu className="w-4 h-4 text-blue-500" />,
          label: 'Mode',
          value: 'LSTM Neural Net',
        },
      ]
    }
    if (name.toLowerCase().includes('spacy')) {
      return [
        {
          icon: <Brain className="w-4 h-4 text-green-500" />,
          label: 'Model',
          value: 'pt_core_news_lg',
        },
        {
          icon: <Database className="w-4 h-4 text-blue-500" />,
          label: 'Pipeline',
          value: 'NER + Deps',
        },
      ]
    }
    if (name.toLowerCase().includes('embedding')) {
      return [
        {
          icon: <Brain className="w-4 h-4 text-indigo-500" />,
          label: 'Model',
          value: 'BERT Base',
        },
        {
          icon: <Cpu className="w-4 h-4 text-purple-500" />,
          label: 'Dim',
          value: '768',
        },
      ]
    }
    return []
  }

  return (
    <motion.div
      layout
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      className={`relative p-4 mb-2 border rounded-lg ${getStatusClass()} ${
        isCurrentStep ? 'scale-105 shadow-md' : ''
      }`}
    >
      <div className="flex items-start space-x-4">
        <div className="flex-shrink-0 mt-1">{getStatusIcon()}</div>
        <div className="flex-grow">
          <h3 className="text-lg font-semibold text-gray-800">{name}</h3>
          <p className="text-sm text-gray-600">{description}</p>
          {status === 'processing' && (
            <div className="mt-2 space-y-2">
              <div className="h-1.5 w-full bg-blue-100 rounded-full overflow-hidden">
                <motion.div
                  className="h-full bg-blue-500 rounded-full"
                  initial={{ width: '0%' }}
                  animate={{
                    width: `${percentageOfTotal}%`,
                  }}
                  transition={{
                    duration: 1,
                    ease: 'easeInOut',
                  }}
                />
              </div>
              {getTechDetails().length > 0 && (
                <div className="grid grid-cols-2 gap-2 text-xs">
                  {getTechDetails().map((detail, index) => (
                    <div key={index} className="flex items-center space-x-1.5">
                      {detail.icon}
                      <span className="text-gray-500">{detail.label}:</span>
                      <span className="font-medium text-gray-700">{detail.value}</span>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}
        </div>
        <div className="flex-shrink-0 text-sm font-medium text-gray-500">
          {percentageOfTotal}%
        </div>
      </div>
    </motion.div>
  )
}
