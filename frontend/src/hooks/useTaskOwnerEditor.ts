import { useState, useEffect } from 'react';
import { User } from '../types';
import { UserService } from '../services/userService';

/**
 * useTaskOwnerEditor - Custom hook for managing task owner reassignment
 * 
 * Provides functionality to change task ownership with lazy loading of users list.
 * Only fetches the users list when entering edit mode for the first time.
 * 
 * @param currentOwnerId - The ID of the current task owner
 * @returns Object containing:
 *   - isEditing: Boolean indicating if owner is being edited
 *   - users: Array of all available users (sorted by email)
 *   - selectedOwnerId: ID of the currently selected owner
 *   - loadingUsers: Boolean indicating if users are being fetched
 *   - setSelectedOwnerId: Function to update selected owner ID
 *   - startEditing: Function to enter edit mode (triggers user fetch)
 *   - cancelEditing: Function to exit edit mode without saving
 *   - saveOwner: Function to save the selected owner (accepts callback)
 * 
 * @example
 * ```tsx
 * const { isEditing, users, selectedOwnerId, setSelectedOwnerId, startEditing, saveOwner } = 
 *   useTaskOwnerEditor(task.owner_id);
 * 
 * // Enter edit mode
 * <button onClick={startEditing}>Change Owner</button>
 * 
 * // Select new owner
 * <select value={selectedOwnerId} onChange={(e) => setSelectedOwnerId(Number(e.target.value))}>
 *   {users.map(user => <option key={user.id} value={user.id}>{user.email}</option>)}
 * </select>
 * 
 * // Save changes
 * <button onClick={() => saveOwner(handleChangeOwner)}>Save</button>
 * ```
 * 
 * Performance:
 *   - Lazy loading: Users are only fetched when entering edit mode
 *   - Caching: Users list is cached after first fetch
 *   - Alphabetical sorting for better UX
 * 
 * Note:
 *   - Requires OWNER role permissions (enforced by backend)
 *   - saveOwner only calls callback if a valid owner is selected
 */
export function useTaskOwnerEditor(currentOwnerId: number | null) {
  const [isEditing, setIsEditing] = useState(false);
  const [users, setUsers] = useState<User[]>([]);
  const [selectedOwnerId, setSelectedOwnerId] = useState<number | null>(null);
  const [loadingUsers, setLoadingUsers] = useState(false);

  useEffect(() => {
    if (isEditing && users.length === 0) {
      setLoadingUsers(true);
      UserService.getAllUsers()
        .then(data => {
          setUsers(data.sort((a, b) => a.email.localeCompare(b.email)));
        })
        .catch(error => {
          console.error("Error loading users", error);
        })
        .finally(() => {
          setLoadingUsers(false);
        });
    }
  }, [isEditing, users.length]);

  const startEditing = () => {
    setSelectedOwnerId(currentOwnerId);
    setIsEditing(true);
  };

  const cancelEditing = () => {
    setIsEditing(false);
    setSelectedOwnerId(null);
  };

  const saveOwner = (onSave: (newOwnerId: number) => void) => {
    if (selectedOwnerId) {
      onSave(selectedOwnerId);
      setIsEditing(false);
    }
  };

  return {
    isEditing,
    users,
    selectedOwnerId,
    loadingUsers,
    setSelectedOwnerId,
    startEditing,
    cancelEditing,
    saveOwner,
  };
}
