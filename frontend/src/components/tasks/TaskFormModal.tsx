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
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label htmlFor="title" className="block mb-1 font-bold text-gray-700">
            Título <span className="text-red-500">*</span>
          </label>
          <input
            id="title"
            type="text"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            placeholder="Título de la tarea"
            required
            className="input-field"
          />
        </div>

        <div>
          <label htmlFor="description" className="block mb-1 font-bold text-gray-700">
            Descripción
          </label>
          <textarea
            id="description"
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            placeholder="Descripción de la tarea (opcional)"
            rows={4}
            className="input-field resize-y"
          />
        </div>

        <div>
          <label htmlFor="status" className="block mb-1 font-bold text-gray-700">
            Estado
          </label>
          <select
            id="status"
            value={status}
            onChange={(e) => setStatus(e.target.value as TaskStatus)}
            className="input-field"
          >
            <option value="todo">Por Hacer</option>
            <option value="in_progress">En Progreso</option>
            <option value="done">Completada</option>
          </select>
        </div>

        <div>
          <label htmlFor="dueDate" className="block mb-1 font-bold text-gray-700">
            Fecha de Vencimiento
          </label>
          <input
            id="dueDate"
            type="date"
            value={dueDate}
            onChange={(e) => setDueDate(e.target.value)}
            min={today}
            className="input-field"
          />
          <small className="text-gray-500 text-xs mt-1 block">
            Opcional - Recibirás notificaciones cuando se acerque la fecha
          </small>
        </div>

        <div className="flex gap-4 justify-end pt-4 border-t border-gray-100">
          <button
            type="button"
            onClick={handleClose}
            disabled={isSubmitting}
            className="btn-secondary"
          >
            Cancelar
          </button>
          <button
            type="submit"
            disabled={isSubmitting || !title.trim()}
            className={`btn-primary ${isSubmitting || !title.trim() ? 'opacity-60 cursor-not-allowed' : ''}`}
          >
            {isSubmitting ? 'Creando...' : 'Crear Tarea'}
          </button>
        </div>
      </form>
    </Modal>
  );
}
