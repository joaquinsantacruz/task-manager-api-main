import { useState, FormEvent } from 'react';
import { Modal } from '../common';
import { TaskStatus, CreateTaskDTO } from '../../types';

interface TaskFormModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (taskData: CreateTaskDTO) => Promise<void>;
}

export default function TaskFormModal({ isOpen, onClose, onSubmit }: TaskFormModalProps) {
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [status, setStatus] = useState<TaskStatus>('todo');
  const [dueDate, setDueDate] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    if (!title.trim()) return;

    // Validate due date is not in the past
    if (dueDate) {
      const selectedDate = new Date(`${dueDate}T00:00:00`);
      const today = new Date();
      today.setHours(0, 0, 0, 0);
      
      if (selectedDate < today) {
        alert('La fecha de vencimiento no puede ser en el pasado');
        return;
      }
    }

    setIsSubmitting(true);
    try {
      // Convert YYYY-MM-DD to ISO datetime format
      let formattedDueDate: string | undefined = undefined;
      if (dueDate) {
        const date = new Date(dueDate);
        // Set to noon UTC to avoid timezone issues
        date.setUTCHours(12, 0, 0, 0);
        formattedDueDate = date.toISOString();
      }
      
      const taskData: CreateTaskDTO = {
        title,
        description: description || undefined,
        status,
        due_date: formattedDueDate
      };
      
      await onSubmit(taskData);
      // Limpiar el formulario y cerrar
      setTitle('');
      setDescription('');
      setStatus('todo');
      setDueDate('');
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
    setDueDate('');
    onClose();
  };

  // Get today's date in YYYY-MM-DD format for min attribute
  const today = new Date().toISOString().split('T')[0];

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

        <div style={{ marginBottom: '1rem' }}>
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

        <div style={{ marginBottom: '1.5rem' }}>
          <label htmlFor="dueDate" style={{ display: 'block', marginBottom: '0.5rem', fontWeight: 'bold' }}>
            Fecha de Vencimiento
          </label>
          <input
            id="dueDate"
            type="date"
            value={dueDate}
            onChange={(e) => setDueDate(e.target.value)}
            min={today}
            style={{
              width: '100%',
              padding: '0.5rem',
              border: '1px solid #ddd',
              borderRadius: '4px',
              fontSize: '1rem'
            }}
          />
          <small style={{ color: '#666', fontSize: '0.85rem' }}>
            Opcional - Recibirás notificaciones cuando se acerque la fecha
          </small>
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
