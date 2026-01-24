import { useState, FormEvent } from 'react';
import Modal from './Modal';
import { TaskStatus } from '../types';

interface TaskFormModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (title: string, description: string, status: TaskStatus) => Promise<void>;
}

export default function TaskFormModal({ isOpen, onClose, onSubmit }: TaskFormModalProps) {
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [status, setStatus] = useState<TaskStatus>('todo');
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    if (!title.trim()) return;

    setIsSubmitting(true);
    try {
      await onSubmit(title, description, status);
      // Limpiar el formulario y cerrar
      setTitle('');
      setDescription('');
      setStatus('todo');
      onClose();
    } catch (error) {
      console.error('Error submitting task', error);
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleClose = () => {
    // Limpiar formulario al cerrar
    setTitle('');
    setDescription('');
    setStatus('todo');
    onClose();
  };

  return (
    <Modal isOpen={isOpen} onClose={handleClose} title="Nueva Tarea">
      <form onSubmit={handleSubmit}>
        <div style={{ marginBottom: '1rem' }}>
          <label htmlFor="title" style={{ display: 'block', marginBottom: '0.5rem', fontWeight: 'bold' }}>
            Título <span style={{ color: 'red' }}>*</span>
          </label>
          <input
            id="title"
            type="text"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            placeholder="Título de la tarea"
            required
            style={{
              width: '100%',
              padding: '0.5rem',
              border: '1px solid #ddd',
              borderRadius: '4px',
              fontSize: '1rem'
            }}
          />
        </div>

        <div style={{ marginBottom: '1rem' }}>
          <label htmlFor="description" style={{ display: 'block', marginBottom: '0.5rem', fontWeight: 'bold' }}>
            Descripción
          </label>
          <textarea
            id="description"
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            placeholder="Descripción de la tarea (opcional)"
            rows={4}
            style={{
              width: '100%',
              padding: '0.5rem',
              border: '1px solid #ddd',
              borderRadius: '4px',
              fontSize: '1rem',
              resize: 'vertical'
            }}
          />
        </div>

        <div style={{ marginBottom: '1.5rem' }}>
          <label htmlFor="status" style={{ display: 'block', marginBottom: '0.5rem', fontWeight: 'bold' }}>
            Estado
          </label>
          <select
            id="status"
            value={status}
            onChange={(e) => setStatus(e.target.value as TaskStatus)}
            style={{
              width: '100%',
              padding: '0.5rem',
              border: '1px solid #ddd',
              borderRadius: '4px',
              fontSize: '1rem'
            }}
          >
            <option value="todo">Por Hacer</option>
            <option value="in_progress">En Progreso</option>
            <option value="done">Completada</option>
          </select>
        </div>

        <div style={{ display: 'flex', gap: '1rem', justifyContent: 'flex-end' }}>
          <button
            type="button"
            onClick={handleClose}
            disabled={isSubmitting}
            style={{
              padding: '0.5rem 1rem',
              border: '1px solid #ddd',
              borderRadius: '4px',
              background: 'white',
              cursor: 'pointer'
            }}
          >
            Cancelar
          </button>
          <button
            type="submit"
            disabled={isSubmitting || !title.trim()}
            style={{
              padding: '0.5rem 1rem',
              border: 'none',
              borderRadius: '4px',
              background: '#007bff',
              color: 'white',
              cursor: isSubmitting || !title.trim() ? 'not-allowed' : 'pointer',
              opacity: isSubmitting || !title.trim() ? 0.6 : 1
            }}
          >
            {isSubmitting ? 'Creando...' : 'Crear Tarea'}
          </button>
        </div>
      </form>
    </Modal>
  );
}
