import React from 'react'

type BaseInputProps = {
  label: string
  error?: string
  type?: 'text' | 'textarea' | 'date'
  rows?: number
  className?: string
}

type InputProps = BaseInputProps & Omit<React.InputHTMLAttributes<HTMLInputElement>, keyof BaseInputProps>
type TextAreaProps = BaseInputProps & Omit<React.TextareaHTMLAttributes<HTMLTextAreaElement>, keyof BaseInputProps>

type FormInputProps = InputProps | TextAreaProps

export function FormInput({
  label,
  error,
  type = 'text',
  className = '',
  rows = 3,
  ...props
}: FormInputProps) {
  const inputClasses = `w-full px-3 py-2 border rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm
    ${error ? 'border-red-300' : 'border-gray-300'}
    ${props.disabled ? 'bg-gray-50 cursor-not-allowed' : 'bg-white'}
  `

  return (
    <div className={className}>
      <label className="block text-sm font-medium text-gray-700 mb-1">
        {label}
      </label>
      {type === 'textarea' ? (
        <textarea
          {...(props as React.TextareaHTMLAttributes<HTMLTextAreaElement>)}
          rows={rows}
          className={inputClasses}
        />
      ) : (
        <input
          {...(props as React.InputHTMLAttributes<HTMLInputElement>)}
          type={type}
          className={inputClasses}
        />
      )}
      {error && (
        <p className="mt-1 text-sm text-red-600">{error}</p>
      )}
    </div>
  )
}
