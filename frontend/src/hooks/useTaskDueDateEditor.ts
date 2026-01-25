import { useState, useCallback } from 'react';

/**
 * useTaskDueDateEditor - Custom hook for managing due date editing state
 * 
 * Following SOLID principles:
 * - Single Responsibility: Manages only due date editing state
 * - Open/Closed: Easy to extend with new functionality
 * 
 * @param currentDueDate - The current due date of the task (ISO format)
 * @returns State and handlers for due date editing
 */
export const useTaskDueDateEditor = (currentDueDate: string | null | undefined) => {
  // Helper function to convert ISO date to YYYY-MM-DD format for input
  const isoToDateInputFormat = (isoDate: string | null | undefined): string => {
    if (!isoDate) return '';
    const date = new Date(isoDate);
    return date.toISOString().split('T')[0];
  };

  const [isEditing, setIsEditing] = useState(false);
  const [selectedDate, setSelectedDate] = useState(isoToDateInputFormat(currentDueDate));

  const startEditing = useCallback(() => {
    setSelectedDate(isoToDateInputFormat(currentDueDate));
    setIsEditing(true);
  }, [currentDueDate]);

  const cancelEditing = useCallback(() => {
    setSelectedDate(isoToDateInputFormat(currentDueDate));
    setIsEditing(false);
  }, [currentDueDate]);

  const saveDueDate = useCallback((onSave: (newDueDate: string | null) => void) => {
    // If empty, send null to clear the due date
    const dateToSave = selectedDate.trim() === '' ? null : selectedDate;
    onSave(dateToSave);
    setIsEditing(false);
  }, [selectedDate]);

  return {
    isEditing,
    selectedDate,
    setSelectedDate,
    startEditing,
    cancelEditing,
    saveDueDate
  };
};
