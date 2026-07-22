import { useState, type FormEvent } from 'react';

interface CommentFormProps {
  onSubmit: (message: string) => void | Promise<void>;
  submitting?: boolean;
  error?: string;
}

export default function CommentForm({ onSubmit, submitting = false, error }: CommentFormProps) {
  const [message, setMessage] = useState('');
  const [clientError, setClientError] = useState('');
  const errorId = 'comment-message-error';

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    if (!message.trim()) {
      setClientError('Comment cannot be blank');
      return;
    }
    setClientError('');
    const trimmed = message.trim();
    try {
      await onSubmit(trimmed);
      setMessage('');
    } catch {
      // Parent displays API errors; keep draft text for retry.
    }
  };

  const displayError = clientError || error;

  return (
    <form className="comment-form" onSubmit={handleSubmit} noValidate>
      <label htmlFor="comment-message">
        Add comment
        <textarea
          id="comment-message"
          value={message}
          rows={3}
          maxLength={2000}
          required
          onChange={(e) => setMessage(e.target.value)}
          aria-invalid={!!displayError}
          aria-describedby={displayError ? errorId : undefined}
        />
      </label>
      {displayError && (
        <span id={errorId} className="field-error" role="alert">
          {displayError}
        </span>
      )}
      <button type="submit" className="btn btn-primary" disabled={submitting}>
        {submitting ? 'Posting…' : 'Post comment'}
      </button>
    </form>
  );
}
