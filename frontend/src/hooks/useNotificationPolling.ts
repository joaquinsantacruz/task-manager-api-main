import { useEffect, useRef } from 'react';

/**
 * useNotificationPolling - Custom hook for periodic notification updates
 * 
 * Implements a polling mechanism to periodically execute a callback function.
 * Commonly used to fetch new notifications at regular intervals without user interaction.
 * 
 * Following SOLID principles:
 *   - Single Responsibility: Handles only polling logic
 *   - Open/Closed: Configurable interval and easy to extend
 * 
 * @param callback - Function to call on each poll (can be sync or async)
 * @param interval - Polling interval in milliseconds (default: 30000 = 30 seconds)
 * @param enabled - Whether polling is active (default: true)
 * 
 * @example
 * ```tsx
 * // Poll for new notifications every 30 seconds
 * useNotificationPolling(fetchNotifications, 30000, true);
 * 
 * // Poll more frequently (every 10 seconds)
 * useNotificationPolling(fetchNotifications, 10000, isUserActive);
 * 
 * // Disable polling
 * useNotificationPolling(fetchNotifications, 30000, false);
 * ```
 * 
 * Features:
 *   - Automatic cleanup on unmount to prevent memory leaks
 *   - Can be enabled/disabled dynamically
 *   - Handles both synchronous and asynchronous callbacks
 *   - Uses refs to avoid stale closures
 * 
 * Performance:
 *   - Uses ref to store callback, preventing unnecessary interval resets
 *   - Automatically clears interval when disabled or unmounted
 *   - Configurable interval for different update frequencies
 * 
 * Note:
 *   - Callback is executed immediately on interval, not on mount
 *   - For immediate execution on mount, call callback in useEffect separately
 */
export const useNotificationPolling = (
  callback: () => void | Promise<void>,
  interval: number = 30000,
  enabled: boolean = true
) => {
  const savedCallback = useRef(callback);
  const intervalIdRef = useRef<NodeJS.Timeout | null>(null);

  // Update the callback ref when it changes
  useEffect(() => {
    savedCallback.current = callback;
  }, [callback]);

  useEffect(() => {
    if (!enabled) {
      // Clear any existing interval if polling is disabled
      if (intervalIdRef.current) {
        clearInterval(intervalIdRef.current);
        intervalIdRef.current = null;
      }
      return;
    }

    // Set up the polling interval
    intervalIdRef.current = setInterval(() => {
      savedCallback.current();
    }, interval);

    // Cleanup on unmount or when dependencies change
    return () => {
      if (intervalIdRef.current) {
        clearInterval(intervalIdRef.current);
        intervalIdRef.current = null;
      }
    };
  }, [interval, enabled]);
};
