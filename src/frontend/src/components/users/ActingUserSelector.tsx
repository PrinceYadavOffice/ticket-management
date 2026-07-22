import { useActingUser } from '../../context/ActingUserContext';

export default function ActingUserSelector() {
  const { users, currentUserId, setCurrentUserId, loading } = useActingUser();

  if (loading) {
    return <span className="acting-user-loading">Loading users…</span>;
  }

  return (
    <label className="acting-user-selector">
      <span className="label-text">Acting as</span>
      <select
        value={currentUserId ?? ''}
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
