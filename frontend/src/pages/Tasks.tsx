import { useEffect, useState } from 'react';
import { TaskService } from '../services/taskService';
import { Task, TaskStatus } from '../types';
import TaskFormModal from '../components/TaskFormModal';
import TaskDetailModal from '../components/TaskDetailModal';
import TaskList from '../components/TaskList';
import TaskFilter from '../components/TaskFilter';
import { useTaskFilter } from '../hooks/useTaskFilter';

const STATUS_ROTATION: Record<TaskStatus, TaskStatus> = {
  'todo': 'in_progress',
  'in_progress': 'done',
  'done': 'todo'
};

export default function Tasks() {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [isDetailModalOpen, setIsDetailModalOpen] = useState(false);
  const [selectedTask, setSelectedTask] = useState<Task | null>(null);
  
  const { selectedStatuses, setSelectedStatuses, filteredTasks } = useTaskFilter(tasks);

  const fetchTasks = async () => {
    try {
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
      throw error;
    }
  };

  const handleOpenDetail = (task: Task) => {
    setSelectedTask(task);
    setIsDetailModalOpen(true);
  };

  const handleToggleStatus = async (task: Task, e: React.MouseEvent) => {
    e.stopPropagation();
    try {
      const newStatus = STATUS_ROTATION[task.status];
      await TaskService.updateStatus(task.id, newStatus);
      fetchTasks();
    } catch (error) {
      console.error("Error updating task", error);
    }
  };

  const handleChangeStatus = async (taskId: number, newStatus: TaskStatus) => {
    try {
      await TaskService.updateStatus(taskId, newStatus);
      fetchTasks();
      setIsDetailModalOpen(false);
    } catch (error) {
      console.error("Error updating task", error);
    }
  };

  const handleChangeOwner = async (taskId: number, newOwnerId: number) => {
    try {
      await TaskService.changeOwner(taskId, newOwnerId);
      fetchTasks();
      setIsDetailModalOpen(false);
    } catch (error) {
      console.error("Error changing task owner", error);
    }
  };

  const handleDelete = async (id: number) => {
    if (!confirm("¿Borrar tarea?")) return;
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

      <TaskDetailModal 
        isOpen={isDetailModalOpen}
        onClose={() => setIsDetailModalOpen(false)}
        task={selectedTask}
        onChangeStatus={handleChangeStatus}
        onChangeOwner={handleChangeOwner}
      />

      <TaskFilter 
        selectedStatuses={selectedStatuses}
        onFilterChange={setSelectedStatuses}
      />

      <TaskList 
        tasks={filteredTasks}
        onOpenDetail={handleOpenDetail}
        onToggleStatus={handleToggleStatus}
        onDelete={handleDelete}
      />
    </div>
  );
}