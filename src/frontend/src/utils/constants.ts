export const TICKET_PRIORITIES = ['Low', 'Medium', 'High', 'Critical'] as const;

export const TICKET_STATUSES = [
  'Open',
  'In Progress',
  'Resolved',
  'Closed',
  'Cancelled',
] as const;

export const ACTING_USER_STORAGE_KEY = 'actingUserId';

export const STATUS_ACTIONS: Record<string, string[]> = {
  Open: ['In Progress', 'Cancelled'],
  'In Progress': ['Resolved', 'Cancelled'],
  Resolved: ['Closed'],
  Closed: [],
  Cancelled: [],
};
