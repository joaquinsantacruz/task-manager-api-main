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
      className="modal-overlay" 
      onClick={onClose}
      style={{
        position: 'fixed',
        top: 0,
        left: 0,
        right: 0,
        bottom: 0,
        backgroundColor: 'rgba(0, 0, 0, 0.5)',
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        zIndex: 1000
      }}
    >
      <div 
        className="modal-content"
        onClick={(e) => e.stopPropagation()}
        style={{
          backgroundColor: 'white',
          padding: '2rem',
          borderRadius: '8px',
          minWidth: '400px',
          maxWidth: '600px',
          maxHeight: '80vh',
          overflow: 'auto'
        }}
      >
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
          <h2 style={{ margin: 0 }}>{title}</h2>
          <button 
            onClick={onClose}
            style={{
              background: 'transparent',
              border: 'none',
              fontSize: '1.5rem',
              cursor: 'pointer',
              color: '#666'
            }}
          >
            ×
          </button>
        </div>
        {children}
      </div>
    </div>
  );
}
