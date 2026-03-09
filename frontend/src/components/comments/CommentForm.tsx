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
    <form onSubmit={handleSubmit} className="mb-4">
      <textarea
        value={content}
        onChange={(e) => setContent(e.target.value)}
        placeholder={placeholder}
        disabled={isSubmitting}
        className="w-full min-h-[80px] p-3 border border-gray-200 rounded-lg text-sm bg-gray-50 focus:bg-white focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all resize-y mb-2 outline-none"
      />
      <div className="flex justify-end">
        <button
          type="submit"
          disabled={isSubmitting || content.trim() === ''}
          className={`px-4 py-2 rounded-lg text-sm font-bold transition-all ${
            content.trim() === '' || isSubmitting
              ? 'bg-gray-200 text-gray-400 cursor-not-allowed'
              : 'bg-primary-600 text-white hover:bg-primary-700 shadow-sm hover:shadow active:scale-95 cursor-pointer'
          }`}
        >
          {isSubmitting ? 'Enviando...' : 'Comentar'}
        </button>
      </div>
    </form>
  );
}
