import type { TicketFilters, TicketPriority, TicketStatus } from '../../api/types';
import type { User } from '../../api/types';
import { TICKET_PRIORITIES, TICKET_STATUSES } from '../../utils/constants';

export interface FilterFormState {
  q: string;
  status: TicketStatus | '';
  priority: TicketPriority | '';
  assignedTo: string;
  unassigned: boolean;
}

interface TicketFiltersProps {
  users: User[];
  value: FilterFormState;
  onChange: (value: FilterFormState) => void;
  onApply: () => void;
  onReset: () => void;
}

export default function TicketFiltersBar({
  users,
  value,
  onChange,
  onApply,
  onReset,
}: TicketFiltersProps) {
  const set = (patch: Partial<FilterFormState>) => onChange({ ...value, ...patch });

  return (
    <form
      className="filters"
      onSubmit={(e) => {
        e.preventDefault();
        onApply();
      }}
    >
      <div className="filters-grid">
        <label>
          Search
          <input
            type="search"
            value={value.q}
            onChange={(e) => set({ q: e.target.value })}
            placeholder="Title or description"
          />
        </label>
        <label>
          Status
          <select
            value={value.status}
            onChange={(e) => set({ status: e.target.value as TicketStatus | '' })}
          >
            <option value="">All</option>
            {TICKET_STATUSES.map((s) => (
              <option key={s} value={s}>
                {s}
              </option>
            ))}
          </select>
        </label>
        <label>
          Priority
          <select
            value={value.priority}
            onChange={(e) => set({ priority: e.target.value as TicketPriority | '' })}
          >
            <option value="">All</option>
            {TICKET_PRIORITIES.map((p) => (
              <option key={p} value={p}>
                {p}
              </option>
            ))}
          </select>
        </label>
        <label>
          Assignee
          <select
            value={value.unassigned ? 'unassigned' : value.assignedTo}
            onChange={(e) => {
              const v = e.target.value;
              if (v === 'unassigned') {
                set({ unassigned: true, assignedTo: '' });
              } else {
                set({ unassigned: false, assignedTo: v });
              }
            }}
            disabled={value.unassigned}
          >
            <option value="">All</option>
            <option value="unassigned">Unassigned only</option>
            {users.map((u) => (
              <option key={u.id} value={String(u.id)}>
                {u.name}
              </option>
            ))}
          </select>
        </label>
        <label className="checkbox-label">
          <input
            type="checkbox"
            checked={value.unassigned}
            onChange={(e) =>
              set({ unassigned: e.target.checked, assignedTo: e.target.checked ? '' : value.assignedTo })
            }
          />
          Unassigned only
        </label>
      </div>
      <div className="filters-actions">
        <button type="submit" className="btn btn-primary">
          Apply filters
        </button>
        <button type="button" className="btn btn-secondary" onClick={onReset}>
          Reset
        </button>
      </div>
    </form>
  );
}

export function filtersToApiParams(
  form: FilterFormState,
  page: number,
  pageSize: number,
): TicketFilters {
  return {
    q: form.q.trim() || undefined,
    status: form.status || undefined,
    priority: form.priority || undefined,
    unassigned: form.unassigned || undefined,
    assignedTo: form.unassigned || !form.assignedTo ? undefined : Number(form.assignedTo),
    page,
    pageSize,
  };
}
