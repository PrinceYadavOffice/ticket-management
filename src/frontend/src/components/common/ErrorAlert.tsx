import { ApiError } from '../../api/client';

interface ErrorAlertProps {
  error: unknown;
  onDismiss?: () => void;
}

function getMessage(error: unknown): string {
  if (error instanceof ApiError) return error.message;
  if (error instanceof Error) return error.message;
  return 'Something went wrong. Please try again.';
}

function getFieldErrors(error: unknown): Record<string, string> {
  if (error instanceof ApiError) return error.fieldErrors;
  return {};
}

export default function ErrorAlert({ error, onDismiss }: ErrorAlertProps) {
  if (!error) return null;
  const fields = getFieldErrors(error);

  return (
    <div className="alert alert-error" role="alert">
      <div className="alert-row">
        <strong>{getMessage(error)}</strong>
        {onDismiss && (
          <button type="button" className="btn-text" onClick={onDismiss} aria-label="Dismiss">
            ×
          </button>
        )}
      </div>
      {Object.keys(fields).length > 0 && (
        <ul className="field-error-list">
          {Object.entries(fields).map(([key, value]) => (
            <li key={key}>
              <strong>{key}:</strong> {value}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
