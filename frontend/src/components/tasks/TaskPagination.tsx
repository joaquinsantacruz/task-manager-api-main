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
    <div className="flex flex-wrap justify-between items-center mt-8 p-4 bg-white border border-gray-100 rounded-xl shadow-sm gap-4">
      {/* Page size selector */}
      <div className="flex items-center gap-3">
        <label htmlFor="pageSize" className="text-sm font-medium text-gray-600">
          Tareas por página:
        </label>
        <select
          id="pageSize"
          value={pageSize}
          onChange={(e) => onPageSizeChange(Number(e.target.value))}
          className="px-3 py-1.5 border border-gray-300 rounded-lg bg-white text-sm focus:ring-2 focus:ring-primary-500 outline-none cursor-pointer hover:border-gray-400 transition-colors"
        >
          {pageSizeOptions.map(size => (
            <option key={size} value={size}>
              {size}
            </option>
          ))}
        </select>
      </div>

      {/* Items info */}
      <div className="text-sm text-gray-500 font-medium">
        Mostrando {startItem} - {endItem} de {totalItems} tareas
      </div>

      {/* Navigation buttons */}
      <div className="flex items-center gap-4">
        <button
          onClick={handlePrevious}
          disabled={currentPage === 1}
          className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
            currentPage === 1
              ? 'bg-gray-100 text-gray-400 cursor-not-allowed'
              : 'bg-white border border-gray-300 text-gray-700 hover:bg-gray-50'
          }`}
        >
          &larr; Anterior
        </button>

        <span className="text-sm font-medium text-gray-700 min-w-[5rem] text-center">
          Página {totalPages > 0 ? currentPage : 0} de {totalPages}
        </span>

        <button
          onClick={handleNext}
          disabled={currentPage === totalPages || totalPages === 0}
          className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
            currentPage === totalPages || totalPages === 0
              ? 'bg-gray-100 text-gray-400 cursor-not-allowed'
              : 'bg-white border border-gray-300 text-gray-700 hover:bg-gray-50'
          }`}
        >
          Siguiente &rarr;
        </button>
      </div>
    </div>
  );
}
