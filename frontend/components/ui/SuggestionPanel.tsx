'use client'

import React from 'react'
import { Card } from './Card'

interface Suggestion {
  description: string
  reasoning: string
  example: string
}

interface SectionSuggestion {
  section: string
  frequency: number
  value: string
  reason: string
}

interface SuggestionPanelProps {
  contentSuggestions: Record<string, Array<Suggestion>>
  sectionSuggestions: Array<SectionSuggestion>
  onApplySuggestion: (section: string, content: string) => void
  onAddSection: (section: SectionSuggestion) => void
}

export function SuggestionPanel({
  contentSuggestions,
  sectionSuggestions,
  onApplySuggestion,
  onAddSection
}: SuggestionPanelProps) {
  return (
    <div className="space-y-6">
      <h3 className="text-lg font-semibold text-gray-900">
        Sugestões de Melhoria
      </h3>

      {/* Content Suggestions */}
      {Object.entries(contentSuggestions).map(([section, suggestions]) => (
        <Card key={section} className="p-4">
          <h4 className="text-md font-medium text-gray-900 mb-3">
            Sugestões para {section}
          </h4>
          <div className="space-y-4">
            {suggestions.map((suggestion, idx) => (
              <div key={idx} className="border-l-4 border-indigo-500 pl-4">
                <p className="text-gray-700 mb-2">{suggestion.description}</p>
                <p className="text-sm text-gray-500 mb-2">
                  <strong>Por quê?</strong> {suggestion.reasoning}
                </p>
                <div className="bg-gray-50 p-2 rounded text-sm mb-2">
                  <strong>Exemplo:</strong> {suggestion.example}
                </div>
                <button
                  onClick={() => onApplySuggestion(section, suggestion.example)}
                  className="text-sm text-indigo-600 hover:text-indigo-800"
                >
                  Aplicar Sugestão
                </button>
              </div>
            ))}
          </div>
        </Card>
      ))}

      {/* Section Suggestions */}
      {sectionSuggestions.length > 0 && (
        <Card className="p-4">
          <h4 className="text-md font-medium text-gray-900 mb-3">
            Seções Recomendadas
          </h4>
          <div className="space-y-4">
            {sectionSuggestions.map((suggestion, idx) => (
              <div key={idx} className="border-l-4 border-green-500 pl-4">
                <div className="flex items-center justify-between mb-2">
                  <h5 className="font-medium text-gray-900">{suggestion.section}</h5>
                  <span className="text-sm text-gray-500">
                    Presente em {suggestion.frequency}% das propostas similares
                  </span>
                </div>
                <p className="text-gray-700 mb-2">{suggestion.reason}</p>
                <button
                  onClick={() => onAddSection(suggestion)}
                  className="text-sm text-green-600 hover:text-green-800"
                >
                  Adicionar Seção
                </button>
              </div>
            ))}
          </div>
        </Card>
      )}
    </div>
  )
}
