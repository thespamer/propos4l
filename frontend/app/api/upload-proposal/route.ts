import { NextRequest, NextResponse } from 'next/server';

export async function POST(request: NextRequest) {
  try {
    const formData = await request.formData();
    const files = formData.getAll('files');
    const clientName = formData.get('client_name');
    const industry = formData.get('industry');

    if (!files || files.length === 0) {
      return NextResponse.json(
        { error: 'No files provided' },
        { status: 400 }
      );
    }

    // Enviar para o backend
    const backendUrl = process.env.NEXT_PUBLIC_API_URL || 'http://backend:8000';
    const backendFormData = new FormData();
    
    // Adicionar os arquivos
    files.forEach((file) => {
      backendFormData.append('files', file);
    });
    
    // Adicionar os metadados
    backendFormData.append('client_name', clientName as string);
    backendFormData.append('industry', industry as string);

    const response = await fetch(`${backendUrl}/api/v1/proposals/upload`, {
      method: 'POST',
      body: backendFormData,
    });

    if (!response.ok) {
      const error = await response.text();
      throw new Error(error || 'Failed to upload files');
    }

    const result = await response.json();

    return NextResponse.json({
      message: 'Upload successful',
      tracking_ids: result.tracking_ids
    });

  } catch (error) {
    console.error('Upload error:', error);
    return NextResponse.json(
      { error: error instanceof Error ? error.message : 'Failed to upload files' },
      { status: 500 }
    );
  }
}
