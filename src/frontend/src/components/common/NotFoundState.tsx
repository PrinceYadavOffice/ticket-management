import { Link } from 'react-router-dom';

interface NotFoundStateProps {
  title?: string;
  message?: string;
}

export default function NotFoundState({
  title = 'Ticket not found',
  message = 'The ticket you are looking for does not exist or may have been removed.',
}: NotFoundStateProps) {
  return (
    <div className="empty-state">
      <h2>{title}</h2>
      <p>{message}</p>
      <Link to="/" className="btn btn-secondary">
        Back to tickets
      </Link>
    </div>
  );
}
