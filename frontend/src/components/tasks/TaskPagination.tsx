/**
 * TaskPagination Component Props
 */
interface TaskPaginationProps {
  /** Current active page number (1-indexed) */
  currentPage: number;
  
  /** Total number of items to paginate */
  totalItems: number;
  
  /** Number of items per page */
  pageSize: number;
  
  /** Callback when page changes */
  onPageChange: (page: number) => void;
  
  /** Callback when page size changes */
  onPageSizeChange: (size: number) => void;
}

/**
 * TaskPagination Component
 * 
 * Provides pagination controls for task lists with configurable page sizes.
 * Displays item range, page navigation, and page size selector.
 * 
 * Features:
 *   - Page size selector (10, 15, 20, 25 items per page)
 *   - Previous/Next navigation buttons
 *   - Current page indicator (e.g., "Page 2 of 5")
 *   - Item range display (e.g., "Showing 11 - 20 of 47 tasks")
 *   - Disabled state for navigation buttons at boundaries
 *   - Responsive layout with flexbox
 * 
 * @param currentPage - Current page number (1-indexed)
 * @param totalItems - Total number of items across all pages
 * @param pageSize - Number of items displayed per page
 * @param onPageChange - Function called when user navigates to different page
 * @param onPageSizeChange - Function called when user changes page size
 * 
 * @example
 * ```tsx
 * <TaskPagination
 *   currentPage={currentPage}
 *   totalItems={filteredTasks.length}
 *   pageSize={pageSize}
 *   onPageChange={setCurrentPage}
 *   onPageSizeChange={handlePageSizeChange}
 * />
 * ```
 * 
 * Behavior:
 *   - Previous button disabled on first page
 *   - Next button disabled on last page
 *   - Changing page size resets to page 1 (handled by parent)
 *   - Handles edge case of 0 total items gracefully
 * 
 * Styling:
 *   - Light gray background (#f8f9fa)
 *   - Rounded corners with padding
 *   - Responsive layout with wrapping
 *   - Blue buttons with hover effects
 */
export default function TaskPagination({
  currentPage,
  totalItems,
  pageSize,
  onPageChange,
  onPageSizeChange
}: TaskPaginationProps) {
  const totalPages = Math.ceil(totalItems / pageSize);
  const pageSizeOptions = [10, 15, 20, 25];

  const handlePrevious = () => {
    if (currentPage > 1) {
      onPageChange(currentPage - 1);
    }
  };

  const handleNext = () => {
    if (currentPage < totalPages) {
      onPageChange(currentPage + 1);
    }
  };

  const startItem = totalItems === 0 ? 0 : (currentPage - 1) * pageSize + 1;
  const endItem = Math.min(currentPage * pageSize, totalItems);

  return (
    <div style={{
      display: 'flex',
      justifyContent: 'space-between',
      alignItems: 'center',
      marginTop: '20px',
      padding: '15px',
      backgroundColor: '#f8f9fa',
      borderRadius: '8px',
      gap: '20px',
      flexWrap: 'wrap'
    }}>
      {/* Page size selector */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
        <label htmlFor="pageSize" style={{ fontSize: '0.9rem', color: '#495057' }}>
          Tareas por página:
        </label>
        <select
          id="pageSize"
          value={pageSize}
          onChange={(e) => onPageSizeChange(Number(e.target.value))}
          style={{
            padding: '5px 10px',
            borderRadius: '4px',
            border: '1px solid #ced4da',
            backgroundColor: 'white',
            cursor: 'pointer',
            fontSize: '0.9rem'
          }}
        >
          {pageSizeOptions.map(size => (
            <option key={size} value={size}>
              {size}
            </option>
          ))}
        </select>
      </div>

      {/* Items info */}
      <div style={{ fontSize: '0.9rem', color: '#6c757d' }}>
        Mostrando {startItem} - {endItem} de {totalItems} tareas
      </div>

      {/* Navigation buttons */}
      <div style={{ display: 'flex', gap: '10px', alignItems: 'center' }}>
        <button
          onClick={handlePrevious}
          disabled={currentPage === 1}
          style={{
            padding: '6px 12px',
            backgroundColor: currentPage === 1 ? '#e9ecef' : '#007bff',
            color: currentPage === 1 ? '#6c757d' : 'white',
            border: 'none',
            borderRadius: '4px',
            cursor: currentPage === 1 ? 'not-allowed' : 'pointer',
            fontSize: '0.9rem',
            fontWeight: '500',
            transition: 'background-color 0.2s'
          }}
        >
          ← Anterior
        </button>

        <span style={{ fontSize: '0.9rem', color: '#495057', minWidth: '80px', textAlign: 'center' }}>
          Página {totalPages > 0 ? currentPage : 0} de {totalPages}
        </span>

        <button
          onClick={handleNext}
          disabled={currentPage === totalPages || totalPages === 0}
          style={{
            padding: '6px 12px',
            backgroundColor: (currentPage === totalPages || totalPages === 0) ? '#e9ecef' : '#007bff',
            color: (currentPage === totalPages || totalPages === 0) ? '#6c757d' : 'white',
            border: 'none',
            borderRadius: '4px',
            cursor: (currentPage === totalPages || totalPages === 0) ? 'not-allowed' : 'pointer',
            fontSize: '0.9rem',
            fontWeight: '500',
            transition: 'background-color 0.2s'
          }}
        >
          Siguiente →
        </button>
      </div>
    </div>
  );
}
