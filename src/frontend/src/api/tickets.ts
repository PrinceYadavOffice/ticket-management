import { apiDownload, apiRequest } from './client';
import type {
  Comment,
  CreateTicketPayload,
  Ticket,
  TicketDetail,
  TicketFilters,
  TicketListResponse,
  TicketStatus,
  UpdateTicketPayload,
  User,
} from './types';

function buildQuery(filters: TicketFilters): string {
  const params = new URLSearchParams();
  if (filters.q) params.set('q', filters.q);
  if (filters.status) params.set('status', filters.status);
  if (filters.priority) params.set('priority', filters.priority);
  if (filters.unassigned) params.set('unassigned', 'true');
  else if (filters.assignedTo !== undefined && filters.assignedTo !== '') {
    params.set('assignedTo', String(filters.assignedTo));
  }
  if (filters.createdBy !== undefined && filters.createdBy !== '') {
    params.set('createdBy', String(filters.createdBy));
  }
  params.set('page', String(filters.page ?? 1));
  params.set('pageSize', String(filters.pageSize ?? 20));
  const query = params.toString();
  return query ? `?${query}` : '';
}

export function fetchUsers(): Promise<User[]> {
  return apiRequest<User[]>('/api/users');
}

export function fetchTickets(filters: TicketFilters = {}): Promise<TicketListResponse> {
  return apiRequest<TicketListResponse>(`/api/tickets${buildQuery(filters)}`);
}

export function fetchTicket(id: number): Promise<TicketDetail> {
  return apiRequest<TicketDetail>(`/api/tickets/${id}`);
}

export function createTicket(
  payload: CreateTicketPayload,
  actingUserId: number,
): Promise<Ticket> {
  return apiRequest<Ticket>('/api/tickets', {
    method: 'POST',
    body: payload,
    actingUserId,
    requireActingUser: true,
  });
}

export function updateTicket(
  id: number,
  payload: UpdateTicketPayload,
): Promise<Ticket> {
  return apiRequest<Ticket>(`/api/tickets/${id}`, {
    method: 'PATCH',
    body: payload,
  });
}

export function transitionTicketStatus(
  id: number,
  status: TicketStatus,
): Promise<Ticket> {
  return apiRequest<Ticket>(`/api/tickets/${id}/status`, {
    method: 'PATCH',
    body: { status },
  });
}

export function addComment(
  ticketId: number,
  message: string,
  actingUserId: number,
): Promise<Comment> {
  return apiRequest<Comment>(`/api/tickets/${ticketId}/comments`, {
    method: 'POST',
    body: { message },
    actingUserId,
    requireActingUser: true,
  });
}

export function exportTicketsCsv(actingUserId: number): Promise<{ blob: Blob; filename: string }> {
  return apiDownload('/api/tickets/export.csv', actingUserId);
}

export { buildQuery };
