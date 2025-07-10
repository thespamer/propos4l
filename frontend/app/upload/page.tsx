'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'

export default function Upload() {
  const router = useRouter()
  const [file, setFile] = useState<File | null>(null)
  const [metadata, setMetadata] = useState({
    client_name: '',
    industry: '',
    date: new Date().toISOString().split('T')[0]
  })
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!file) {
      setError('Por favor, selecione um arquivo PDF')
      return
    }

    setLoading(true)
    setError('')

    const formData = new FormData()
    formData.append('file', file)
    formData.append('metadata', JSON.stringify(metadata))

    try {
      const response = await fetch('http://localhost:8000/upload-proposal', {
        method: 'POST',
        body: formData,
      })

      if (!response.ok) {
        throw new Error('Erro ao fazer upload da proposta')
      }

      const result = await response.json()
      router.push('/history')
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erro ao processar proposta')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-2xl mx-auto">
        <h1 className="text-3xl font-bold text-gray-900 mb-8">
          Upload de Proposta
        </h1>

        <form onSubmit={handleSubmit} className="space-y-6 bg-white p-6 rounded-lg shadow">
          {/* File Upload */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Arquivo da Proposta (PDF)
            </label>
            <input
              type="file"
              accept=".pdf"
              onChange={(e) => setFile(e.target.files?.[0] || null)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
            />
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

          <button
            type="submit"
            disabled={loading}
            className={`w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 ${loading ? 'opacity-50 cursor-not-allowed' : ''}`}
          >
            {loading ? 'Processando...' : 'Enviar Proposta'}
          </button>
        </form>
      </div>
    </div>
  )
}
