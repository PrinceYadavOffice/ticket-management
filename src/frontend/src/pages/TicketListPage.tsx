import { useCallback, useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { fetchTickets } from '../api/tickets';
import type { Ticket } from '../api/types';
import ErrorAlert from '../components/common/ErrorAlert';
import EmptyState from '../components/common/EmptyState';
import LoadingSpinner from '../components/common/LoadingSpinner';
import TicketExportButton from '../components/tickets/TicketExportButton';
import TicketFiltersBar, {
  filtersToApiParams,
  type FilterFormState,
} from '../components/tickets/TicketFilters';
import TicketList from '../components/tickets/TicketList';
import { useActingUser } from '../context/ActingUserContext';

const defaultFilters: FilterFormState = {
  q: '',
  status: '',
  priority: '',
  assignedTo: '',
  unassigned: false,
};

export default function TicketListPage() {
  const { users } = useActingUser();
  const [formFilters, setFormFilters] = useState<FilterFormState>(defaultFilters);
  const [appliedFilters, setAppliedFilters] = useState<FilterFormState>(defaultFilters);
  const [page, setPage] = useState(1);
  const [tickets, setTickets] = useState<Ticket[]>([]);
  const [total, setTotal] = useState(0);
  const [pageSize] = useState(20);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<unknown>(null);
  const [success, setSuccess] = useState<string | null>(null);

  const loadTickets = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await fetchTickets(filtersToApiParams(appliedFilters, page, pageSize));
      setTickets(data.items);
      setTotal(data.total);
    } catch (err) {
      setError(err);
      setTickets([]);
      setTotal(0);
    } finally {
      setLoading(false);
    }
  }, [appliedFilters, page, pageSize]);

  useEffect(() => {
    loadTickets();
  }, [loadTickets]);

  const totalPages = Math.max(1, Math.ceil(total / pageSize));

  return (
    <div className="page">
      <div className="page-header">
        <h2>Tickets</h2>
        <div className="page-actions">
          <TicketExportButton
            onError={setError}
            onSuccess={(msg) => {
              setSuccess(msg);
              setError(null);
            }}
          />
          <Link to="/tickets/new" className="btn btn-primary">
            New ticket
          </Link>
        </div>
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

      <TicketFiltersBar
        users={users}
        value={formFilters}
        onChange={setFormFilters}
        onApply={() => {
          setAppliedFilters(formFilters);
          setPage(1);
        }}
        onReset={() => {
          setFormFilters(defaultFilters);
          setAppliedFilters(defaultFilters);
          setPage(1);
        }}
      />

      {loading ? (
        <LoadingSpinner label="Loading tickets…" />
      ) : tickets.length === 0 ? (
        <EmptyState
          title="No tickets found"
          message="Try adjusting your filters or create a new ticket."
          action={
            <Link to="/tickets/new" className="btn btn-primary">
              Create ticket
            </Link>
          }
        />
      ) : (
        <>
          <TicketList tickets={tickets} users={users} />
          <div className="pagination">
            <button
              type="button"
              className="btn btn-secondary"
              disabled={page <= 1}
              onClick={() => setPage((p) => p - 1)}
            >
              Previous
            </button>
            <span>
              Page {page} of {totalPages} ({total} total)
            </span>
            <button
              type="button"
              className="btn btn-secondary"
              disabled={page >= totalPages}
              onClick={() => setPage((p) => p + 1)}
            >
              Next
            </button>
          </div>
        </>
      )}
    </div>
  );
}
