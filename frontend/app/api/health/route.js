/**
 * API route for health check
 * This endpoint proxies the health check to the backend
 */

import { getBackendUrl } from '../../utils/config'

export async function GET() {
  try {
    // Get the backend URL based on execution context (server/client)
    const backendUrl = getBackendUrl();
    
    // Make a request to the backend health endpoint
    const response = await fetch(`${backendUrl}/health`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
      cache: 'no-store', // Don't cache the health check
    });

    // Get the response data
    const data = await response.json();

    // Return the response with the same status code
    return Response.json(
      { 
        status: data.status,
        timestamp: data.timestamp,
        frontend: 'healthy',
      },
      { status: response.status }
    );
  } catch (error) {
    console.error('Health check failed:', error);
    
    // Return error response
    return Response.json(
      { 
        status: 'error',
        message: 'Failed to connect to backend',
        error: error.message,
        frontend: 'healthy',
      },
      { status: 503 }
    );
  }
}
