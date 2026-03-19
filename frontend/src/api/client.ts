import { getSessionId } from '../utils/session'

const BASE = import.meta.env.VITE_BASE_URL

export class ApiError extends Error {
  code: string
  status: number

  constructor(code: string, message: string, status: number) {
    super(message)
    this.code = code
    this.status = status
  }
}

export async function apiRequest<T>(
  path: string,
  options?: RequestInit
): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      'X-Session-ID': getSessionId(),
      ...options?.headers,
    },
  })

  if (!res.ok) {
    const err = await res.json()
    const detail = err.detail
    if (typeof detail === 'object' && detail?.message) {
      throw new ApiError(detail.type ?? 'UNKNOWN', detail.message, res.status)
    }
    throw new ApiError('UNKNOWN', typeof detail === 'string' ? detail : 'Request failed', res.status)
  }

  return res.json()
}