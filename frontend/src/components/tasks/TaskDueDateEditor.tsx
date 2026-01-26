/**
 * TaskDueDateEditor - Component for editing task due date
 * 
 */
interface TaskDueDateEditorProps {
  dueDate: string | null | undefined;
  isOwnerRole: boolean;
  isEditing: boolean;
  selectedDate: string;
  onStartEdit: () => void;
  onCancelEdit: () => void;
  onSaveEdit: () => void;
  onDateChange: (date: string) => void;
}

export default function TaskDueDateEditor({
  dueDate,
  isOwnerRole,
  isEditing,
  selectedDate,
  onStartEdit,
  onCancelEdit,
  onSaveEdit,
  onDateChange
}: TaskDueDateEditorProps) {
  
  const formatDueDate = (dateString: string | null | undefined) => {
    if (!dateString) return 'Sin fecha de vencimiento';
    
    const date = new Date(dateString);
    const now = new Date();
    now.setHours(0, 0, 0, 0);
    const taskDate = new Date(date);
    taskDate.setHours(0, 0, 0, 0);
    
    const isOverdue = taskDate < now;
    const isDueToday = taskDate.getTime() === now.getTime();
    
    const formatted = date.toLocaleDateString('es-ES', {
      day: '2-digit',
      month: 'long',
      year: 'numeric'
    });
    
    return {
      formatted,
      isOverdue,
      isDueToday
    };
  };

  const dueDateInfo = formatDueDate(dueDate);
  const today = new Date().toISOString().split('T')[0];

  const getStatusColor = () => {
    if (typeof dueDateInfo === 'string') return '#999';
    if (dueDateInfo.isOverdue) return '#dc3545';
    if (dueDateInfo.isDueToday) return '#ffc107';
    return '#28a745';
  };

  const getStatusIcon = () => {
    if (typeof dueDateInfo === 'string') return '📅';
    if (dueDateInfo.isOverdue) return '⚠️';
    if (dueDateInfo.isDueToday) return '🔔';
    return '📅';
  };

  const getStatusText = () => {
    if (typeof dueDateInfo === 'string') return '';
    if (dueDateInfo.isOverdue) return ' - Vencida';
    if (dueDateInfo.isDueToday) return ' - Vence hoy';
    return '';
  };

  return (
    <div>
      <label style={{ 
        display: 'block', 
        marginBottom: '0.5rem', 
        fontWeight: 'bold', 
        color: '#666', 
        fontSize: '0.875rem' 
      }}>
        FECHA DE VENCIMIENTO
      </label>

      {!isEditing ? (
        <div style={{ 
          display: 'flex', 
          justifyContent: 'space-between', 
          alignItems: 'center',
          padding: '0.5rem',
          backgroundColor: '#f9f9f9',
          borderRadius: '4px',
          border: `1px solid ${getStatusColor()}`,
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <span style={{ fontSize: '1.2rem' }}>{getStatusIcon()}</span>
            <span style={{ 
              color: getStatusColor(),
              fontWeight: typeof dueDateInfo !== 'string' && (dueDateInfo.isOverdue || dueDateInfo.isDueToday) ? 'bold' : 'normal'
            }}>
              {typeof dueDateInfo === 'string' ? dueDateInfo : dueDateInfo.formatted}
              {typeof dueDateInfo !== 'string' && getStatusText()}
            </span>
          </div>
          
          {isOwnerRole && (
            <button
              onClick={onStartEdit}
              style={{
                padding: '0.25rem 0.75rem',
                fontSize: '0.85rem',
                border: '1px solid #007bff',
                borderRadius: '4px',
                background: 'white',
                color: '#007bff',
                cursor: 'pointer'
              }}
            >
              {dueDate ? 'Cambiar' : 'Establecer'}
            </button>
          )}
        </div>
      ) : (
        <div style={{ 
          padding: '0.75rem',
          backgroundColor: '#f0f8ff',
          borderRadius: '4px',
          border: '1px solid #007bff'
        }}>
          <div style={{ marginBottom: '0.75rem' }}>
            <label htmlFor="dueDate" style={{ 
              display: 'block', 
              marginBottom: '0.5rem',
              fontSize: '0.9rem',
              color: '#333'
            }}>
              Seleccionar fecha:
            </label>
            <input
              id="dueDate"
              type="date"
              value={selectedDate}
              onChange={(e) => onDateChange(e.target.value)}
              min={today}
              style={{
                width: '100%',
                padding: '0.5rem',
                border: '1px solid #ccc',
                borderRadius: '4px',
                fontSize: '1rem'
              }}
            />
            <small style={{ color: '#666', fontSize: '0.85rem', display: 'block', marginTop: '0.25rem' }}>
              Deja vacío para eliminar la fecha de vencimiento
            </small>
          </div>

          <div style={{ display: 'flex', gap: '0.5rem' }}>
            <button
              onClick={onSaveEdit}
              style={{
                padding: '0.5rem 1rem',
                border: 'none',
                borderRadius: '4px',
                background: '#28a745',
                color: 'white',
                cursor: 'pointer',
                fontSize: '0.9rem',
                fontWeight: 'bold'
              }}
            >
              Guardar
            </button>
            <button
              onClick={onCancelEdit}
              style={{
                padding: '0.5rem 1rem',
                border: '1px solid #6c757d',
                borderRadius: '4px',
                background: 'white',
                color: '#6c757d',
                cursor: 'pointer',
                fontSize: '0.9rem'
              }}
            >
              Cancelar
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
