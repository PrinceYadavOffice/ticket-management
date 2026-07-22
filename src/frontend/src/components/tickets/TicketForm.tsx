import { useState, type FormEvent } from 'react';

import { ApiError } from '../../api/client';
import type { CreateTicketPayload, TicketPriority, UpdateTicketPayload, User } from '../../api/types';
import { TICKET_PRIORITIES } from '../../utils/constants';

export interface TicketFormValues {
  title: string;
  description: string;
  priority: TicketPriority;
  assignedTo: string;
}

interface TicketFormProps {
  mode: 'create' | 'edit';
  users: User[];
  initialValues?: TicketFormValues;
  submitting?: boolean;
  fieldErrors?: Record<string, string>;
  onSubmit: (payload: CreateTicketPayload | UpdateTicketPayload) => void;
  submitLabel?: string;
}

const defaultValues: TicketFormValues = {
  title: '',
  description: '',
  priority: 'Medium',
  assignedTo: '',
};

export function validateTicketForm(values: TicketFormValues): Record<string, string> {
  const errors: Record<string, string> = {};
  if (!values.title.trim()) errors.title = 'Title is required';
  if (!values.description.trim()) errors.description = 'Description is required';
  return errors;
}

export default function TicketForm({
  mode,
  users,
  initialValues = defaultValues,
  submitting = false,
  fieldErrors = {},
  onSubmit,
  submitLabel,
}: TicketFormProps) {
  const [values, setValues] = useState<TicketFormValues>(initialValues);
  const [clientErrors, setClientErrors] = useState<Record<string, string>>({});

  const errors = { ...clientErrors, ...fieldErrors };

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault();
    const validation = validateTicketForm(values);
    setClientErrors(validation);
    if (Object.keys(validation).length > 0) return;

    const payload = {
      title: values.title.trim(),
      description: values.description.trim(),
      priority: values.priority,
      assignedTo: values.assignedTo ? Number(values.assignedTo) : null,
    };
    onSubmit(payload);
  };

  return (
    <form className="ticket-form" onSubmit={handleSubmit} noValidate>
      <label htmlFor="ticket-title">
        Title
        <input
          id="ticket-title"
          type="text"
          value={values.title}
          maxLength={200}
          required
          onChange={(e) => setValues((v) => ({ ...v, title: e.target.value }))}
          aria-invalid={!!errors.title}
          aria-describedby={errors.title ? 'title-error' : undefined}
        />
        {errors.title && (
          <span id="title-error" className="field-error">
            {errors.title}
          </span>
        )}
      </label>

      <label htmlFor="ticket-description">
        Description
        <textarea
          id="ticket-description"
          value={values.description}
          maxLength={5000}
          required
          rows={5}
          onChange={(e) => setValues((v) => ({ ...v, description: e.target.value }))}
          aria-invalid={!!errors.description}
          aria-describedby={errors.description ? 'description-error' : undefined}
        />
        {errors.description && (
          <span id="description-error" className="field-error">
            {errors.description}
          </span>
        )}
      </label>

      <label htmlFor="ticket-priority">
        Priority
        <select
          id="ticket-priority"
          value={values.priority}
          onChange={(e) =>
            setValues((v) => ({ ...v, priority: e.target.value as TicketPriority }))
          }
        >
          {TICKET_PRIORITIES.map((p) => (
            <option key={p} value={p}>
              {p}
            </option>
          ))}
        </select>
      </label>

      <label htmlFor="ticket-assignee">
        Assignee
        <select
          id="ticket-assignee"
          value={values.assignedTo}
          onChange={(e) => setValues((v) => ({ ...v, assignedTo: e.target.value }))}
        >
          <option value="">Unassigned</option>
          {users.map((u) => (
            <option key={u.id} value={String(u.id)}>
              {u.name}
            </option>
          ))}
        </select>
        {errors.assignedTo && <span className="field-error">{errors.assignedTo}</span>}
      </label>

      <button type="submit" className="btn btn-primary" disabled={submitting}>
        {submitting ? 'Saving…' : submitLabel ?? (mode === 'create' ? 'Create ticket' : 'Save changes')}
      </button>
    </form>
  );
}

export function mapApiErrorToFields(error: unknown): Record<string, string> {
  if (error instanceof ApiError) return error.fieldErrors;
  return {};
}
