import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';

import { ApiError } from '../api/client';
import { createTicket } from '../api/tickets';
import type { CreateTicketPayload, UpdateTicketPayload } from '../api/types';
import ErrorAlert from '../components/common/ErrorAlert';
import TicketForm, { mapApiErrorToFields } from '../components/tickets/TicketForm';
import { useActingUser } from '../context/ActingUserContext';

export default function TicketCreatePage() {
  const navigate = useNavigate();
  const { users, currentUserId } = useActingUser();
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<unknown>(null);
  const [fieldErrors, setFieldErrors] = useState<Record<string, string>>({});

  const handleSubmit = async (payload: CreateTicketPayload | UpdateTicketPayload) => {
    if (currentUserId == null) {
      setError(
        new ApiError(401, {
          error: {
            code: 'MISSING_ACTING_USER',
            message: 'Please select a user before creating a ticket.',
            details: {},
          },
        }),
      );
      return;
    }
    setSubmitting(true);
    setError(null);
    setFieldErrors({});
    try {
      const ticket = await createTicket(payload as CreateTicketPayload, currentUserId);
      navigate(`/tickets/${ticket.id}`);
    } catch (err) {
      setError(err);
      setFieldErrors(mapApiErrorToFields(err));
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="page">
      <div className="page-header">
        <h2>Create ticket</h2>
        <Link to="/" className="btn btn-secondary">
          Back to list
        </Link>
      </div>
      <ErrorAlert error={error} onDismiss={() => setError(null)} />
      <TicketForm
        mode="create"
        users={users}
        submitting={submitting}
        fieldErrors={fieldErrors}
        onSubmit={handleSubmit}
      />
    </div>
  );
}
