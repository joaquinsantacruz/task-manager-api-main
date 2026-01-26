import { useEffect, useState } from 'react';
import { TaskService } from '../services/taskService';
import { Task, TaskStatus, CreateTaskDTO } from '../types';
import { TaskFormModal, TaskDetailModal, TaskList, TaskFilter, TaskPagination } from '../components/tasks';
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
  const [currentPage, setCurrentPage] = useState(1);
  const [pageSize, setPageSize] = useState(10);
  
  const { selectedStatuses, setSelectedStatuses, filteredTasks } = useTaskFilter(tasks);
  
  // Calculate paginated tasks
  const totalFilteredTasks = filteredTasks.length;
  const startIndex = (currentPage - 1) * pageSize;
  const endIndex = startIndex + pageSize;
  const paginatedTasks = filteredTasks.slice(startIndex, endIndex);

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

  const handleCreateTask = async (taskData: CreateTaskDTO) => {
    try {
      await TaskService.create(taskData);
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

  const handleChangeDueDate = async (taskId: number, newDueDate: string | null) => {
    try {
      // Convert YYYY-MM-DD to ISO datetime format (set to noon UTC to avoid timezone issues)
      let formattedDate: string | undefined = undefined;
      
      if (newDueDate) {
        const date = new Date(newDueDate);
        // Set to noon UTC to avoid timezone issues
        date.setUTCHours(12, 0, 0, 0);
        formattedDate = date.toISOString();
      }
      
      await TaskService.update(taskId, { due_date: formattedDate });
      fetchTasks();
      setIsDetailModalOpen(false);
    } catch (error) {
      console.error("Error changing due date", error);
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

  const handlePageChange = (page: number) => {
    setCurrentPage(page);
  };

  const handlePageSizeChange = (size: number) => {
    setPageSize(size);
    setCurrentPage(1); // Reset to first page when changing page size
  };

  // Reset to first page when filters change
  useEffect(() => {
    setCurrentPage(1);
  }, [selectedStatuses]);

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
        onChangeDueDate={handleChangeDueDate}
      />

      <TaskFilter 
        selectedStatuses={selectedStatuses}
        onFilterChange={setSelectedStatuses}
      />

      <TaskList 
        tasks={paginatedTasks}
        onOpenDetail={handleOpenDetail}
        onToggleStatus={handleToggleStatus}
        onDelete={handleDelete}
      />

      <TaskPagination 
        currentPage={currentPage}
        totalItems={totalFilteredTasks}
        pageSize={pageSize}
        onPageChange={handlePageChange}
        onPageSizeChange={handlePageSizeChange}
      />
    </div>
  );
}