import { useActingUser } from '../../context/ActingUserContext';

export default function ActingUserSelector() {
  const { users, currentUserId, setCurrentUserId, loading, error } = useActingUser();

  if (loading) {
    return <span className="acting-user-loading">Loading users…</span>;
  }

  if (error) {
    return (
      <span className="acting-user-error" role="alert">
        Failed to load users: {error}
      </span>
    );
  }

  if (users.length === 0) {
    return (
      <span className="acting-user-error" role="alert">
        No users available. Run the backend seed script.
      </span>
    );
  }

  return (
    <label className="acting-user-selector">
      <span className="label-text">Acting as</span>
      <select
        value={currentUserId ?? users[0].id}
        onChange={(e) => setCurrentUserId(Number(e.target.value))}
        aria-label="Select acting user"
      >
        {users.map((user) => (
          <option key={user.id} value={user.id}>
            {user.name} ({user.role})
          </option>
        ))}
      </select>
    </label>
  );
}
