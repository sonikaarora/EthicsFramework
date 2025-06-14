"""
Logging Configuration for Ethics-by-Design Framework
===================================================

Comprehensive logging setup with multiple handlers, formatters, and loggers
for different components of the framework.
"""

import logging
import logging.handlers
import os
import sys
import time
from typing import Dict, Any, Optional
from pathlib import Path
import json
from datetime import datetime


class JSONFormatter(logging.Formatter):
    """JSON formatter for structured logging"""
    
    def format(self, record):
        """Format log record as JSON"""
        log_entry = {
            'timestamp': datetime.fromtimestamp(record.created).isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno
        }
        
        # Add exception info if present
        if record.exc_info:
            log_entry['exception'] = self.formatException(record.exc_info)
        
        # Add extra fields
        for key, value in record.__dict__.items():
            if key not in ['name', 'msg', 'args', 'levelname', 'levelno', 'pathname',
                          'filename', 'module', 'lineno', 'funcName', 'created',
                          'msecs', 'relativeCreated', 'thread', 'threadName',
                          'processName', 'process', 'getMessage', 'exc_info',
                          'exc_text', 'stack_info']:
                log_entry[key] = value
        
        return json.dumps(log_entry)


class PerformanceFormatter(logging.Formatter):
    """Formatter optimized for performance metrics logging"""
    
    def format(self, record):
        """Format performance-related log records"""
        if hasattr(record, 'metrics'):
            metrics = record.metrics
            return f"{record.levelname} | {record.name} | {record.getMessage()} | " \
                   f"Latency: {metrics.get('latency_ms', 'N/A')}ms | " \
                   f"Throughput: {metrics.get('throughput', 'N/A')}/s | " \
                   f"Memory: {metrics.get('memory_mb', 'N/A')}MB"
        else:
            return super().format(record)


class ConstraintViolationFormatter(logging.Formatter):
    """Formatter for constraint violation logs"""
    
    def format(self, record):
        """Format constraint violation records"""
        if hasattr(record, 'violation'):
            violation = record.violation
            return f"{record.levelname} | VIOLATION | {violation.get('constraint_name', 'Unknown')} | " \
                   f"User: {violation.get('user_id', 'N/A')} | " \
                   f"Severity: {violation.get('severity', 'N/A')} | " \
                   f"Score: {violation.get('violation_score', 'N/A')} | " \
                   f"Message: {violation.get('message', record.getMessage())}"
        else:
            return super().format(record)


