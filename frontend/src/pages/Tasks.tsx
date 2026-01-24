import { useEffect, useState } from 'react';
import { TaskService } from '../services/taskService';
import { Task, TaskStatus } from '../types';
import TaskFormModal from '../components/TaskFormModal';

export default function Tasks() {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [isModalOpen, setIsModalOpen] = useState(false);

  const fetchTasks = async () => {
    try {
      // 3. Usamos el servicio en lugar de api.get directo
      const data = await TaskService.getAll();
      setTasks(data);
    } catch (error) {
      console.error("Error fetching tasks", error);
    }
  };

  useEffect(() => {
    fetchTasks();
  }, []);

  const handleCreateTask = async (title: string, description: string, status: TaskStatus) => {
    try {
      await TaskService.create(title, description, status);
      fetchTasks();
    } catch (error) {
      console.error("Error creating task", error);
      throw error; // Re-lanzar para que el modal lo maneje
    }
  };

  const handleToggleStatus = async (task: Task) => {
    try {
      // Definimos la rotación: todo -> in_progress -> done -> todo
      const statusRotation: Record<TaskStatus, TaskStatus> = {
        'todo': 'in_progress',
        'in_progress': 'done',
        'done': 'todo'
      };

      const newStatus = statusRotation[task.status];
      
      // Usamos el método específico del servicio
      await TaskService.updateStatus(task.id, newStatus);
      fetchTasks();
    } catch (error) {
      console.error("Error updating task", error);
    }
  };

  const handleDelete = async (id: number) => {
    if(!confirm("¿Borrar tarea?")) return;
    try {
      await TaskService.delete(id);
      fetchTasks();
    } catch (error) {
      console.error("Error deleting task", error);
    }
  };

  return (
    <div className="tasks-container">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
        <h1 style={{ margin: 0 }}>Mis Tareas</h1>
        <button 
          onClick={() => setIsModalOpen(true)}
          style={{
            padding: '0.75rem 1.5rem',
            background: '#007bff',
            color: 'white',
            border: 'none',
            borderRadius: '4px',
            cursor: 'pointer',
            fontSize: '1rem',
            fontWeight: 'bold'
          }}
        >
          + Agregar Tarea
        </button>
      </div>

      <TaskFormModal 
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        onSubmit={handleCreateTask}
      />

      <ul className="task-list">
        {tasks.map(task => (
          <li key={task.id} className="task-item">
            <span 
                onClick={() => handleToggleStatus(task)}
                className={`task-text ${task.status === 'done' ? 'completed' : ''}`}
                style={{
                    // Aplicamos tachado solo si es 'done' (según backend)
                    textDecoration: task.status === 'done' ? 'line-through' : 'none',
                    color: task.status === 'done' ? '#888' : 'inherit'
                }}
            >
              {/* Mostramos el estado visualmente para saber en qué etapa está */}
              <small style={{marginRight: '10px', fontWeight: 'bold'}}>
                [{task.status.toUpperCase().replace('_', ' ')}]
              </small>
              {task.title}
            </span>
            
            <button 
                onClick={() => handleDelete(task.id)} 
                className="btn-delete"
            >
                Eliminar
            </button>
          </li>
        ))}
      </ul>
    </div>
  );
}