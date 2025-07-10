import React from 'react'
import { Card } from './Card'

interface ProposalPreviewProps {
  proposal: {
    client_name: string
    industry: string
    requirements: string
    scope: string
    timeline: string
    budget: string
  }
}

export function ProposalPreview({ proposal }: ProposalPreviewProps) {
  return (
    <Card className="prose max-w-none">
      <div className="text-center mb-8">
        <h1 className="text-3xl font-bold text-gray-900">
          Proposta Comercial
        </h1>
        <p className="text-xl text-gray-600 mt-2">
          {proposal.client_name}
        </p>
      </div>

      <div className="space-y-6">
        <section>
          <h2 className="text-2xl font-semibold text-gray-900">
            Informações Gerais
          </h2>
          <div className="mt-4 grid grid-cols-2 gap-4">
            <div>
              <p className="font-medium text-gray-700">Cliente:</p>
              <p className="text-gray-600">{proposal.client_name}</p>
            </div>
            <div>
              <p className="font-medium text-gray-700">Setor:</p>
              <p className="text-gray-600">{proposal.industry}</p>
            </div>
          </div>
        </section>

        <section>
          <h2 className="text-2xl font-semibold text-gray-900">
            Requisitos do Projeto
          </h2>
          <p className="mt-4 text-gray-600 whitespace-pre-wrap">
            {proposal.requirements}
          </p>
        </section>

        <section>
          <h2 className="text-2xl font-semibold text-gray-900">
            Escopo
          </h2>
          <p className="mt-4 text-gray-600 whitespace-pre-wrap">
            {proposal.scope}
          </p>
        </section>

        <section>
          <h2 className="text-2xl font-semibold text-gray-900">
            Cronograma e Investimento
          </h2>
          <div className="mt-4 grid grid-cols-2 gap-4">
            <div>
              <p className="font-medium text-gray-700">Prazo Estimado:</p>
              <p className="text-gray-600">{proposal.timeline}</p>
            </div>
            <div>
              <p className="font-medium text-gray-700">Investimento:</p>
              <p className="text-gray-600">{proposal.budget}</p>
            </div>
          </div>
        </section>
      </div>
    </Card>
  )
}
