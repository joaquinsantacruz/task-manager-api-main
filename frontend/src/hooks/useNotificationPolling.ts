import { useEffect, useRef } from 'react';

/**
 * useNotificationPolling - Custom hook for periodic notification updates
 * 
 * Following SOLID principles:
 * - Single Responsibility: Handles only polling logic
 * - Open/Closed: Configurable interval and easy to extend
 * 
 * @param callback - Function to call on each poll
 * @param interval - Polling interval in milliseconds (default: 30000 = 30 seconds)
 * @param enabled - Whether polling is enabled
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
