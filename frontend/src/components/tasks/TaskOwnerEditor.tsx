import { User } from '../../types';

interface TaskOwnerEditorProps {
  ownerEmail: string;
  isOwnerRole: boolean;
  isEditing: boolean;
  users: User[];
  selectedOwnerId: number | null;
  currentOwnerId: number;
  loadingUsers: boolean;
  onStartEdit: () => void;
  onCancelEdit: () => void;
  onSaveEdit: () => void;
  onSelectOwner: (ownerId: number) => void;
}

export default function TaskOwnerEditor({
  ownerEmail,
  isOwnerRole,
  isEditing,
  users,
  selectedOwnerId,
  currentOwnerId,
  loadingUsers,
  onStartEdit,
  onCancelEdit,
  onSaveEdit,
  onSelectOwner,
}: TaskOwnerEditorProps) {
  return (
    <div>
      <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: 'bold', color: '#666', fontSize: '0.875rem' }}>
        RESPONSABLE
      </label>
      {!isEditing ? (
        <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
          <p style={{ margin: 0, flex: 1 }}>{ownerEmail}</p>
          {isOwnerRole && (
            <button
              onClick={onStartEdit}
              style={{
                padding: '0.4rem 0.8rem',
                border: '1px solid #007bff',
                borderRadius: '4px',
                background: 'white',
                color: '#007bff',
                cursor: 'pointer',
                fontSize: '0.85rem',
                fontWeight: 'bold'
              }}
            >
              Cambiar
            </button>
          )}
        </div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
          <select
            value={selectedOwnerId || ''}
            onChange={(e) => onSelectOwner(Number(e.target.value))}
            disabled={loadingUsers}
            style={{
              padding: '0.5rem',
              border: '1px solid #ddd',
              borderRadius: '4px',
              fontSize: '1rem',
              cursor: 'pointer'
            }}
          >
            {loadingUsers ? (
              <option>Cargando...</option>
            ) : (
              users.map(user => (
                <option key={user.id} value={user.id}>
                  {user.email}
                </option>
              ))
            )}
          </select>
          <div style={{ display: 'flex', gap: '0.5rem' }}>
            <button
              onClick={onSaveEdit}
              disabled={!selectedOwnerId || selectedOwnerId === currentOwnerId}
              style={{
                flex: 1,
                padding: '0.5rem',
                border: 'none',
                borderRadius: '4px',
                background: selectedOwnerId && selectedOwnerId !== currentOwnerId ? '#28a745' : '#e9ecef',
                color: selectedOwnerId && selectedOwnerId !== currentOwnerId ? 'white' : '#6c757d',
                cursor: selectedOwnerId && selectedOwnerId !== currentOwnerId ? 'pointer' : 'not-allowed',
                fontSize: '0.9rem',
                fontWeight: 'bold'
              }}
            >
              Guardar
            </button>
            <button
              onClick={onCancelEdit}
              style={{
                flex: 1,
                padding: '0.5rem',
                border: '1px solid #6c757d',
                borderRadius: '4px',
                background: 'white',
                color: '#6c757d',
                cursor: 'pointer',
                fontSize: '0.9rem',
                fontWeight: 'bold'
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
