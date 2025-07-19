'use client'

import React from 'react'
import { useSearchParams } from 'next/navigation'
import EnhancedProcessingProgress from '../components/EnhancedProcessingProgress'
import { useProcessingStatus } from '../hooks/useProcessingStatus'
import Link from 'next/link'
import { motion, AnimatePresence } from 'framer-motion'

export default function ProcessingStatusPage() {
  const searchParams = useSearchParams()
  const trackerId = searchParams.get('id')
  const { status, error, isConnected } = useProcessingStatus(trackerId)
  
  if (!trackerId) {
    return (
      <motion.div 
      className="container mx-auto px-4 py-8"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
    >
      <motion.div 
        className="bg-yellow-50 border-l-4 border-yellow-400 p-4 mb-6"
        initial={{ x: -50 }}
        animate={{ x: 0 }}
        transition={{ type: 'spring', stiffness: 100 }}
      >
        <div className="flex">
          <div className="flex-shrink-0">
            <motion.svg 
              className="h-5 w-5 text-yellow-400" 
              xmlns="http://www.w3.org/2000/svg" 
              viewBox="0 0 20 20" 
              fill="currentColor"
              animate={{ rotate: [0, 10, -10, 0] }}
              transition={{ duration: 0.5, repeat: Infinity, repeatDelay: 3 }}
            >
              <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
            </motion.svg>
          </div>
          <div className="ml-3">
            <p className="text-sm text-yellow-700">
              Nenhum ID de processamento fornecido. Por favor, inicie um upload para visualizar o progresso.
            </p>
          </div>
        </div>
      </motion.div>
      <motion.div
        whileHover={{ scale: 1.05 }}
        whileTap={{ scale: 0.95 }}
      >
        <Link href="/upload" className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500">
          Ir para página de upload
        </Link>
      </motion.div>
    </motion.div>
    )
  }

  if (error) {
    return (
      <motion.div 
      className="container mx-auto px-4 py-8"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
    >
      <motion.div 
        className="bg-red-50 border-l-4 border-red-400 p-4 mb-6"
        initial={{ x: -50 }}
        animate={{ x: 0 }}
        transition={{ type: 'spring', stiffness: 100 }}
      >
        <div className="flex">
          <div className="flex-shrink-0">
            <motion.svg 
              className="h-5 w-5 text-red-400" 
              xmlns="http://www.w3.org/2000/svg" 
              viewBox="0 0 20 20" 
              fill="currentColor"
              animate={{ scale: [1, 1.2, 1] }}
              transition={{ duration: 0.5, repeat: Infinity }}
            >
              <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
            </motion.svg>
          </div>
          <div className="ml-3">
            <p className="text-sm text-red-700">
              Erro ao carregar status de processamento: {error}
            </p>
          </div>
        </div>
      </motion.div>
      <motion.div
        whileHover={{ scale: 1.05 }}
        whileTap={{ scale: 0.95 }}
      >
        <Link href="/upload" className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500">
          Voltar para upload
        </Link>
      </motion.div>
    </motion.div>
    )
  }

  if (!status) {
    return (
      <motion.div 
      className="container mx-auto px-4 py-8"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
    >
      <div className="flex flex-col justify-center items-center h-64 space-y-8">
        <motion.div 
          className="relative w-32 h-32"
          animate={{ rotate: 360 }}
          transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
        >
          <div className="absolute top-0 left-0 w-full h-full border-8 border-blue-200 rounded-full"></div>
          <div className="absolute top-0 left-0 w-full h-full border-t-8 border-blue-500 rounded-full"></div>
        </motion.div>
        <motion.p 
          className="text-center text-gray-600 text-lg"
          initial={{ y: 20, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ delay: 0.2 }}
        >
          Carregando informações de processamento...
        </motion.p>
        <motion.div 
          className="text-center mt-4"
          initial={{ y: 20, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ delay: 0.4 }}
        >
          <motion.span 
            className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium ${
              isConnected ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'
            }`}
            animate={{
              scale: isConnected ? [1, 1.05, 1] : [1, 1.1, 1],
              opacity: isConnected ? 1 : [0.7, 1, 0.7]
            }}
            transition={{ duration: 2, repeat: Infinity }}
          >
            {isConnected ? (
              <>
                <motion.div
                  className="w-2 h-2 bg-green-500 rounded-full mr-2"
                  animate={{ scale: [1, 1.2, 1] }}
                  transition={{ duration: 1, repeat: Infinity }}
                />
                Conectado
              </>
            ) : (
              <>
                <motion.div
                  className="w-2 h-2 bg-yellow-500 rounded-full mr-2"
                  animate={{ opacity: [0, 1, 0] }}
                  transition={{ duration: 1.5, repeat: Infinity }}
                />
                Conectando...
              </>
            )}
          </motion.span>
        </motion.div>
      </div>
    </motion.div>
    )
  }

  return (
    <motion.div 
      className="container mx-auto px-4 py-8"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
    >
      <motion.h1 
        className="text-3xl font-bold text-gray-900 mb-8"
        initial={{ opacity: 0, x: -20 }}
        animate={{ opacity: 1, x: 0 }}
        transition={{ delay: 0.2 }}
      >
        Status de Processamento
      </motion.h1>
      
      <AnimatePresence mode="wait">
        <EnhancedProcessingProgress
          key={status.id}
          steps={status.steps}
          currentStepId={status.currentStepId}
          overallProgress={status.overallProgress}
          processingComplete={status.isComplete}
          fileName={status.fileName}
          onComplete={() => console.log('Processamento concluído')}
        />
      </AnimatePresence>
      
      <motion.div 
        className="mt-8 flex justify-between"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.4 }}
      >
        <motion.div whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}>
          <Link 
            href="/upload" 
            className="inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md shadow-sm text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
          >
            Voltar para upload
          </Link>
        </motion.div>
        
        <AnimatePresence>
          {status.isComplete && (
            <motion.div
              initial={{ opacity: 0, scale: 0.8 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.8 }}
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
            >
              <Link 
                href={`/history?highlight=${status.id}`} 
                className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
              >
                Ver no histórico
              </Link>
            </motion.div>
          )}
        </AnimatePresence>
      </motion.div>
    </motion.div>
  )
}
