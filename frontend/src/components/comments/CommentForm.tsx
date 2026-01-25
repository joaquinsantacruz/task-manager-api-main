import { useState, FormEvent } from 'react';

/**
 * CommentForm - Component for creating new comments
 * 
 */
interface CommentFormProps {
  onSubmit: (content: string) => Promise<boolean>;
  placeholder?: string;
}

export default function CommentForm({ onSubmit, placeholder = 'Escribe un comentario...' }: CommentFormProps) {
  const [content, setContent] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    
    if (content.trim() === '') {
      alert('El comentario no puede estar vacío');
      return;
    }

    setIsSubmitting(true);
    const success = await onSubmit(content.trim());
    setIsSubmitting(false);

    if (success) {
      setContent('');
    }
  };

  return (
    <form onSubmit={handleSubmit} style={{ marginBottom: '1rem' }}>
      <textarea
        value={content}
        onChange={(e) => setContent(e.target.value)}
        placeholder={placeholder}
        disabled={isSubmitting}
        style={{
          width: '100%',
          minHeight: '80px',
          padding: '0.75rem',
          border: '1px solid #ccc',
          borderRadius: '4px',
          fontSize: '0.95rem',
          fontFamily: 'inherit',
          resize: 'vertical',
          marginBottom: '0.5rem'
        }}
      />
      <button
        type="submit"
        disabled={isSubmitting || content.trim() === ''}
        style={{
          padding: '0.5rem 1.5rem',
          border: 'none',
          borderRadius: '4px',
          background: content.trim() === '' ? '#ccc' : '#007bff',
          color: 'white',
          cursor: content.trim() === '' ? 'not-allowed' : 'pointer',
          fontSize: '0.95rem',
          fontWeight: 'bold'
        }}
      >
        {isSubmitting ? 'Enviando...' : 'Comentar'}
      </button>
    </form>
  );
}
