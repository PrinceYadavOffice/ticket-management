import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from 'react';

import { fetchUsers } from '../api/tickets';
import type { User } from '../api/types';
import { setActingUserIdProvider } from '../api/client';
import { ACTING_USER_STORAGE_KEY } from '../utils/constants';

interface ActingUserContextValue {
  users: User[];
  currentUser: User | null;
  currentUserId: number | null;
  setCurrentUserId: (id: number) => void;
  loading: boolean;
  error: string | null;
}

const ActingUserContext = createContext<ActingUserContextValue | null>(null);

function readStoredUserId(): number | null {
  const raw = localStorage.getItem(ACTING_USER_STORAGE_KEY);
  if (!raw) return null;
  const id = Number(raw);
  return Number.isInteger(id) && id > 0 ? id : null;
}

export function ActingUserProvider({ children }: { children: ReactNode }) {
  const [users, setUsers] = useState<User[]>([]);
  const [currentUserId, setCurrentUserIdState] = useState<number | null>(readStoredUserId);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    (async () => {
      try {
        const data = await fetchUsers();
        if (cancelled) return;
        setUsers(data);
        const stored = readStoredUserId();
        const validStored = stored != null && data.some((u) => u.id === stored);
        const initialId = validStored ? stored : data[0]?.id ?? null;
        setCurrentUserIdState(initialId);
        if (initialId != null) {
          localStorage.setItem(ACTING_USER_STORAGE_KEY, String(initialId));
        }
      } catch (err) {
        if (!cancelled) {
          setError(err instanceof Error ? err.message : 'Failed to load users');
        }
      } finally {
        if (!cancelled) setLoading(false);
      }
    })();
    return () => {
      cancelled = true;
    };
  }, []);

  const setCurrentUserId = useCallback((id: number) => {
    setCurrentUserIdState(id);
    localStorage.setItem(ACTING_USER_STORAGE_KEY, String(id));
  }, []);

  useEffect(() => {
    setActingUserIdProvider(() => currentUserId);
    return () => setActingUserIdProvider(() => null);
  }, [currentUserId]);

  const currentUser = useMemo(
    () => users.find((u) => u.id === currentUserId) ?? null,
    [users, currentUserId],
  );

  const value = useMemo(
    () => ({
      users,
      currentUser,
      currentUserId,
      setCurrentUserId,
      loading,
      error,
    }),
    [users, currentUser, currentUserId, setCurrentUserId, loading, error],
  );

  return (
    <ActingUserContext.Provider value={value}>{children}</ActingUserContext.Provider>
  );
}

export function useActingUser(): ActingUserContextValue {
  const ctx = useContext(ActingUserContext);
  if (!ctx) {
    throw new Error('useActingUser must be used within ActingUserProvider');
  }
  return ctx;
}
