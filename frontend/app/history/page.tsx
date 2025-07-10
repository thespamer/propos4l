'use client'

import { useEffect, useState } from 'react'

interface Proposal {
  filename: string
  client_name: string
  industry: string
  date: string
  similarity_score?: number
  pdf_url?: string
}

export default function History() {
  const [proposals, setProposals] = useState<Proposal[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    const fetchProposals = async () => {
      try {
        const response = await fetch('http://localhost:8000/')
        if (!response.ok) {
          throw new Error('Erro ao carregar propostas')
        }
        const data = await response.json()
        // TODO: Implement proper history endpoint
        // This is just a placeholder until we implement the history endpoint
        setProposals([])
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Erro ao carregar propostas')
      } finally {
        setLoading(false)
      }
    }

    fetchProposals()
  }, [])

  const downloadProposal = (url: string) => {
    window.open(`http://localhost:8000${url}`, '_blank')
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
          <div className="text-center">
            <p className="text-lg text-gray-600">Carregando propostas...</p>
          </div>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
          <div className="text-center text-red-600">
            <p>{error}</p>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-7xl mx-auto">
        <h1 className="text-3xl font-bold text-gray-900 mb-8">
          Histórico de Propostas
        </h1>

        {proposals.length === 0 ? (
          <div className="text-center text-gray-600">
            <p>Nenhuma proposta encontrada.</p>
          </div>
        ) : (
          <div className="bg-white shadow overflow-hidden sm:rounded-md">
            <ul className="divide-y divide-gray-200">
              {proposals.map((proposal, index) => (
                <li key={index}>
                  <div className="px-4 py-4 sm:px-6 hover:bg-gray-50">
                    <div className="flex items-center justify-between">
                      <div className="flex-1">
                        <h3 className="text-lg font-medium text-indigo-600 truncate">
                          {proposal.client_name}
                        </h3>
                        <div className="mt-2 flex flex-col sm:flex-row sm:flex-wrap sm:space-x-6">
                          <div className="mt-2 flex items-center text-sm text-gray-500">
                            <span className="font-medium">Indústria:</span>
                            <span className="ml-2">{proposal.industry}</span>
                          </div>
                          <div className="mt-2 flex items-center text-sm text-gray-500">
                            <span className="font-medium">Data:</span>
                            <span className="ml-2">{proposal.date}</span>
                          </div>
                          {proposal.similarity_score && (
                            <div className="mt-2 flex items-center text-sm text-gray-500">
                              <span className="font-medium">Relevância:</span>
                              <span className="ml-2">
                                {Math.round(proposal.similarity_score * 100)}%
                              </span>
                            </div>
                          )}
                        </div>
                      </div>
                      {proposal.pdf_url && (
                        <div className="ml-4">
                          <button
                            onClick={() => downloadProposal(proposal.pdf_url!)}
                            className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
                          >
                            Download
                          </button>
                        </div>
                      )}
                    </div>
                  </div>
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>
    </div>
  )
}
