import { useActingUser } from '../../context/ActingUserContext';
import { exportTicketsCsv } from '../../api/tickets';
import { ApiError } from '../../api/client';
import { useState } from 'react';

interface TicketExportButtonProps {
  onError: (error: unknown) => void;
  onSuccess?: (message: string) => void;
}

export default function TicketExportButton({ onError, onSuccess }: TicketExportButtonProps) {
  const { currentUserId } = useActingUser();
  const [loading, setLoading] = useState(false);

  const handleExport = async () => {
    if (currentUserId == null) {
      onError(
        new ApiError(401, {
          error: {
            code: 'MISSING_ACTING_USER',
            message: 'Please select a user before exporting.',
            details: {},
          },
        }),
      );
      return;
    }
    setLoading(true);
    try {
      const { blob, filename } = await exportTicketsCsv(currentUserId);
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = filename;
      a.click();
      window.setTimeout(() => URL.revokeObjectURL(url), 100);
      onSuccess?.('CSV export downloaded.');
    } catch (err) {
      onError(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <button
      type="button"
      className="btn btn-secondary"
      onClick={handleExport}
      disabled={loading}
    >
      {loading ? 'Exporting…' : 'Export My Tickets (CSV)'}
    </button>
  );
}
