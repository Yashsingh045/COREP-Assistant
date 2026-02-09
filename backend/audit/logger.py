"""
Audit logging module for COREP Assistant.
Logs all queries and responses to JSON files for compliance and debugging.
"""
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional
from config import settings

logger = logging.getLogger(__name__)

# Default audit log directory
AUDIT_LOG_DIR = Path(__file__).parent.parent.parent / "logs"


class AuditLogger:
    """Audit logger for COREP queries and responses."""
    
    def __init__(self, log_dir: Optional[Path] = None):
        """
        Initialize audit logger.
        
        Args:
            log_dir: Directory to store audit logs (default: logs/)
        """
        self.log_dir = log_dir or AUDIT_LOG_DIR
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"Audit logger initialized with directory: {self.log_dir}")
    
    def log_query(
        self,
        question: str,
        scenario: str,
        template: str,
        corep_output: Dict[str, Any],
        retrieved_paragraphs: list,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Log a COREP query and its response.
        
        Args:
            question: User's question
            scenario: Bank scenario description
            template: COREP template code
            corep_output: Generated COREP output
            retrieved_paragraphs: Retrieved regulatory paragraphs
            metadata: Additional metadata (e.g., execution time)
        
        Returns:
            Path to the created log file
        """
        timestamp = datetime.now()
        log_id = timestamp.strftime("%Y%m%d_%H%M%S_%f")
        
        # Create audit log entry
        audit_entry = {
            "log_id": log_id,
            "timestamp": timestamp.isoformat(),
            "query": {
                "question": question,
                "scenario": scenario,
                "template": template
            },
            "response": corep_output,
            "retrieval": {
                "paragraphs_count": len(retrieved_paragraphs),
                "paragraphs": retrieved_paragraphs
            },
            "system": {
                "llm_model": settings.openai_model,
                "embedding_model": settings.openai_embedding_model,
                "environment": settings.environment
            },
            "metadata": metadata or {}
        }
        
        # Write to JSON file
        log_file = self.log_dir / f"audit_{log_id}.json"
        
        try:
            with open(log_file, 'w', encoding='utf-8') as f:
                json.dump(audit_entry, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Audit log created: {log_file}")
            return str(log_file)
        
        except Exception as e:
            logger.error(f"Failed to write audit log: {e}")
            raise
    
    def get_all_logs(self, limit: Optional[int] = None) -> list[Dict[str, Any]]:
        """
        Retrieve all audit logs, sorted by timestamp (newest first).
        
        Args:
            limit: Maximum number of logs to return
        
        Returns:
            List of audit log entries
        """
        log_files = sorted(
            self.log_dir.glob("audit_*.json"),
            key=lambda p: p.stat().st_mtime,
            reverse=True
        )
        
        if limit:
            log_files = log_files[:limit]
        
        logs = []
        for log_file in log_files:
            try:
                with open(log_file, 'r', encoding='utf-8') as f:
                    log_entry = json.load(f)
                    logs.append(log_entry)
            except Exception as e:
                logger.error(f"Failed to read log file {log_file}: {e}")
        
        return logs
    
    def get_log_by_id(self, log_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve a specific audit log by ID.
        
        Args:
            log_id: Log ID
        
        Returns:
            Audit log entry or None if not found
        """
        log_file = self.log_dir / f"audit_{log_id}.json"
        
        if not log_file.exists():
            return None
        
        try:
            with open(log_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to read log file {log_file}: {e}")
            return None


# Global audit logger instance
audit_logger = AuditLogger()
