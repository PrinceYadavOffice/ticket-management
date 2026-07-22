import { useState, type FormEvent } from 'react';

interface CommentFormProps {
  onSubmit: (message: string) => void;
  submitting?: boolean;
  error?: string;
}

export default function CommentForm({ onSubmit, submitting = false, error }: CommentFormProps) {
  const [message, setMessage] = useState('');
  const [clientError, setClientError] = useState('');

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault();
    if (!message.trim()) {
      setClientError('Comment cannot be blank');
      return;
    }
    setClientError('');
    onSubmit(message.trim());
    setMessage('');
  };

  return (
    <form className="comment-form" onSubmit={handleSubmit}>
      <label htmlFor="comment-message">
        Add comment
        <textarea
          id="comment-message"
          value={message}
          rows={3}
          maxLength={2000}
          required
          onChange={(e) => setMessage(e.target.value)}
          aria-invalid={!!(clientError || error)}
        />
      </label>
      {(clientError || error) && (
        <span className="field-error" role="alert">
          {clientError || error}
        </span>
      )}
      <button type="submit" className="btn btn-primary" disabled={submitting}>
        {submitting ? 'Posting…' : 'Post comment'}
      </button>
    </form>
  );
}
