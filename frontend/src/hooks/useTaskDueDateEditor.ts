import { useState, useCallback } from 'react';

/**
 * useTaskDueDateEditor - Custom hook for managing due date editing state
 * 
 * Provides inline editing functionality for task due dates with edit/cancel/save operations.
 * Handles date format conversion between ISO format (backend) and YYYY-MM-DD (HTML input).
 * 
 * Following SOLID principles:
 *   - Single Responsibility: Manages only due date editing state
 *   - Open/Closed: Easy to extend with new functionality
 * 
 * @param currentDueDate - The current due date of the task (ISO format or null)
 * @returns Object containing:
 *   - isEditing: Boolean indicating if date is being edited
 *   - selectedDate: Currently selected date in YYYY-MM-DD format
 *   - setSelectedDate: Function to update selected date
 *   - startEditing: Function to enter edit mode (initializes with current date)
 *   - cancelEditing: Function to exit edit mode without saving
 *   - saveDueDate: Function to save the selected date (accepts callback)
 * 
 * @example
 * ```tsx
 * const { isEditing, selectedDate, setSelectedDate, startEditing, saveDueDate } = 
 *   useTaskDueDateEditor(task.due_date);
 * 
 * // Enter edit mode
 * <button onClick={startEditing}>Edit Due Date</button>
 * 
 * // Save changes
 * <button onClick={() => saveDueDate(handleUpdateTask)}>Save</button>
 * ```
 * 
 * Features:
 *   - Converts between ISO and date input formats automatically
 *   - Supports clearing due date (empty string becomes null)
 *   - Restores original value on cancel
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
