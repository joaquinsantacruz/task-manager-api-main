/**
 * Frontend Logging Utility
 * 
 * Provides centralized logging functionality for the frontend application.
 * Includes different log levels and optional console output control.
 * 
 * Features:
 *   - Multiple log levels (debug, info, warn, error)
 *   - Timestamps for all log entries
 *   - Optional disable in production
 *   - Structured log format
 *   - Error stack trace capture
 * 
 * @example
 * ```typescript
 * import logger from './utils/logger';
 * 
 * logger.info('User logged in', { userId: 123 });
 * logger.error('API call failed', { error, endpoint: '/tasks' });
 * logger.debug('Component rendered', { component: 'TaskList' });
 * ```
 */

export enum LogLevel {
  DEBUG = 'DEBUG',
  INFO = 'INFO',
  WARN = 'WARN',
  ERROR = 'ERROR'
}

interface LogEntry {
  timestamp: string;
  level: LogLevel;
  message: string;
  data?: any;
  error?: Error;
}

class Logger {
  private isDevelopment: boolean;
  private isEnabled: boolean;

  constructor() {
    this.isDevelopment = import.meta.env.DEV;
    this.isEnabled = true; // Can be toggled via setEnabled()
  }

  /**
   * Enable or disable logging
   */
  setEnabled(enabled: boolean): void {
    this.isEnabled = enabled;
  }

  /**
   * Format log entry with timestamp and structured data
   */
  private formatLog(level: LogLevel, message: string, data?: any): LogEntry {
    return {
      timestamp: new Date().toISOString(),
      level,
      message,
      ...(data && { data })
    };
  }

  /**
   * Log debug messages (only in development)
   */
  debug(message: string, data?: any): void {
    if (!this.isEnabled || !this.isDevelopment) return;
    
    const logEntry = this.formatLog(LogLevel.DEBUG, message, data);
    console.debug(`[${logEntry.timestamp}] [DEBUG] ${message}`, data || '');
  }

  /**
   * Log informational messages
   */
  info(message: string, data?: any): void {
    if (!this.isEnabled) return;
    
    const logEntry = this.formatLog(LogLevel.INFO, message, data);
    console.info(`[${logEntry.timestamp}] [INFO] ${message}`, data || '');
  }

  /**
   * Log warning messages
   */
  warn(message: string, data?: any): void {
    if (!this.isEnabled) return;
    
    const logEntry = this.formatLog(LogLevel.WARN, message, data);
    console.warn(`[${logEntry.timestamp}] [WARN] ${message}`, data || '');
  }

  /**
   * Log error messages with optional Error object
   */
  error(message: string, error?: Error | any, data?: any): void {
    if (!this.isEnabled) return;
    
    const logEntry = this.formatLog(LogLevel.ERROR, message, {
      ...data,
      ...(error && {
        error: {
          message: error.message,
          stack: error.stack,
          ...error
        }
      })
    });
    
    console.error(`[${logEntry.timestamp}] [ERROR] ${message}`, {
      error,
      ...data
    });
  }

  /**
   * Log API request
   */
  logRequest(method: string, url: string, data?: any): void {
    this.debug(`API Request: ${method} ${url}`, data);
  }

  /**
   * Log API response
   */
  logResponse(method: string, url: string, status: number, data?: any): void {
    if (status >= 400) {
      this.error(`API Error: ${method} ${url} - Status ${status}`, undefined, data);
    } else {
      this.debug(`API Response: ${method} ${url} - Status ${status}`, data);
    }
  }

  /**
   * Log user action
   */
  logUserAction(action: string, details?: any): void {
    this.info(`User Action: ${action}`, details);
  }
}

// Export singleton instance
const logger = new Logger();
export default logger;
