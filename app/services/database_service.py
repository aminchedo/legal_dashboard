"""
Database Service for Legal Dashboard
==================================

Advanced database management with full-text search, document versioning,
audit trails, and performance optimizations for legal document processing.
"""

import sqlite3
import json
import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
import hashlib
import os
from pathlib import Path
import threading
from contextlib import contextmanager

logger = logging.getLogger(__name__)


class DatabaseManager:
    """
    Advanced database manager with full-text search and document versioning
    """

    def __init__(self, db_path: str = "legal_documents.db"):
        """Initialize database manager"""
        self.db_path = db_path
        self.connection = None
        self.lock = threading.Lock()
        self.initialized = False

        # Performance optimization settings
        self.batch_size = 100
        self.cache_size = 1000
        self.enable_wal = True

    def initialize(self):
        """Initialize database with advanced features"""
        if self.initialized:
            return

        try:
            with self._get_connection() as conn:
                # Enable WAL mode for better concurrency
                if self.enable_wal:
                    conn.execute("PRAGMA journal_mode=WAL")

                # Set cache size for better performance
                conn.execute(f"PRAGMA cache_size={self.cache_size}")

                # Enable foreign keys
                conn.execute("PRAGMA foreign_keys=ON")

                # Create tables with advanced features
                self._create_tables(conn)

                # Create indexes for better performance
                self._create_indexes(conn)

                # Initialize full-text search
                self._initialize_fulltext_search(conn)

                self.initialized = True
                logger.info(
                    "✅ Database initialized successfully with advanced features")

        except Exception as e:
            logger.error(f"❌ Database initialization failed: {e}")
            raise

    def _create_tables(self, conn: sqlite3.Connection):
        """Create database tables with advanced features"""

        # Main documents table with versioning support
        conn.execute("""
            CREATE TABLE IF NOT EXISTS documents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                full_text TEXT NOT NULL,
                source TEXT,
                category TEXT,
                ai_score REAL DEFAULT 0.0,
                ocr_confidence REAL DEFAULT 0.0,
                file_path TEXT,
                file_size INTEGER,
                mime_type TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                version INTEGER DEFAULT 1,
                parent_id INTEGER,
                status TEXT DEFAULT 'active',
                metadata TEXT,
                FOREIGN KEY (parent_id) REFERENCES documents(id)
            )
        """)

        # Document versions table for versioning
        conn.execute("""
            CREATE TABLE IF NOT EXISTS document_versions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                document_id INTEGER NOT NULL,
                version_number INTEGER NOT NULL,
                title TEXT NOT NULL,
                full_text TEXT NOT NULL,
                ai_score REAL,
                ocr_confidence REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                created_by TEXT,
                change_summary TEXT,
                FOREIGN KEY (document_id) REFERENCES documents(id)
            )
        """)

        # Full-text search table
        conn.execute("""
            CREATE VIRTUAL TABLE IF NOT EXISTS documents_fts USING fts5(
                title, full_text, category, source,
                content='documents',
                content_rowid='id'
            )
        """)

        # Audit trail table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS audit_trail (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                table_name TEXT NOT NULL,
                record_id INTEGER NOT NULL,
                action TEXT NOT NULL,
                old_values TEXT,
                new_values TEXT,
                user_id TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                ip_address TEXT,
                user_agent TEXT
            )
        """)

        # AI analysis cache table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS ai_analysis_cache (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                document_id INTEGER NOT NULL,
                analysis_type TEXT NOT NULL,
                analysis_data TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP,
                FOREIGN KEY (document_id) REFERENCES documents(id)
            )
        """)

        # Document relationships table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS document_relationships (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source_document_id INTEGER NOT NULL,
                target_document_id INTEGER NOT NULL,
                relationship_type TEXT NOT NULL,
                similarity_score REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (source_document_id) REFERENCES documents(id),
                FOREIGN KEY (target_document_id) REFERENCES documents(id)
            )
        """)

        # System metrics table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS system_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                metric_name TEXT NOT NULL,
                metric_value REAL NOT NULL,
                metric_unit TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                metadata TEXT
            )
        """)

    def _create_indexes(self, conn: sqlite3.Connection):
        """Create performance indexes"""

        # Main document indexes
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_documents_category ON documents(category)")
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_documents_created_at ON documents(created_at)")
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_documents_ai_score ON documents(ai_score)")
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_documents_status ON documents(status)")

        # Version indexes
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_versions_document_id ON document_versions(document_id)")
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_versions_version_number ON document_versions(version_number)")

        # Audit trail indexes
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_audit_table_record ON audit_trail(table_name, record_id)")
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_audit_timestamp ON audit_trail(timestamp)")

        # AI analysis cache indexes
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_ai_cache_document ON ai_analysis_cache(document_id)")
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_ai_cache_expires ON ai_analysis_cache(expires_at)")

        # Relationship indexes
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_relationships_source ON document_relationships(source_document_id)")
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_relationships_target ON document_relationships(target_document_id)")

    def _initialize_fulltext_search(self, conn: sqlite3.Connection):
        """Initialize full-text search triggers"""

        # Trigger to update FTS table on document insert
        conn.execute("""
            CREATE TRIGGER IF NOT EXISTS documents_ai AFTER INSERT ON documents BEGIN
                INSERT INTO documents_fts(rowid, title, full_text, category, source)
                VALUES (new.id, new.title, new.full_text, new.category, new.source);
            END
        """)

        # Trigger to update FTS table on document update
        conn.execute("""
            CREATE TRIGGER IF NOT EXISTS documents_ad AFTER DELETE ON documents BEGIN
                INSERT INTO documents_fts(documents_fts, rowid, title, full_text, category, source)
                VALUES('delete', old.id, old.title, old.full_text, old.category, old.source);
            END
        """)

        # Trigger to update FTS table on document update
        conn.execute("""
            CREATE TRIGGER IF NOT EXISTS documents_au AFTER UPDATE ON documents BEGIN
                INSERT INTO documents_fts(documents_fts, rowid, title, full_text, category, source)
                VALUES('delete', old.id, old.title, old.full_text, old.category, old.source);
                INSERT INTO documents_fts(rowid, title, full_text, category, source)
                VALUES (new.id, new.title, new.full_text, new.category, new.source);
            END
        """)

    @contextmanager
    def _get_connection(self):
        """Get database connection with proper error handling"""
        conn = None
        try:
            conn = sqlite3.connect(self.db_path, check_same_thread=False)
            conn.row_factory = sqlite3.Row
            yield conn
        except Exception as e:
            logger.error(f"Database connection error: {e}")
            raise
        finally:
            if conn:
                conn.close()

    def is_connected(self) -> bool:
        """Check if database is connected and initialized"""
        return self.initialized

    def create_document(self, document_data: Dict[str, Any]) -> int:
        """Create a new document with versioning support"""
        try:
            with self._get_connection() as conn:
                # Generate document hash for deduplication
                content_hash = hashlib.md5(
                    document_data.get('full_text', '').encode()
                ).hexdigest()

                # Check for duplicate
                existing = conn.execute(
                    "SELECT id FROM documents WHERE full_text = ?",
                    (document_data.get('full_text', ''),)
                ).fetchone()

                if existing:
                    logger.warning(
                        f"Duplicate document detected: {existing['id']}")
                    return existing['id']

                # Insert new document
                cursor = conn.execute("""
                    INSERT INTO documents (
                        title, full_text, source, category, ai_score, 
                        ocr_confidence, file_path, file_size, mime_type, metadata
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    document_data.get('title', ''),
                    document_data.get('full_text', ''),
                    document_data.get('source', ''),
                    document_data.get('category', ''),
                    document_data.get('ai_score', 0.0),
                    document_data.get('ocr_confidence', 0.0),
                    document_data.get('file_path', ''),
                    document_data.get('file_size', 0),
                    document_data.get('mime_type', ''),
                    json.dumps(document_data.get('metadata', {}))
                ))

                document_id = cursor.lastrowid

                # Create initial version
                self._create_document_version(
                    conn, document_id, document_data, "Initial version")

                # Log audit trail
                self._log_audit_trail(conn, 'documents', document_id, 'CREATE',
                                      None, document_data)

                logger.info(f"✅ Document created successfully: {document_id}")
                return document_id

        except Exception as e:
            logger.error(f"❌ Error creating document: {e}")
            raise

    def _create_document_version(self, conn: sqlite3.Connection, document_id: int,
                                 document_data: Dict[str, Any], change_summary: str):
        """Create a new document version"""
        conn.execute("""
            INSERT INTO document_versions (
                document_id, version_number, title, full_text, 
                ai_score, ocr_confidence, created_by, change_summary
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            document_id,
            document_data.get('version', 1),
            document_data.get('title', ''),
            document_data.get('full_text', ''),
            document_data.get('ai_score', 0.0),
            document_data.get('ocr_confidence', 0.0),
            document_data.get('created_by', 'system'),
            change_summary
        ))

    def get_document(self, document_id: int) -> Optional[Dict[str, Any]]:
        """Get document by ID with full metadata"""
        try:
            with self._get_connection() as conn:
                document = conn.execute("""
                    SELECT * FROM documents WHERE id = ? AND status = 'active'
                """, (document_id,)).fetchone()

                if document:
                    doc_dict = dict(document)
                    # Parse metadata JSON
                    if doc_dict.get('metadata'):
                        doc_dict['metadata'] = json.loads(doc_dict['metadata'])
                    return doc_dict
                return None

        except Exception as e:
            logger.error(f"❌ Error getting document {document_id}: {e}")
            return None

    def update_document(self, document_id: int, update_data: Dict[str, Any]) -> bool:
        """Update document with versioning support"""
        try:
            with self._get_connection() as conn:
                # Get current document
                current_doc = self.get_document(document_id)
                if not current_doc:
                    return False

                # Create new version
                version_data = {**current_doc, **update_data}
                version_data['version'] = current_doc.get('version', 1) + 1

                self._create_document_version(
                    conn, document_id, version_data,
                    update_data.get('change_summary', 'Document updated')
                )

                # Update main document
                conn.execute("""
                    UPDATE documents SET 
                        title = ?, full_text = ?, source = ?, category = ?,
                        ai_score = ?, ocr_confidence = ?, updated_at = CURRENT_TIMESTAMP,
                        version = ?, metadata = ?
                    WHERE id = ?
                """, (
                    version_data.get('title', ''),
                    version_data.get('full_text', ''),
                    version_data.get('source', ''),
                    version_data.get('category', ''),
                    version_data.get('ai_score', 0.0),
                    version_data.get('ocr_confidence', 0.0),
                    version_data.get('version', 1),
                    json.dumps(version_data.get('metadata', {})),
                    document_id
                ))

                # Log audit trail
                self._log_audit_trail(conn, 'documents', document_id, 'UPDATE',
                                      current_doc, version_data)

                logger.info(f"✅ Document {document_id} updated successfully")
                return True

        except Exception as e:
            logger.error(f"❌ Error updating document {document_id}: {e}")
            return False

    def delete_document(self, document_id: int) -> bool:
        """Soft delete document (mark as inactive)"""
        try:
            with self._get_connection() as conn:
                # Get current document for audit trail
                current_doc = self.get_document(document_id)
                if not current_doc:
                    return False

                # Soft delete
                conn.execute("""
                    UPDATE documents SET status = 'deleted', updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                """, (document_id,))

                # Log audit trail
                self._log_audit_trail(conn, 'documents', document_id, 'DELETE',
                                      current_doc, None)

                logger.info(f"✅ Document {document_id} deleted successfully")
                return True

        except Exception as e:
            logger.error(f"❌ Error deleting document {document_id}: {e}")
            return False

    def search_documents(self, query: str, filters: Dict = None,
                         limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
        """Advanced document search with full-text capabilities"""
        try:
            with self._get_connection() as conn:
                # Build search query
                search_sql = """
                    SELECT d.*, 
                           rank as search_rank
                    FROM documents d
                    LEFT JOIN documents_fts fts ON d.id = fts.rowid
                    WHERE d.status = 'active'
                """

                params = []

                # Add full-text search
                if query.strip():
                    search_sql += " AND documents_fts MATCH ?"
                    params.append(query)

                # Add filters
                if filters:
                    if filters.get('category'):
                        search_sql += " AND d.category = ?"
                        params.append(filters['category'])

                    if filters.get('source'):
                        search_sql += " AND d.source = ?"
                        params.append(filters['source'])

                    if filters.get('min_score'):
                        search_sql += " AND d.ai_score >= ?"
                        params.append(filters['min_score'])

                    if filters.get('date_from'):
                        search_sql += " AND d.created_at >= ?"
                        params.append(filters['date_from'])

                    if filters.get('date_to'):
                        search_sql += " AND d.created_at <= ?"
                        params.append(filters['date_to'])

                # Add ordering and pagination
                search_sql += " ORDER BY search_rank DESC, d.created_at DESC"
                search_sql += " LIMIT ? OFFSET ?"
                params.extend([limit, offset])

                # Execute search
                results = conn.execute(search_sql, params).fetchall()

                # Convert to dictionaries and parse metadata
                documents = []
                for row in results:
                    doc_dict = dict(row)
                    if doc_dict.get('metadata'):
                        doc_dict['metadata'] = json.loads(doc_dict['metadata'])
                    documents.append(doc_dict)

                return documents

        except Exception as e:
            logger.error(f"❌ Error searching documents: {e}")
            return []

    def get_document_versions(self, document_id: int) -> List[Dict[str, Any]]:
        """Get all versions of a document"""
        try:
            with self._get_connection() as conn:
                versions = conn.execute("""
                    SELECT * FROM document_versions 
                    WHERE document_id = ? 
                    ORDER BY version_number DESC
                """, (document_id,)).fetchall()

                return [dict(version) for version in versions]

        except Exception as e:
            logger.error(f"❌ Error getting document versions: {e}")
            return []

    def get_document_statistics(self) -> Dict[str, Any]:
        """Get comprehensive document statistics"""
        try:
            with self._get_connection() as conn:
                stats = {}

                # Basic counts
                stats['total_documents'] = conn.execute(
                    "SELECT COUNT(*) FROM documents WHERE status = 'active'"
                ).fetchone()[0]

                stats['total_versions'] = conn.execute(
                    "SELECT COUNT(*) FROM document_versions"
                ).fetchone()[0]

                # Category distribution
                category_stats = conn.execute("""
                    SELECT category, COUNT(*) as count 
                    FROM documents 
                    WHERE status = 'active' 
                    GROUP BY category
                """).fetchall()
                stats['category_distribution'] = {
                    row['category']: row['count'] for row in category_stats}

                # Quality metrics
                quality_stats = conn.execute("""
                    SELECT 
                        AVG(ai_score) as avg_ai_score,
                        AVG(ocr_confidence) as avg_ocr_confidence,
                        COUNT(CASE WHEN ai_score > 0.8 THEN 1 END) as high_quality_count
                    FROM documents 
                    WHERE status = 'active'
                """).fetchone()

                stats['quality_metrics'] = {
                    'avg_ai_score': quality_stats['avg_ai_score'] or 0.0,
                    'avg_ocr_confidence': quality_stats['avg_ocr_confidence'] or 0.0,
                    'high_quality_count': quality_stats['high_quality_count'] or 0
                }

                # Recent activity
                recent_stats = conn.execute("""
                    SELECT COUNT(*) as recent_count
                    FROM documents 
                    WHERE status = 'active' 
                    AND created_at >= datetime('now', '-7 days')
                """).fetchone()
                stats['recent_activity'] = recent_stats['recent_count'] or 0

                return stats

        except Exception as e:
            logger.error(f"❌ Error getting document statistics: {e}")
            return {}

    def cache_ai_analysis(self, document_id: int, analysis_type: str,
                          analysis_data: Dict[str, Any], ttl_hours: int = 24):
        """Cache AI analysis results"""
        try:
            with self._get_connection() as conn:
                expires_at = datetime.now() + timedelta(hours=ttl_hours)

                conn.execute("""
                    INSERT OR REPLACE INTO ai_analysis_cache (
                        document_id, analysis_type, analysis_data, expires_at
                    ) VALUES (?, ?, ?, ?)
                """, (
                    document_id, analysis_type,
                    json.dumps(analysis_data), expires_at.isoformat()
                ))

        except Exception as e:
            logger.error(f"❌ Error caching AI analysis: {e}")

    def get_cached_ai_analysis(self, document_id: int, analysis_type: str) -> Optional[Dict[str, Any]]:
        """Get cached AI analysis results"""
        try:
            with self._get_connection() as conn:
                result = conn.execute("""
                    SELECT analysis_data FROM ai_analysis_cache 
                    WHERE document_id = ? AND analysis_type = ? 
                    AND expires_at > datetime('now')
                """, (document_id, analysis_type)).fetchone()

                if result:
                    return json.loads(result['analysis_data'])
                return None

        except Exception as e:
            logger.error(f"❌ Error getting cached AI analysis: {e}")
            return None

    def _log_audit_trail(self, conn: sqlite3.Connection, table_name: str,
                         record_id: int, action: str, old_values: Dict = None,
                         new_values: Dict = None):
        """Log audit trail entry"""
        try:
            conn.execute("""
                INSERT INTO audit_trail (
                    table_name, record_id, action, old_values, new_values
                ) VALUES (?, ?, ?, ?, ?)
            """, (
                table_name, record_id, action,
                json.dumps(old_values) if old_values else None,
                json.dumps(new_values) if new_values else None
            ))
        except Exception as e:
            logger.error(f"❌ Error logging audit trail: {e}")

    def get_audit_trail(self, table_name: str = None, record_id: int = None,
                        limit: int = 100) -> List[Dict[str, Any]]:
        """Get audit trail entries"""
        try:
            with self._get_connection() as conn:
                sql = "SELECT * FROM audit_trail WHERE 1=1"
                params = []

                if table_name:
                    sql += " AND table_name = ?"
                    params.append(table_name)

                if record_id:
                    sql += " AND record_id = ?"
                    params.append(record_id)

                sql += " ORDER BY timestamp DESC LIMIT ?"
                params.append(limit)

                results = conn.execute(sql, params).fetchall()
                return [dict(row) for row in results]

        except Exception as e:
            logger.error(f"❌ Error getting audit trail: {e}")
            return []

    def cleanup_expired_cache(self):
        """Clean up expired AI analysis cache"""
        try:
            with self._get_connection() as conn:
                deleted = conn.execute("""
                    DELETE FROM ai_analysis_cache 
                    WHERE expires_at < datetime('now')
                """).rowcount

                if deleted > 0:
                    logger.info(
                        f"🧹 Cleaned up {deleted} expired cache entries")

        except Exception as e:
            logger.error(f"❌ Error cleaning up expired cache: {e}")

    def optimize_database(self):
        """Optimize database performance"""
        try:
            with self._get_connection() as conn:
                # Analyze tables for better query planning
                conn.execute("ANALYZE")

                # Vacuum to reclaim space
                conn.execute("VACUUM")

                # Rebuild indexes
                conn.execute("REINDEX")

                logger.info("✅ Database optimization completed")

        except Exception as e:
            logger.error(f"❌ Error optimizing database: {e}")

    def backup_database(self, backup_path: str):
        """Create database backup"""
        try:
            import shutil
            shutil.copy2(self.db_path, backup_path)
            logger.info(f"✅ Database backed up to: {backup_path}")
        except Exception as e:
            logger.error(f"❌ Error backing up database: {e}")

    def get_system_metrics(self) -> Dict[str, Any]:
        """Get system performance metrics"""
        try:
            with self._get_connection() as conn:
                # Database size
                db_size = os.path.getsize(
                    self.db_path) if os.path.exists(self.db_path) else 0

                # Table sizes
                table_sizes = {}
                tables = ['documents', 'document_versions',
                          'audit_trail', 'ai_analysis_cache']
                for table in tables:
                    count = conn.execute(
                        f"SELECT COUNT(*) FROM {table}").fetchone()[0]
                    table_sizes[table] = count

                # Performance metrics
                performance = conn.execute("""
                    SELECT 
                        COUNT(*) as total_queries,
                        AVG(metric_value) as avg_response_time
                    FROM system_metrics 
                    WHERE metric_name = 'query_response_time'
                    AND timestamp >= datetime('now', '-1 hour')
                """).fetchone()

                return {
                    'database_size_mb': round(db_size / (1024 * 1024), 2),
                    'table_sizes': table_sizes,
                    'performance_metrics': {
                        'total_queries': performance['total_queries'] or 0,
                        'avg_response_time_ms': performance['avg_response_time'] or 0
                    }
                }

        except Exception as e:
            logger.error(f"❌ Error getting system metrics: {e}")
            return {}
