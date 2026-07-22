import type { ApiErrorBody } from './types';

export class ApiError extends Error {
  code: string;
  details: ApiErrorBody['error']['details'];
  status: number;

  constructor(status: number, body: ApiErrorBody) {
    super(body.error.message);
    this.name = 'ApiError';
    this.code = body.error.code;
    this.details = body.error.details;
    this.status = status;
  }

  get fieldErrors(): Record<string, string> {
    return this.details.fields ?? {};
  }
}

export class NetworkError extends Error {
  constructor(message = 'Unable to reach the server. Check your connection.') {
    super(message);
    this.name = 'NetworkError';
  }
}

const BASE_URL = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000';

type RequestOptions = {
  method?: string;
  body?: unknown;
  actingUserId?: number | null;
  requireActingUser?: boolean;
  headers?: Record<string, string>;
};

let actingUserIdProvider: (() => number | null) | null = null;

export function setActingUserIdProvider(provider: () => number | null): void {
  actingUserIdProvider = provider;
}

function isApiErrorBody(data: unknown): data is ApiErrorBody {
  return (
    typeof data === 'object' &&
    data !== null &&
    'error' in data &&
    typeof (data as ApiErrorBody).error?.message === 'string'
  );
}

function toApiError(status: number, data: unknown): ApiError {
  if (isApiErrorBody(data)) {
    return new ApiError(status, data);
  }
  return new ApiError(status, {
    error: {
      code: 'UNKNOWN_ERROR',
      message: 'Request failed',
      details: {},
    },
  });
}

async function parseJsonBody(response: Response): Promise<unknown> {
  const contentType = response.headers.get('content-type') ?? '';
  if (contentType.includes('application/json') && typeof response.json === 'function') {
    try {
      return await response.json();
    } catch {
      throw toApiError(response.status, null);
    }
  }
  if (typeof response.text !== 'function') {
    return null;
  }
  const text = await response.text();
  if (!text) {
    return null;
  }
  try {
    return JSON.parse(text);
  } catch {
    throw toApiError(response.status, null);
  }
}

export async function apiRequest<T>(
  path: string,
  options: RequestOptions = {},
): Promise<T> {
  const {
    method = 'GET',
    body,
    actingUserId,
    requireActingUser = false,
    headers = {},
  } = options;

  const resolvedUserId = actingUserId ?? actingUserIdProvider?.() ?? null;

  if (requireActingUser && resolvedUserId == null) {
    throw new ApiError(401, {
      error: {
        code: 'MISSING_ACTING_USER',
        message: 'Please select a user to continue.',
        details: {},
      },
    });
  }

  const requestHeaders: Record<string, string> = { ...headers };
  if (body !== undefined) {
    requestHeaders['Content-Type'] = 'application/json';
  }
  if (resolvedUserId != null) {
    requestHeaders['X-User-Id'] = String(resolvedUserId);
  }

  let response: Response;
  try {
    response = await fetch(`${BASE_URL}${path}`, {
      method,
      headers: requestHeaders,
      body: body !== undefined ? JSON.stringify(body) : undefined,
    });
  } catch {
    throw new NetworkError();
  }

  if (response.status === 204) {
    return undefined as T;
  }

  const contentType = response.headers.get('content-type') ?? '';
  if (contentType.includes('text/csv')) {
    return (await response.text()) as T;
  }

  const data = await parseJsonBody(response);
  if (!response.ok) {
    throw toApiError(response.status, data);
  }
  return data as T;
}

export async function apiDownload(
  path: string,
  actingUserId: number,
): Promise<{ blob: Blob; filename: string }> {
  let response: Response;
  try {
    response = await fetch(`${BASE_URL}${path}`, {
      headers: { 'X-User-Id': String(actingUserId) },
    });
  } catch {
    throw new NetworkError();
  }

  if (!response.ok) {
    const data = await parseJsonBody(response);
    throw toApiError(response.status, data);
  }

  const disposition = response.headers.get('Content-Disposition') ?? '';
  const match = disposition.match(/filename="([^"]+)"/);
  const filename = match?.[1] ?? 'export.csv';
  const blob = await response.blob();
  return { blob, filename };
}
