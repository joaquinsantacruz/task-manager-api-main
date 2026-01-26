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
    <div style={{ 
      display: 'flex', 
      gap: '1rem', 
      alignItems: 'center',
      padding: '1rem',
      backgroundColor: '#f8f9fa',
      borderRadius: '8px',
      marginBottom: '1.5rem'
    }}>
      <span style={{ fontWeight: 'bold', color: '#495057' }}>Filtrar por:</span>
      
      {STATUS_OPTIONS.map((option) => {
        const isSelected = selectedStatuses.includes(option.value);
        return (
          <label
            key={option.value}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '0.5rem',
              cursor: 'pointer',
              padding: '0.2rem 0.4rem',
              borderRadius: '6px',
              backgroundColor: isSelected ? option.color : 'transparent',
              color: isSelected ? (option.value === 'in_progress' ? '#000' : '#fff') : '#495057',
              border: `2px solid ${option.color}`,
              transition: 'all 0.2s',
              fontWeight: isSelected ? 'bold' : 'normal',
              fontSize: '0.9rem'
            }}
          >
            <input
              type="checkbox"
              checked={isSelected}
              onChange={() => handleToggle(option.value)}
              style={{ cursor: 'pointer' }}
            />
            {option.label}
          </label>
        );
      })}

      <button
        onClick={handleSelectAll}
        disabled={isAllSelected}
        style={{
          padding: '0.5rem 1rem',
          border: 'none',
          borderRadius: '6px',
          backgroundColor: isAllSelected ? '#e9ecef' : '#007bff',
          color: isAllSelected ? '#6c757d' : 'white',
          cursor: isAllSelected ? 'not-allowed' : 'pointer',
          fontSize: '0.85rem',
          fontWeight: 'bold',
          opacity: isAllSelected ? 0.6 : 1,
          marginLeft: 'auto'
        }}
      >
        Mostrar Todas
      </button>
    </div>
  );
}
