import { Link, Outlet } from 'react-router-dom';

import ActingUserSelector from '../users/ActingUserSelector';

export default function AppLayout() {
  return (
    <div className="app-shell">
      <header className="app-header">
        <div className="header-top">
          <h1>
            <Link to="/">Support Ticket Management</Link>
          </h1>
          <ActingUserSelector />
        </div>
        <p className="disclaimer" role="note">
          Demo mode: the selected user is sent as <code>X-User-Id</code> for acting-user
          context. This is <strong>not authentication</strong>.
        </p>
        <nav className="app-nav" aria-label="Main">
          <Link to="/">Tickets</Link>
          <Link to="/tickets/new">New Ticket</Link>
        </nav>
      </header>
      <main className="app-main">
        <Outlet />
      </main>
    </div>
  );
}
