import { Link } from 'react-router-dom';

import type { Ticket } from '../../api/types';
import type { User } from '../../api/types';

interface TicketListProps {
  tickets: Ticket[];
  users: User[];
}

function userName(users: User[], id: number | null): string {
  if (id == null) return '—';
  return users.find((u) => u.id === id)?.name ?? `User #${id}`;
}

export default function TicketList({ tickets, users }: TicketListProps) {
  return (
    <div className="table-wrap">
      <table className="ticket-table">
        <thead>
          <tr>
            <th scope="col">Title</th>
            <th scope="col">Status</th>
            <th scope="col">Priority</th>
            <th scope="col">Assignee</th>
            <th scope="col">Updated</th>
          </tr>
        </thead>
        <tbody>
          {tickets.map((ticket) => (
            <tr key={ticket.id}>
              <td>
                <Link to={`/tickets/${ticket.id}`} className="ticket-link">
                  {ticket.title}
                </Link>
              </td>
              <td>
                <span className={`badge status-${ticket.status.replace(/\s+/g, '-').toLowerCase()}`}>
                  {ticket.status}
                </span>
              </td>
              <td>{ticket.priority}</td>
              <td>{userName(users, ticket.assignedTo)}</td>
              <td>{new Date(ticket.updatedAt).toLocaleString()}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