class EthicsFrameworkLogger:
    """Main logger configuration for the ethics framework"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.log_directory = Path(self.config.get('log_directory', 'logs'))
        self.log_level = self.config.get('log_level', 'INFO')
        self.max_file_size = self.config.get('max_file_size', '10MB')
        self.backup_count = self.config.get('backup_count', 5)
        self.enable_json_logging = self.config.get('enable_json_logging', True)
        self.enable_console_logging = self.config.get('enable_console_logging', True)
        
        # Create log directory
        self.log_directory.mkdir(exist_ok=True)
        
        # Setup loggers
        self._setup_loggers()
    
    def _setup_loggers(self):
        """Setup all framework loggers"""
        # Root logger configuration
        root_logger = logging.getLogger()
        root_logger.setLevel(getattr(logging, self.log_level.upper()))
        
        # Clear existing handlers
        root_logger.handlers.clear()
        
        # Setup main framework logger
        self._setup_main_logger()
        
        # Setup component-specific loggers
        self._setup_constraint_logger()
        self._setup_performance_logger()
        self._setup_experiment_logger()
        self._setup_optimization_logger()
        self._setup_audit_logger()
    
    def _setup_main_logger(self):
        """Setup main framework logger"""
        logger = logging.getLogger('ethics_framework')
        logger.setLevel(getattr(logging, self.log_level.upper()))
        
        # File handler
        file_handler = logging.handlers.RotatingFileHandler(
            self.log_directory / 'ethics_framework.log',
            maxBytes=self._parse_file_size(self.max_file_size),
            backupCount=self.backup_count
        )
        file_handler.setLevel(logging.DEBUG)
        
        # Console handler
        if self.enable_console_logging:
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(getattr(logging, self.log_level.upper()))
            
            # Formatter
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            console_handler.setFormatter(formatter)
            logger.addHandler(console_handler)
        
        # JSON file handler
        if self.enable_json_logging:
            json_handler = logging.handlers.RotatingFileHandler(
                self.log_directory / 'ethics_framework.json',
                maxBytes=self._parse_file_size(self.max_file_size),
                backupCount=self.backup_count
            )
            json_handler.setLevel(logging.DEBUG)
            json_handler.setFormatter(JSONFormatter())
            logger.addHandler(json_handler)
        
        # Standard file formatter
        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
        )
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)
    
    def _setup_constraint_logger(self):
        """Setup constraint validation logger"""
        logger = logging.getLogger('ethics_framework.constraints')
        logger.setLevel(logging.WARNING)  # Only log violations and errors
        
        # Constraint violations file
        violation_handler = logging.handlers.RotatingFileHandler(
            self.log_directory / 'constraint_violations.log',
            maxBytes=self._parse_file_size(self.max_file_size),
            backupCount=self.backup_count
        )
        violation_handler.setLevel(logging.WARNING)
        violation_handler.setFormatter(ConstraintViolationFormatter())
        logger.addHandler(violation_handler)
        
        # JSON violations for analysis
        if self.enable_json_logging:
            json_violation_handler = logging.handlers.RotatingFileHandler(
                self.log_directory / 'constraint_violations.json',
                maxBytes=self._parse_file_size(self.max_file_size),
                backupCount=self.backup_count
            )
            json_violation_handler.setLevel(logging.WARNING)
            json_violation_handler.setFormatter(JSONFormatter())
            logger.addHandler(json_violation_handler)
    
    def _setup_performance_logger(self):
        """Setup performance metrics logger"""
        logger = logging.getLogger('ethics_framework.performance')
        logger.setLevel(logging.INFO)
        
        # Performance metrics file
        perf_handler = logging.handlers.RotatingFileHandler(
            self.log_directory / 'performance_metrics.log',
            maxBytes=self._parse_file_size(self.max_file_size),
            backupCount=self.backup_count
        )
        perf_handler.setLevel(logging.INFO)
        perf_handler.setFormatter(PerformanceFormatter())
        logger.addHandler(perf_handler)
        
        # JSON performance data
        if self.enable_json_logging:
            json_perf_handler = logging.handlers.RotatingFileHandler(
                self.log_directory / 'performance_metrics.json',
                maxBytes=self._parse_file_size(self.max_file_size),
                backupCount=self.backup_count
            )
            json_perf_handler.setLevel(logging.INFO)
            json_perf_handler.setFormatter(JSONFormatter())
            logger.addHandler(json_perf_handler)
    
    def _setup_experiment_logger(self):
        """Setup experiment runner logger"""
        logger = logging.getLogger('ethics_framework.experiments')
        logger.setLevel(logging.DEBUG)
        
        # Experiment log file
        exp_handler = logging.handlers.RotatingFileHandler(
            self.log_directory / 'experiments.log',
            maxBytes=self._parse_file_size(self.max_file_size),
            backupCount=self.backup_count
        )
        exp_handler.setLevel(logging.DEBUG)
        
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - [%(experiment_id)s] - %(message)s'
        )
        exp_handler.setFormatter(formatter)
        logger.addHandler(exp_handler)
    
    def _setup_optimization_logger(self):
        """Setup optimization algorithm logger"""
        logger = logging.getLogger('ethics_framework.optimization')
        logger.setLevel(logging.INFO)
        
        # Optimization log file
        opt_handler = logging.handlers.RotatingFileHandler(
            self.log_directory / 'optimization.log',
            maxBytes=self._parse_file_size(self.max_file_size),
            backupCount=self.backup_count
        )
        opt_handler.setLevel(logging.INFO)
        
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - [Iter %(iteration)s] - %(message)s'
        )
        opt_handler.setFormatter(formatter)
        logger.addHandler(opt_handler)
    
    def _setup_audit_logger(self):
        """Setup audit trail logger"""
        logger = logging.getLogger('ethics_framework.audit')
        logger.setLevel(logging.INFO)
        
        # Audit trail file (append-only, no rotation for compliance)
        audit_handler = logging.FileHandler(
            self.log_directory / 'audit_trail.log'
        )
        audit_handler.setLevel(logging.INFO)
        
        # Audit entries should be immutable and timestamped
        audit_formatter = logging.Formatter(
            '%(asctime)s - AUDIT - %(message)s'
        )
        audit_handler.setFormatter(audit_formatter)
        logger.addHandler(audit_handler)
        
        # JSON audit trail for analysis
        if self.enable_json_logging:
            json_audit_handler = logging.FileHandler(
                self.log_directory / 'audit_trail.json'
            )
            json_audit_handler.setLevel(logging.INFO)
            json_audit_handler.setFormatter(JSONFormatter())
            logger.addHandler(json_audit_handler)
    
    def _parse_file_size(self, size_str: str) -> int:
        """Parse file size string to bytes"""
        size_str = size_str.upper()
        if size_str.endswith('KB'):
            return int(size_str[:-2]) * 1024
        elif size_str.endswith('MB'):
            return int(size_str[:-2]) * 1024 * 1024
        elif size_str.endswith('GB'):
            return int(size_str[:-2]) * 1024 * 1024 * 1024
        else:
            return int(size_str)
    
    def get_logger(self, name: str) -> logging.Logger:
        """Get a logger with the specified name"""
        return logging.getLogger(f'ethics_framework.{name}')
    
    def log_constraint_violation(self, violation: Dict[str, Any], 
                               decision: Dict[str, Any] = None):
        """Log a constraint violation"""
        logger = logging.getLogger('ethics_framework.constraints')
        
        # Add decision context to violation
        if decision:
            violation['user_id'] = decision.get('user_id')
            violation['content_id'] = decision.get('content_id')
            violation['algorithm'] = decision.get('algorithm')
        
        logger.warning(
            f"Constraint violation: {violation.get('constraint_name')}",
            extra={'violation': violation}
        )
    
    def log_performance_metrics(self, metrics: Dict[str, Any], 
                              operation: str = "unknown"):
        """Log performance metrics"""
        logger = logging.getLogger('ethics_framework.performance')
        
        logger.info(
            f"Performance metrics for {operation}",
            extra={'metrics': metrics}
        )
    
    def log_experiment_event(self, event: str, experiment_id: str, 
                           data: Dict[str, Any] = None):
        """Log experiment event"""
        logger = logging.getLogger('ethics_framework.experiments')
        
        extra = {'experiment_id': experiment_id}
        if data:
            extra.update(data)
        
        logger.info(event, extra=extra)
    
    def log_optimization_step(self, iteration: int, objective_value: float,
                            parameters: Dict[str, Any] = None):
        """Log optimization step"""
        logger = logging.getLogger('ethics_framework.optimization')
        
        extra = {'iteration': iteration}
        if parameters:
            extra.update(parameters)
        
        logger.info(
            f"Optimization step completed - Objective: {objective_value:.6f}",
            extra=extra
        )
    
    def log_audit_event(self, event_type: str, user_id: Optional[int] = None,
                       decision_id: Optional[str] = None, 
                       details: Dict[str, Any] = None):
        """Log audit event"""
        logger = logging.getLogger('ethics_framework.audit')
        
        audit_entry = {
            'event_type': event_type,
            'timestamp': datetime.now().isoformat(),
            'user_id': user_id,
            'decision_id': decision_id
        }
        
        if details:
            audit_entry.update(details)
        
        logger.info(
            f"Audit event: {event_type}",
            extra=audit_entry
        )


# Global logger instance
_logger_instance: Optional[EthicsFrameworkLogger] = None


def setup_logging(config: Dict[str, Any] = None) -> EthicsFrameworkLogger:
    """Setup framework logging with configuration"""
    global _logger_instance
    
    if _logger_instance is None:
        _logger_instance = EthicsFrameworkLogger(config)
    
    return _logger_instance


def get_logger(name: str = 'main') -> logging.Logger:
    """Get a framework logger"""
    if _logger_instance is None:
        setup_logging()
    
    return _logger_instance.get_logger(name)


def log_constraint_violation(violation: Dict[str, Any], 
                           decision: Dict[str, Any] = None):
    """Convenience function to log constraint violations"""
    if _logger_instance is None:
        setup_logging()
    
    _logger_instance.log_constraint_violation(violation, decision)


def log_performance_metrics(metrics: Dict[str, Any], operation: str = "unknown"):
    """Convenience function to log performance metrics"""
    if _logger_instance is None:
        setup_logging()
    
    _logger_instance.log_performance_metrics(metrics, operation)


def log_experiment_event(event: str, experiment_id: str, 
                        data: Dict[str, Any] = None):
    """Convenience function to log experiment events"""
    if _logger_instance is None:
        setup_logging()
    
    _logger_instance.log_experiment_event(event, experiment_id, data)


def log_optimization_step(iteration: int, objective_value: float,
                         parameters: Dict[str, Any] = None):
    """Convenience function to log optimization steps"""
    if _logger_instance is None:
        setup_logging()
    
    _logger_instance.log_optimization_step(iteration, objective_value, parameters)


def log_audit_event(event_type: str, user_id: Optional[int] = None,
                   decision_id: Optional[str] = None, 
                   details: Dict[str, Any] = None):
    """Convenience function to log audit events"""
    if _logger_instance is None:
        setup_logging()
    
    _logger_instance.log_audit_event(event_type, user_id, decision_id, details)


# Example usage and testing
if __name__ == "__main__":
    # Test logging configuration
    config = {
        'log_level': 'DEBUG',
        'log_directory': 'test_logs',
        'max_file_size': '1MB',
        'backup_count': 3,
        'enable_json_logging': True,
        'enable_console_logging': True
    }
    
    # Setup logging
    framework_logger = setup_logging(config)
    
    # Test different loggers
    main_logger = get_logger('main')
    main_logger.info("Framework logging initialized")
    
    # Test constraint violation logging
    violation = {
        'constraint_name': 'fairness',
        'constraint_type': 'FAIRNESS',
        'severity': 'HIGH',
        'violation_score': 0.8,
        'message': 'Demographic parity violation detected'
    }
    
    decision = {
        'user_id': 12345,
        'content_id': 67890,
        'algorithm': 'recommendation'
    }
    
    log_constraint_violation(violation, decision)
    
    # Test performance metrics logging
    metrics = {
        'latency_ms': 2.5,
        'throughput': 15000,
        'memory_mb': 128.5,
        'cache_hit_rate': 0.85
    }
    
    log_performance_metrics(metrics, "constraint_validation")
    
    # Test experiment logging
    log_experiment_event("Experiment started", "exp_001", {'scenario': 'social_media'})
    
    # Test optimization logging
    log_optimization_step(1, 0.234567, {'learning_rate': 0.01, 'momentum': 0.9})
    
    # Test audit logging
    log_audit_event("decision_processed", user_id=12345, decision_id="dec_001", 
                    details={'approved': True, 'constraints_satisfied': 4})
    
    print("Logging test completed. Check test_logs directory for output files.") 