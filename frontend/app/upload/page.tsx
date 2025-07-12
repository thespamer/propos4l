'use client'

import { useState, useCallback } from 'react'
import { useRouter } from 'next/navigation'
import { useToast } from '../contexts/ToastContext'
import { useLoading } from '../contexts/LoadingContext'

export default function Upload() {
  const router = useRouter()
  const { showToast } = useToast()
  const { isLoading, withLoading } = useLoading()
  const [files, setFiles] = useState<File[]>([])
  const [metadata, setMetadata] = useState({
    client_name: '',
    industry: '',
    date: new Date().toISOString().split('T')[0]
  })
  const [uploading, setUploading] = useState(false)
  const [uploadProgress, setUploadProgress] = useState(0)
  const [error, setError] = useState('')

  const handleFileChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      const fileList = Array.from(e.target.files)
      setFiles(fileList)
    }
  }, [])

  const handleRemoveFile = useCallback((index: number) => {
    setFiles(prev => prev.filter((_, i) => i !== index))
  }, [])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (files.length === 0) {
      setError('Por favor, selecione pelo menos um arquivo PDF')
      return
    }

    setUploading(true)
    setError('')
    setUploadProgress(0)

    const formData = new FormData()
    
    // Append all files
    files.forEach((file, index) => {
      formData.append(`files`, file)
    })
    
    // Append metadata fields individually
    formData.append('client_name', metadata.client_name)
    formData.append('industry', metadata.industry)

    try {
      const uploadPromise = async () => {
        const response = await fetch('/api/upload-proposal', {
          method: 'POST',
          body: formData,
        })

        if (!response.ok) {
          throw new Error('Erro ao fazer upload das propostas')
        }

        const result = await response.json()
        showToast(`${result.message}`, 'success')
        return result
      }
      
      const result = await withLoading(uploadPromise())
      
      // Redirecionar para a página de status de processamento se houver tracking_ids
      if (result.tracking_ids && result.tracking_ids.length > 0) {
        if (result.tracking_ids.length === 1) {
          // Se for apenas um arquivo, redirecionar para a página de status desse arquivo
          router.push(`/processing-status?id=${result.tracking_ids[0]}`)
        } else {
          // Se forem múltiplos arquivos, redirecionar para o primeiro e mostrar mensagem
          router.push(`/processing-status?id=${result.tracking_ids[0]}`)
          showToast(`Processando ${result.tracking_ids.length} arquivos. Você pode acompanhar cada um individualmente.`, 'success')
        }
      } else {
        // Fallback para a página de histórico se não houver tracking_ids
        router.push('/history')
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erro ao processar propostas')
      showToast(err instanceof Error ? err.message : 'Erro ao processar propostas', 'error')
    } finally {
      setUploading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-2xl mx-auto">
        <h1 className="text-3xl font-bold text-gray-900 mb-8">
          Upload de Proposta
        </h1>

        <form onSubmit={handleSubmit} className="space-y-6 bg-white p-6 rounded-lg shadow">
          {/* File Upload - Multiple Files */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Arquivos de Proposta (PDF) - Upload em Massa
            </label>
            <input
              type="file"
              accept=".pdf"
              multiple
              onChange={handleFileChange}
              className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
            />
            
            {/* Selected Files List */}
            {files.length > 0 && (
              <div className="mt-3">
                <h4 className="text-sm font-medium text-gray-700 mb-2">
                  {files.length} arquivo(s) selecionado(s):
                </h4>
                <ul className="max-h-40 overflow-y-auto border border-gray-200 rounded-md divide-y">
                  {files.map((file, index) => (
                    <li key={index} className="px-3 py-2 flex justify-between items-center text-sm">
                      <span className="truncate">{file.name}</span>
                      <button 
                        type="button" 
                        onClick={() => handleRemoveFile(index)}
                        className="ml-2 text-red-500 hover:text-red-700"
                      >
                        Remover
                      </button>
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>

          {/* Client Name */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Nome do Cliente
            </label>
            <input
              type="text"
              value={metadata.client_name}
              onChange={(e) => setMetadata({ ...metadata, client_name: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
              required
            />
          </div>

          {/* Industry */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Setor/Indústria
            </label>
            <input
              type="text"
              value={metadata.industry}
              onChange={(e) => setMetadata({ ...metadata, industry: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
              required
            />
          </div>

          {/* Date */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Data
            </label>
            <input
              type="date"
              value={metadata.date}
              onChange={(e) => setMetadata({ ...metadata, date: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
              required
            />
          </div>

          {error && (
            <div className="text-red-600 text-sm">
              {error}
            </div>
          )}

          {/* Upload Progress */}
          {uploading && (
            <div className="w-full">
              <div className="w-full bg-gray-200 rounded-full h-2.5">
                <div 
                  className="bg-indigo-600 h-2.5 rounded-full transition-all duration-300" 
                  style={{ width: `${uploadProgress}%` }}
                ></div>
              </div>
              <p className="text-xs text-gray-500 mt-1 text-center">
                {uploadProgress}% concluído
              </p>
            </div>
          )}

          <button
            type="submit"
            disabled={uploading}
            className={`w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 ${uploading ? 'opacity-50 cursor-not-allowed' : ''}`}
          >
            {uploading ? 'Processando...' : `Enviar ${files.length} Proposta(s)`}
          </button>
        </form>
      </div>
    </div>
  )
}
