import { ReactNode } from 'react';

/**
 * Modal Component Props
 */
interface ModalProps {
  /** Controls modal visibility */
  isOpen: boolean;
  
  /** Callback when modal should be closed (clicking overlay or X button) */
  onClose: () => void;
  
  /** Title displayed in the modal header */
  title: string;
  
  /** Content to be rendered inside the modal */
  children: ReactNode;
}

/**
 * Modal Component
 * 
 * A reusable modal dialog component with overlay backdrop.
 * Provides a consistent modal experience across the application.
 * 
 * Features:
 *   - Click overlay to close
 *   - X button in header to close
 *   - Click on modal content doesn't close (event propagation stopped)
 *   - Scrollable content area with max height
 *   - Fixed positioning with high z-index
 *   - Centered on screen
 * 
 * @param isOpen - Controls whether modal is visible
 * @param onClose - Function called when user attempts to close modal
 * @param title - Modal title text
 * @param children - Modal content (forms, text, buttons, etc.)
 * 
 * @example
 * ```tsx
 * <Modal
 *   isOpen={showModal}
 *   onClose={() => setShowModal(false)}
 *   title="Edit Task"
 * >
 *   <TaskForm onSubmit={handleSubmit} />
 * </Modal>
 * ```
 * 
 * Styling:
 *   - Overlay: Semi-transparent black background (rgba(0,0,0,0.5))
 *   - Content: White background, rounded corners, padding
 *   - Min width: 400px, Max width: 600px
 *   - Max height: 80vh with overflow scroll
 *   - z-index: 1000
 * 
 * Accessibility:
 *   - Consider adding aria-modal="true" and role="dialog"
 *   - Consider trapping focus within modal when open
 *   - Consider adding keyboard ESC to close
 */
export default function Modal({ isOpen, onClose, title, children }: ModalProps) {
  if (!isOpen) return null;

  return (
    <div 
      className="fixed inset-0 z-[1000] flex items-center justify-center bg-black/50 backdrop-blur-sm animate-fade-in" 
      onClick={onClose}
    >
      <div 
        className="bg-white p-8 rounded-2xl shadow-2xl min-w-[400px] max-w-[600px] max-h-[85vh] overflow-auto transform transition-all animate-slide-up"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-2xl font-bold tracking-tight text-gray-900 m-0">{title}</h2>
          <button 
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 bg-transparent hover:bg-gray-100 rounded-full w-8 h-8 flex items-center justify-center text-xl transition-colors"
          >
            ×
          </button>
        </div>
        {children}
      </div>
    </div>
  );
}
