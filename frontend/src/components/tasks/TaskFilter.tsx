import { TaskStatus } from '../../types';

interface TaskFilterProps {
  selectedStatuses: TaskStatus[];
  onFilterChange: (statuses: TaskStatus[]) => void;
}

const STATUS_OPTIONS = [
  { value: 'todo' as TaskStatus, label: 'Por Hacer', color: '#6c757d' },
  { value: 'in_progress' as TaskStatus, label: 'En Progreso', color: '#ffc107' },
  { value: 'done' as TaskStatus, label: 'Completada', color: '#28a745' }
];

export default function TaskFilter({ selectedStatuses, onFilterChange }: TaskFilterProps) {
  const handleToggle = (status: TaskStatus) => {
    if (selectedStatuses.includes(status)) {
      // Si ya está seleccionado, quitarlo (solo si no es el último)
      if (selectedStatuses.length > 1) {
        onFilterChange(selectedStatuses.filter(s => s !== status));
      }
    } else {
      // Si no está seleccionado, agregarlo
      onFilterChange([...selectedStatuses, status]);
    }
  };

  const handleSelectAll = () => {
    onFilterChange(STATUS_OPTIONS.map(opt => opt.value));
  };

  const isAllSelected = selectedStatuses.length === STATUS_OPTIONS.length;

  return (
    <div className="flex flex-wrap gap-4 items-center p-4 bg-white border border-gray-100 rounded-xl shadow-sm mb-6">
      <span className="font-semibold text-gray-700">Filtrar por:</span>
      
      {STATUS_OPTIONS.map((option) => {
        const isSelected = selectedStatuses.includes(option.value);
        return (
          <label
            key={option.value}
            className={`flex items-center gap-2 cursor-pointer px-3 py-1.5 rounded-lg text-sm transition-all border-2 
              ${isSelected 
                ? (option.value === 'in_progress' ? 'bg-yellow-400 text-yellow-900 border-yellow-400 font-bold shadow-sm' : 
                   option.value === 'done' ? 'bg-green-500 text-white border-green-500 font-bold shadow-sm' : 
                   'bg-gray-500 text-white border-gray-500 font-bold shadow-sm')
                : 'bg-transparent text-gray-600 border-gray-200 hover:border-gray-300'
              }`}
          >
            <input
              type="checkbox"
              checked={isSelected}
              onChange={() => handleToggle(option.value)}
              className="w-4 h-4 rounded text-primary-600 focus:ring-primary-500 border-gray-300 cursor-pointer"
            />
            {option.label}
          </label>
        );
      })}

      <button
        onClick={handleSelectAll}
        disabled={isAllSelected}
        className={`ml-auto px-4 py-2 rounded-lg text-sm font-semibold transition-all
          ${isAllSelected 
            ? 'bg-gray-100 text-gray-400 cursor-not-allowed' 
            : 'bg-primary-50 text-primary-700 hover:bg-primary-100 cursor-pointer'
          }`}
      >
        Mostrar Todas
      </button>
    </div>
  );
}
