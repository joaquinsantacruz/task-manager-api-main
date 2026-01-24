import { useState, useEffect } from 'react';
import { User } from '../types';
import { UserService } from '../services/userService';

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
