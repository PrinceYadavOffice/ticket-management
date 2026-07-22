import type { TicketStatus } from '../../api/types';

interface TicketStatusActionsProps {
  currentStatus: TicketStatus;
  allowedTransitions: TicketStatus[];
  onTransition: (status: TicketStatus) => void;
  loading?: boolean;
  error?: unknown;
}

export default function TicketStatusActions({
  currentStatus,
  allowedTransitions,
  onTransition,
  loading = false,
  error,
}: TicketStatusActionsProps) {
  if (allowedTransitions.length === 0) {
    return (
      <div className="status-actions" data-testid="status-actions">
        <p className="status-note">
          No status actions available for <strong>{currentStatus}</strong> tickets.
        </p>
      </div>
    );
  }

  return (
    <div className="status-actions" data-testid="status-actions">
      <h3>Change status</h3>
      <p className="status-current">
        Current: <strong>{currentStatus}</strong>
      </p>
      <div className="status-buttons">
        {allowedTransitions.map((status) => (
          <button
            key={status}
            type="button"
            className="btn btn-secondary"
            disabled={loading}
            onClick={() => onTransition(status)}
          >
            {loading ? 'Updating…' : `Move to ${status}`}
          </button>
        ))}
      </div>
      {error != null && (
        <p className="status-error" role="alert">
          {error instanceof Error ? error.message : 'Status update failed'}
        </p>
      )}
    </div>
  );
}
