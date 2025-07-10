'use client'

import React, { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { FormInput, Button, ProposalPreview, SuggestionPanel } from '../../components/ui'
import { useToast } from '../contexts/ToastContext'
import { useLoading } from '../contexts/LoadingContext'
import { debounce } from 'lodash'

interface ProposalForm {
  client_name: string
  industry: string
  requirements: string
  scope: string
  timeline: string
  budget: string
  [key: string]: string  // Allow dynamic section additions
}

interface ProposalSuggestions {
  content_suggestions: Record<string, Array<{
    description: string
    reasoning: string
    example: string
  }>>
  section_suggestions: Array<{
    section: string
    frequency: number
    value: string
    reason: string
  }>
  overall_quality: {
    completeness: number
    sections_with_suggestions: number
    missing_critical_sections: string[]
  }
}

export default function Generate() {
  const router = useRouter()
  const { showToast } = useToast()
  const { withLoading } = useLoading()
  const [showPreview, setShowPreview] = useState(false)
  const [formData, setFormData] = useState<ProposalForm>({
    client_name: '',
    industry: '',
    requirements: '',
    scope: '',
    timeline: '',
    budget: ''
  })
  const [suggestions, setSuggestions] = useState<ProposalSuggestions | null>(null)
  const [isGenerating, setIsGenerating] = useState(false)

  // Get suggestions when form data changes
  useEffect(() => {
    const getSuggestions = async () => {
      if (!formData.client_name || !formData.industry) return
      
      try {
        const response = await fetch('http://localhost:8000/smart-suggestions', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(formData)
        })
        
        if (response.ok) {
          const data = await response.json()
          setSuggestions(data)
        }
      } catch (err) {
        console.error('Error fetching suggestions:', err)
      }
    }
    
    const debouncedGetSuggestions = debounce(getSuggestions, 500)
    debouncedGetSuggestions()
    
    return () => {
      debouncedGetSuggestions.cancel()
    }
  }, [formData])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsGenerating(true)

    try {
      const response = await withLoading(
        fetch('http://localhost:8000/generate-proposal', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(formData),
        })
      )

      if (!response.ok) {
        throw new Error('Failed to generate proposal')
      }

      const result = await response.json()
      showToast('Proposta gerada com sucesso!', 'success')
      router.push(`/history/${result.id}`)
    } catch (err) {
      showToast('Erro ao gerar proposta', 'error')
    } finally {
      setIsGenerating(false)
    }
  }

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target
    setFormData(prev => ({
      ...prev,
      [name]: value
    }))
  }

  const togglePreview = () => {
    setShowPreview(!showPreview)
  }

  const handleApplySuggestion = (section: string, content: string) => {
    setFormData(prev => ({
      ...prev,
      [section.toLowerCase()]: content
    }))
    showToast('Sugestão aplicada com sucesso!', 'success')
  }

  const handleAddSection = (suggestion: { section: string, value: string }) => {
    setFormData(prev => ({
      ...prev,
      [suggestion.section.toLowerCase()]: suggestion.value
    }))
    showToast(`Seção ${suggestion.section} adicionada!`, 'success')
  }

  return (
    <div className="min-h-screen bg-gradient-to-b from-gray-50 to-gray-100 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-7xl mx-auto grid grid-cols-1 lg:grid-cols-3 gap-8">
        <div className="lg:col-span-2">
          <div className="flex items-center justify-between mb-8">
            <h1 className="text-3xl font-bold text-gray-900">
              Gerar Nova Proposta
            </h1>
            <div className="space-x-4">
              <Button
                variant="outline"
                onClick={togglePreview}
              >
                {showPreview ? 'Ocultar Preview' : 'Mostrar Preview'}
              </Button>
              {suggestions?.overall_quality && (
                <div className="inline-flex items-center space-x-2">
                  <span className="text-sm text-gray-500">
                    Completude:
                  </span>
                  <div className="h-2 w-24 bg-gray-200 rounded-full overflow-hidden">
                    <div
                      className="h-full bg-green-500"
                      style={{ width: `${suggestions.overall_quality.completeness}%` }}
                    />
                  </div>
                  <span className="text-sm font-medium text-gray-700">
                    {suggestions.overall_quality.completeness}%
                  </span>
                </div>
              )}
            </div>
          </div>

          <form onSubmit={handleSubmit} className="space-y-6 bg-white p-6 rounded-lg shadow-lg">
            <FormInput
              label="Nome do Cliente"
              name="client_name"
              value={formData.client_name}
              onChange={handleInputChange}
              required
            />

            <FormInput
              label="Setor/Indústria"
              name="industry"
              value={formData.industry}
              onChange={handleInputChange}
              required
            />

            <FormInput
              label="Requisitos do Projeto"
              name="requirements"
              value={formData.requirements}
              onChange={handleInputChange}
              type="textarea"
              rows={4}
              required
              placeholder="Descreva os requisitos principais do projeto..."
            />

            <FormInput
              label="Escopo"
              name="scope"
              value={formData.scope}
              onChange={handleInputChange}
              type="textarea"
              rows={3}
              placeholder="Defina o escopo do projeto..."
            />

            <FormInput
              label="Cronograma"
              name="timeline"
              value={formData.timeline}
              onChange={handleInputChange}
              placeholder="Ex: 6 meses"
            />

            <FormInput
              label="Orçamento"
              name="budget"
              value={formData.budget}
              onChange={handleInputChange}
              placeholder="Ex: R$ 100.000"
            />

            <Button 
              type="submit" 
              className="w-full"
              disabled={isGenerating}
            >
              {isGenerating ? 'Gerando...' : 'Gerar Proposta'}
            </Button>
          </form>
        </div>

        <div className="space-y-6">
          {/* Smart Suggestions Panel */}
          {suggestions && (
            <SuggestionPanel
              contentSuggestions={suggestions.content_suggestions}
              sectionSuggestions={suggestions.section_suggestions}
              onApplySuggestion={handleApplySuggestion}
              onAddSection={handleAddSection}
            />
          )}
          
          {/* Preview Panel */}
          {showPreview && (
            <div className="lg:sticky lg:top-4 space-y-4">
              <h2 className="text-2xl font-bold text-gray-900 mb-4">
                Preview da Proposta
              </h2>
              <div className="overflow-auto max-h-[calc(100vh-8rem)]">
                <ProposalPreview proposal={formData} />
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
