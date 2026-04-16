import logging
import sys
from datetime import datetime
from pathlib import Path

class TestLogger:
    _loggers = {}
    
    @classmethod
    def get_logger(cls, name, log_file=None, level=logging.INFO):
        if name in cls._loggers:
            return cls._loggers[name]
        
        logger = logging.getLogger(name)
        logger.setLevel(level)
        
        if not logger.handlers:
            formatter = logging.Formatter(
                '%(asctime)s | %(name)s | %(levelname)s | %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(level)
            console_handler.setFormatter(formatter)
            logger.addHandler(console_handler)
            
            if log_file:
                log_path = Path(log_file)
                log_path.parent.mkdir(parents=True, exist_ok=True)
                file_handler = logging.FileHandler(log_file)
                file_handler.setLevel(level)
                file_handler.setFormatter(formatter)
                logger.addHandler(file_handler)
        
        cls._loggers[name] = logger
        return logger
    
    @classmethod
    def test_start(cls, test_name, module=None):
        logger = cls.get_logger('test.lifecycle')
        logger.info(f"START: {test_name} (module: {module or 'unknown'})")
    
    @classmethod
    def test_end(cls, test_name, status='PASSED', duration=None):
        logger = cls.get_logger('test.lifecycle')
        duration_str = f" ({duration:.2f}s)" if duration else ""
        logger.info(f"END: {test_name} [{status}]{duration_str}")
    
    @classmethod
    def test_step(cls, step_name, status='INFO'):
        logger = cls.get_logger('test.steps')
        logger.info(f"  STEP: {step_name} [{status}]")
    
    @classmethod
    def api_request(cls, method, url, status_code=None, duration=None):
        logger = cls.get_logger('api.requests')
        status_str = f" ({status_code})" if status_code else ""
        duration_str = f" in {duration:.3f}s" if duration else ""
        logger.info(f"API {method} {url}{status_str}{duration_str}")
    
    @classmethod
    def db_operation(cls, operation, table, rows=None):
        logger = cls.get_logger('db.operations')
        rows_str = f" ({rows} rows)" if rows is not None else ""
        logger.info(f"DB {operation} on {table}{rows_str}")
    
    @classmethod
    def ui_action(cls, action, element, page=None):
        logger = cls.get_logger('ui.actions')
        page_str = f" on {page}" if page else ""
        logger.info(f"UI {action}: {element}{page_str}")
    
    @classmethod
    def assertion(cls, description, expected, actual, passed):
        logger = cls.get_logger('test.assertions')
        status = "PASS" if passed else "FAIL"
        logger.info(f"ASSERT [{status}]: {description} - expected={expected}, actual={actual}")

logger = TestLogger
