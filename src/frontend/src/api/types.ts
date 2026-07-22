export type UserRole = 'Agent' | 'Admin';

export type TicketPriority = 'Low' | 'Medium' | 'High' | 'Critical';

export type TicketStatus =
  | 'Open'
  | 'In Progress'
  | 'Resolved'
  | 'Closed'
  | 'Cancelled';

export interface User {
  id: number;
  name: string;
  email: string;
  role: UserRole;
}

export interface Ticket {
  id: number;
  title: string;
  description: string;
  priority: TicketPriority;
  status: TicketStatus;
  assignedTo: number | null;
  createdBy: number;
  createdAt: string;
  updatedAt: string;
}

export interface TicketListResponse {
  items: Ticket[];
  total: number;
  page: number;
  pageSize: number;
}

export interface Comment {
  id: number;
  ticketId: number;
  message: string;
  createdAt: string;
  createdBy: User;
}

export interface TicketDetail extends Ticket {
  creator: User;
  assignee: User | null;
  comments: Comment[];
  allowedStatusTransitions: TicketStatus[];
}

export interface ApiErrorBody {
  error: {
    code: string;
    message: string;
    details: {
      fields?: Record<string, string>;
      [key: string]: unknown;
    };
  };
}

export interface TicketFilters {
  q?: string;
  status?: TicketStatus | '';
  priority?: TicketPriority | '';
  assignedTo?: number | '';
  unassigned?: boolean;
  createdBy?: number | '';
  page?: number;
  pageSize?: number;
}

export interface CreateTicketPayload {
  title: string;
  description: string;
  priority: TicketPriority;
  assignedTo?: number | null;
}

export interface UpdateTicketPayload {
  title?: string;
  description?: string;
  priority?: TicketPriority;
  assignedTo?: number | null;
}
