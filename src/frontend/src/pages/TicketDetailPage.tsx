import { useCallback, useEffect, useState } from 'react';
import { Link, useParams } from 'react-router-dom';

import { ApiError } from '../api/client';
import {
  addComment,
  fetchTicket,
  transitionTicketStatus,
  updateTicket,
} from '../api/tickets';
import type { TicketDetail, TicketStatus, UpdateTicketPayload } from '../api/types';
import CommentForm from '../components/comments/CommentForm';
import CommentList from '../components/comments/CommentList';
import ErrorAlert from '../components/common/ErrorAlert';
import LoadingSpinner from '../components/common/LoadingSpinner';
import NotFoundState from '../components/common/NotFoundState';
import TicketForm, { mapApiErrorToFields, type TicketFormValues } from '../components/tickets/TicketForm';
import TicketStatusActions from '../components/tickets/TicketStatusActions';
import { useActingUser } from '../context/ActingUserContext';

export default function TicketDetailPage() {
  const { id } = useParams();
  const ticketId = Number(id);
  const { users, currentUserId } = useActingUser();

  const [ticket, setTicket] = useState<TicketDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [notFound, setNotFound] = useState(false);
  const [error, setError] = useState<unknown>(null);
  const [success, setSuccess] = useState<string | null>(null);

  const [saving, setSaving] = useState(false);
  const [fieldErrors, setFieldErrors] = useState<Record<string, string>>({});

  const [statusLoading, setStatusLoading] = useState(false);
  const [statusError, setStatusError] = useState<unknown>(null);

  const [commentSubmitting, setCommentSubmitting] = useState(false);
  const [commentError, setCommentError] = useState<string | undefined>();

  const loadTicket = useCallback(async () => {
    if (!Number.isInteger(ticketId) || ticketId < 1) {
      setNotFound(true);
      setLoading(false);
      return;
    }
    setLoading(true);
    setError(null);
    try {
      const data = await fetchTicket(ticketId);
      setTicket(data);
      setNotFound(false);
    } catch (err) {
      if (err instanceof ApiError && err.status === 404) {
        setNotFound(true);
        setTicket(null);
      } else {
        setError(err);
      }
    } finally {
      setLoading(false);
    }
  }, [ticketId]);

  useEffect(() => {
    loadTicket();
  }, [loadTicket]);

  const handleUpdate = async (payload: UpdateTicketPayload) => {
    if (!ticket) return;
    setSaving(true);
    setError(null);
    setFieldErrors({});
    setSuccess(null);
    try {
      await updateTicket(ticket.id, payload);
      await loadTicket();
      setSuccess('Ticket updated successfully.');
    } catch (err) {
      setError(err);
      setFieldErrors(mapApiErrorToFields(err));
    } finally {
      setSaving(false);
    }
  };

  const handleStatusTransition = async (status: TicketStatus) => {
    if (!ticket) return;
    setStatusLoading(true);
    setStatusError(null);
    setSuccess(null);
    const previousStatus = ticket.status;
    try {
      await transitionTicketStatus(ticket.id, status);
      await loadTicket();
      setSuccess(`Status updated to ${status}.`);
    } catch (err) {
      setStatusError(err);
      setTicket((t) => (t ? { ...t, status: previousStatus } : t));
    } finally {
      setStatusLoading(false);
    }
  };

  const handleComment = async (message: string) => {
    if (!ticket || currentUserId == null) {
      setCommentError('Please select a user before commenting.');
      return;
    }
    setCommentSubmitting(true);
    setCommentError(undefined);
    try {
      await addComment(ticket.id, message, currentUserId);
      await loadTicket();
      setSuccess('Comment added.');
    } catch (err) {
      if (err instanceof ApiError) {
        setCommentError(err.message);
      } else if (err instanceof Error) {
        setCommentError(err.message);
      }
    } finally {
      setCommentSubmitting(false);
    }
  };

  if (loading) return <LoadingSpinner label="Loading ticket…" />;
  if (notFound) return <NotFoundState />;

  if (!ticket) return <ErrorAlert error={error} />;

  const formValues: TicketFormValues = {
    title: ticket.title,
    description: ticket.description,
    priority: ticket.priority,
    assignedTo: ticket.assignedTo != null ? String(ticket.assignedTo) : '',
  };

  return (
    <div className="page">
      <div className="page-header">
        <h2>Ticket #{ticket.id}</h2>
        <Link to="/" className="btn btn-secondary">
          Back to list
        </Link>
      </div>

      {success && (
        <div className="alert alert-success" role="status">
          {success}
          <button type="button" className="btn-text" onClick={() => setSuccess(null)}>
            ×
          </button>
        </div>
      )}
      <ErrorAlert error={error} onDismiss={() => setError(null)} />

      <section className="ticket-meta card">
        <dl className="meta-grid">
          <div>
            <dt>Status</dt>
            <dd>
              <span className={`badge status-${ticket.status.replace(/\s+/g, '-').toLowerCase()}`}>
                {ticket.status}
              </span>
            </dd>
          </div>
          <div>
            <dt>Creator</dt>
            <dd>{ticket.creator.name}</dd>
          </div>
          <div>
            <dt>Assignee</dt>
            <dd>{ticket.assignee?.name ?? 'Unassigned'}</dd>
          </div>
          <div>
            <dt>Created</dt>
            <dd>{new Date(ticket.createdAt).toLocaleString()}</dd>
          </div>
          <div>
            <dt>Updated</dt>
            <dd>{new Date(ticket.updatedAt).toLocaleString()}</dd>
          </div>
        </dl>
      </section>

      <section className="card">
        <h3>Edit ticket</h3>
        <TicketForm
          key={`${ticket.id}-${ticket.updatedAt}`}
          mode="edit"
          users={users}
          initialValues={formValues}
          submitting={saving}
          fieldErrors={fieldErrors}
          onSubmit={handleUpdate}
          submitLabel="Save changes"
        />
      </section>

      <section className="card">
        <TicketStatusActions
          currentStatus={ticket.status}
          allowedTransitions={ticket.allowedStatusTransitions}
          onTransition={handleStatusTransition}
          loading={statusLoading}
          error={statusError}
        />
      </section>

      <section className="card">
        <h3>Comments</h3>
        <CommentList comments={ticket.comments} />
        <CommentForm
          onSubmit={handleComment}
          submitting={commentSubmitting}
          error={commentError}
        />
      </section>
    </div>
  );
}
