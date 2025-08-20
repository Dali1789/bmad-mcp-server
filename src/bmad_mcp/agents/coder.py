"""
BMAD Coder Agent - Advanced Semantic Code Analysis and Editing
Advanced semantic code analysis and precise code editing
"""

import asyncio
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
import subprocess
import os
import tempfile

logger = logging.getLogger(__name__)

class BMadCoderAgent:
    """
    Advanced Coding Agent mit semantischer Code-Analyse
    
    Features inspiriert von semantic code analysis MCP:
    - Symbolbasierte Code-Navigation
    - Semantische Code-Suche  
    - Präzise Code-Editierung
    - Language Server Integration
    - Intelligent Code Completion
    """
    
    def __init__(self, project_path: str = None):
        self.project_path = Path(project_path) if project_path else Path.cwd()
        self.memories = {}
        self.active_project = None
        self.language_servers = {}
        
    async def activate_project(self, project_path: str, project_name: str = None) -> Dict[str, Any]:
        """
        Aktiviert ein Projekt für semantische Code-Analyse
        
        Args:
            project_path: Absoluter Pfad zum Projekt
            project_name: Optionaler Projektname
            
        Returns:
            Projekt-Informationen und Status
        """
        try:
            self.project_path = Path(project_path)
            self.active_project = project_name or self.project_path.name
            
            # Projekt-Struktur analysieren
            project_info = await self._analyze_project_structure()
            
            # semantic code analysis-Integration Setup
            await self._setup_semantic_integration()
            
            logger.info(f"Projekt '{self.active_project}' erfolgreich aktiviert")
            
            return {
                "status": "success",
                "project_name": self.active_project,
                "project_path": str(self.project_path),
                "project_info": project_info,
                "semantic_integration": True
            }
            
        except Exception as e:
            logger.error(f"Fehler beim Aktivieren des Projekts: {e}")
            return {"status": "error", "message": str(e)}
    
    async def find_symbol(self, symbol_name: str, symbol_type: str = None, local_only: bool = False) -> List[Dict[str, Any]]:
        """
        Semantische Symbol-Suche (inspiriert von semantic code analysis's find_symbol)
        
        Args:
            symbol_name: Name des zu suchenden Symbols
            symbol_type: Typ des Symbols (function, class, variable, etc.)
            local_only: Nur in aktueller Datei suchen
            
        Returns:
            Liste gefundener Symbole mit Positionen und Kontext
        """
        try:
            symbols = []
            
            # semantic code analysis-ähnliche symbolbasierte Suche
            if self.active_project:
                symbols = await self._execute_semantic_find_symbol(symbol_name, symbol_type, local_only)
            else:
                # Fallback auf traditionelle Textsuche
                symbols = await self._fallback_text_search(symbol_name)
            
            return symbols
            
        except Exception as e:
            logger.error(f"Fehler bei Symbol-Suche: {e}")
            return []
    
    async def get_symbols_overview(self, file_path: str) -> Dict[str, Any]:
        """
        Übersicht über Top-Level Symbole in einer Datei
        
        Args:
            file_path: Pfad zur Datei
            
        Returns:
            Übersicht der Symbole in der Datei
        """
        try:
            file_path = Path(file_path)
            
            if not file_path.exists():
                return {"error": f"Datei nicht gefunden: {file_path}"}
            
            # Semantische Analyse der Datei-Struktur
            overview = await self._analyze_file_symbols(file_path)
            
            return {
                "file_path": str(file_path),
                "symbols": overview,
                "language": self._detect_language(file_path)
            }
            
        except Exception as e:
            logger.error(f"Fehler bei Symbol-Übersicht: {e}")
            return {"error": str(e)}
    
    async def find_referencing_symbols(self, symbol_location: str, symbol_type: str = None) -> List[Dict[str, Any]]:
        """
        Findet alle Referenzen zu einem Symbol (Go to References)
        
        Args:
            symbol_location: Position des Symbols (Datei:Zeile:Spalte)
            symbol_type: Optional - Typ des Symbols
            
        Returns:
            Liste aller Referenzen
        """
        try:
            references = []
            
            # Parse Symbol-Location
            parts = symbol_location.split(':')
            if len(parts) >= 3:
                file_path, line, column = parts[0], int(parts[1]), int(parts[2])
                
                # Semantische Referenz-Suche
                references = await self._find_symbol_references(file_path, line, column)
            
            return references
            
        except Exception as e:
            logger.error(f"Fehler bei Referenz-Suche: {e}")
            return []
    
    async def insert_after_symbol(self, symbol_location: str, content: str) -> Dict[str, Any]:
        """
        Fügt Code nach einem Symbol ein (präzise Symbol-basierte Editierung)
        
        Args:
            symbol_location: Position des Symbols
            content: Einzufügender Code
            
        Returns:
            Ergebnis der Editierung
        """
        try:
            # Parse Symbol-Location
            parts = symbol_location.split(':')
            if len(parts) >= 3:
                file_path, line, column = parts[0], int(parts[1]), int(parts[2])
                
                # Symbolbasierte Insertion
                result = await self._insert_content_after_symbol(file_path, line, column, content)
                return result
            
            return {"error": "Ungültige Symbol-Location"}
            
        except Exception as e:
            logger.error(f"Fehler beim Code-Einfügen: {e}")
            return {"error": str(e)}
    
    async def replace_symbol_body(self, symbol_location: str, new_content: str) -> Dict[str, Any]:
        """
        Ersetzt den Body eines Symbols komplett
        
        Args:
            symbol_location: Position des Symbols
            new_content: Neuer Symbol-Inhalt
            
        Returns:
            Ergebnis der Ersetzung
        """
        try:
            parts = symbol_location.split(':')
            if len(parts) >= 3:
                file_path, line, column = parts[0], int(parts[1]), int(parts[2])
                
                # Symbolbasierte Ersetzung
                result = await self._replace_symbol_content(file_path, line, column, new_content)
                return result
            
            return {"error": "Ungültige Symbol-Location"}
            
        except Exception as e:
            logger.error(f"Fehler beim Symbol-Ersetzen: {e}")
            return {"error": str(e)}
    
    async def execute_shell_command(self, command: str, working_dir: str = None) -> Dict[str, Any]:
        """
        Führt Shell-Kommandos aus (für Testing, Building, etc.)
        
        Args:
            command: Auszuführendes Kommando
            working_dir: Arbeitsverzeichnis
            
        Returns:
            Kommando-Ergebnis
        """
        try:
            cwd = working_dir or str(self.project_path)
            
            process = await asyncio.create_subprocess_shell(
                command,
                cwd=cwd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            return {
                "command": command,
                "working_dir": cwd,
                "return_code": process.returncode,
                "stdout": stdout.decode('utf-8', errors='ignore'),
                "stderr": stderr.decode('utf-8', errors='ignore'),
                "success": process.returncode == 0
            }
            
        except Exception as e:
            logger.error(f"Fehler bei Shell-Kommando: {e}")
            return {"error": str(e), "success": False}
    
    async def search_for_pattern(self, pattern: str, file_types: List[str] = None, case_sensitive: bool = False) -> List[Dict[str, Any]]:
        """
        Sucht nach Pattern im Projekt (erweiterte Grep-Funktionalität)
        
        Args:
            pattern: Suchmuster
            file_types: Zu durchsuchende Dateitypen
            case_sensitive: Groß-/Kleinschreibung beachten
            
        Returns:
            Suchergebnisse mit Kontext
        """
        try:
            results = []
            file_types = file_types or ['*.py', '*.js', '*.ts', '*.java', '*.cpp', '*.c', '*.h']
            
            for file_type in file_types:
                for file_path in self.project_path.rglob(file_type):
                    if file_path.is_file():
                        matches = await self._search_in_file(file_path, pattern, case_sensitive)
                        results.extend(matches)
            
            return results
            
        except Exception as e:
            logger.error(f"Fehler bei Pattern-Suche: {e}")
            return []
    
    async def write_memory(self, memory_name: str, content: str) -> Dict[str, Any]:
        """
        Speichert Projekt-spezifische Memories (semantic code analysis-Feature)
        
        Args:
            memory_name: Name des Memory
            content: Memory-Inhalt
            
        Returns:
            Speicher-Status
        """
        try:
            memories_dir = self.project_path / '.bmad' / 'memories'
            memories_dir.mkdir(parents=True, exist_ok=True)
            
            memory_file = memories_dir / f"{memory_name}.md"
            memory_file.write_text(content, encoding='utf-8')
            
            self.memories[memory_name] = content
            
            return {
                "status": "success",
                "memory_name": memory_name,
                "file_path": str(memory_file)
            }
            
        except Exception as e:
            logger.error(f"Fehler beim Speichern des Memory: {e}")
            return {"error": str(e)}
    
    async def read_memory(self, memory_name: str) -> Dict[str, Any]:
        """
        Liest Projekt-spezifische Memories
        
        Args:
            memory_name: Name des Memory
            
        Returns:
            Memory-Inhalt
        """
        try:
            memories_dir = self.project_path / '.bmad' / 'memories'
            memory_file = memories_dir / f"{memory_name}.md"
            
            if memory_file.exists():
                content = memory_file.read_text(encoding='utf-8')
                return {
                    "memory_name": memory_name,
                    "content": content,
                    "file_path": str(memory_file)
                }
            else:
                return {"error": f"Memory '{memory_name}' nicht gefunden"}
                
        except Exception as e:
            logger.error(f"Fehler beim Lesen des Memory: {e}")
            return {"error": str(e)}
    
    async def list_memories(self) -> List[str]:
        """
        Listet alle verfügbaren Memories auf
        
        Returns:
            Liste der Memory-Namen
        """
        try:
            memories_dir = self.project_path / '.bmad' / 'memories'
            
            if not memories_dir.exists():
                return []
            
            memories = []
            for memory_file in memories_dir.glob('*.md'):
                memories.append(memory_file.stem)
            
            return sorted(memories)
            
        except Exception as e:
            logger.error(f"Fehler beim Auflisten der Memories: {e}")
            return []
    
    # Private Helper Methods
    
    async def _analyze_project_structure(self) -> Dict[str, Any]:
        """Analysiert die Projekt-Struktur"""
        try:
            structure = {
                "languages": set(),
                "frameworks": set(),
                "total_files": 0,
                "code_files": 0,
                "directories": []
            }
            
            for item in self.project_path.rglob('*'):
                if item.is_file():
                    structure["total_files"] += 1
                    
                    # Language Detection
                    lang = self._detect_language(item)
                    if lang:
                        structure["languages"].add(lang)
                        structure["code_files"] += 1
                
                elif item.is_dir():
                    structure["directories"].append(str(item.relative_to(self.project_path)))
            
            # Convert sets to lists for JSON serialization
            structure["languages"] = list(structure["languages"])
            structure["frameworks"] = list(structure["frameworks"])
            
            return structure
            
        except Exception as e:
            logger.error(f"Fehler bei Projekt-Analyse: {e}")
            return {}
    
    async def _setup_semantic_integration(self):
        """Setup für semantic code analysis-Integration"""
        try:
            # Erstelle semantic code analysis-Konfiguration falls nicht vorhanden
            semantic_dir = self.project_path / '.semantic'
            semantic_dir.mkdir(exist_ok=True)
            
            project_yml = semantic_dir / 'project.yml'
            if not project_yml.exists():
                config = {
                    'name': self.active_project,
                    'path': str(self.project_path),
                    'language_servers': {
                        'python': True,
                        'typescript': True,
                        'javascript': True
                    },
                    'tools': {
                        'enabled': ['find_symbol', 'find_referencing_symbols', 'get_symbols_overview']
                    }
                }
                
                import yaml
                with open(project_yml, 'w') as f:
                    yaml.dump(config, f, default_flow_style=False)
            
            logger.info("semantic code analysis-Integration erfolgreich konfiguriert")
            
        except Exception as e:
            logger.error(f"Fehler bei semantic code analysis-Setup: {e}")
    
    def _detect_language(self, file_path: Path) -> Optional[str]:
        """Erkennt die Programmiersprache einer Datei"""
        suffix = file_path.suffix.lower()
        
        language_map = {
            '.py': 'python',
            '.js': 'javascript',
            '.ts': 'typescript',
            '.jsx': 'javascript',
            '.tsx': 'typescript',
            '.java': 'java',
            '.cpp': 'cpp',
            '.c': 'c',
            '.h': 'c',
            '.hpp': 'cpp',
            '.cs': 'csharp',
            '.php': 'php',
            '.rb': 'ruby',
            '.go': 'go',
            '.rs': 'rust',
            '.swift': 'swift',
            '.kt': 'kotlin'
        }
        
        return language_map.get(suffix)
    
    async def _execute_semantic_find_symbol(self, symbol_name: str, symbol_type: str, local_only: bool) -> List[Dict[str, Any]]:
        """Führt semantic code analysis's find_symbol über uvx aus"""
        try:
            # Placeholder for actual semantic code analysis integration
            # In production, this would call the actual semantic code analysis tools
            return []
        except Exception as e:
            logger.error(f"Fehler bei semantic code analysis find_symbol: {e}")
            return []
    
    async def _fallback_text_search(self, symbol_name: str) -> List[Dict[str, Any]]:
        """Fallback Textsuche wenn semantic code analysis nicht verfügbar"""
        try:
            results = []
            
            for file_path in self.project_path.rglob('*.py'):
                if file_path.is_file():
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            lines = f.readlines()
                            
                        for line_num, line in enumerate(lines, 1):
                            if symbol_name in line:
                                results.append({
                                    'file': str(file_path),
                                    'line': line_num,
                                    'content': line.strip(),
                                    'type': 'text_match'
                                })
                    except Exception:
                        continue
            
            return results
            
        except Exception as e:
            logger.error(f"Fehler bei Fallback-Suche: {e}")
            return []
    
    async def _analyze_file_symbols(self, file_path: Path) -> List[Dict[str, Any]]:
        """Analysiert Symbole in einer Datei"""
        try:
            symbols = []
            
            if file_path.suffix == '.py':
                symbols = await self._analyze_python_symbols(file_path)
            elif file_path.suffix in ['.js', '.ts']:
                symbols = await self._analyze_javascript_symbols(file_path)
            
            return symbols
            
        except Exception as e:
            logger.error(f"Fehler bei Datei-Symbol-Analyse: {e}")
            return []
    
    async def _analyze_python_symbols(self, file_path: Path) -> List[Dict[str, Any]]:
        """Analysiert Python-Symbole in einer Datei"""
        try:
            import ast
            
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content)
            symbols = []
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    symbols.append({
                        'name': node.name,
                        'type': 'function',
                        'line': node.lineno,
                        'col': node.col_offset
                    })
                elif isinstance(node, ast.ClassDef):
                    symbols.append({
                        'name': node.name,
                        'type': 'class',
                        'line': node.lineno,
                        'col': node.col_offset
                    })
            
            return symbols
            
        except Exception as e:
            logger.error(f"Fehler bei Python-Symbol-Analyse: {e}")
            return []
    
    async def _analyze_javascript_symbols(self, file_path: Path) -> List[Dict[str, Any]]:
        """Analysiert JavaScript/TypeScript-Symbole"""
        try:
            # Simplified JS/TS symbol detection
            # In production, use proper parser like esprima or typescript compiler
            symbols = []
            
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            for line_num, line in enumerate(lines, 1):
                line = line.strip()
                
                # Function declarations
                if line.startswith('function ') or 'function ' in line:
                    import re
                    match = re.search(r'function\s+(\w+)', line)
                    if match:
                        symbols.append({
                            'name': match.group(1),
                            'type': 'function',
                            'line': line_num,
                            'col': 0
                        })
                
                # Class declarations
                if line.startswith('class ') or 'class ' in line:
                    import re
                    match = re.search(r'class\s+(\w+)', line)
                    if match:
                        symbols.append({
                            'name': match.group(1),
                            'type': 'class',
                            'line': line_num,
                            'col': 0
                        })
            
            return symbols
            
        except Exception as e:
            logger.error(f"Fehler bei JS/TS-Symbol-Analyse: {e}")
            return []
    
    async def _find_symbol_references(self, file_path: str, line: int, column: int) -> List[Dict[str, Any]]:
        """Findet Referenzen zu einem Symbol"""
        try:
            # Placeholder for reference finding
            # In production, use language server or AST analysis
            return []
        except Exception as e:
            logger.error(f"Fehler bei Referenz-Suche: {e}")
            return []
    
    async def _insert_content_after_symbol(self, file_path: str, line: int, column: int, content: str) -> Dict[str, Any]:
        """Fügt Content nach einem Symbol ein"""
        try:
            path = Path(file_path)
            
            with open(path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            # Insert after specified line
            if 0 <= line - 1 < len(lines):
                lines.insert(line, content + '\n')
                
                with open(path, 'w', encoding='utf-8') as f:
                    f.writelines(lines)
                
                return {
                    "status": "success",
                    "file_path": file_path,
                    "line": line,
                    "content_inserted": content
                }
            else:
                return {"error": "Ungültige Zeilennummer"}
                
        except Exception as e:
            logger.error(f"Fehler beim Content-Einfügen: {e}")
            return {"error": str(e)}
    
    async def _replace_symbol_content(self, file_path: str, line: int, column: int, new_content: str) -> Dict[str, Any]:
        """Ersetzt Symbol-Content"""
        try:
            path = Path(file_path)
            
            with open(path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            # Replace line content
            if 0 <= line - 1 < len(lines):
                lines[line - 1] = new_content + '\n'
                
                with open(path, 'w', encoding='utf-8') as f:
                    f.writelines(lines)
                
                return {
                    "status": "success",
                    "file_path": file_path,
                    "line": line,
                    "new_content": new_content
                }
            else:
                return {"error": "Ungültige Zeilennummer"}
                
        except Exception as e:
            logger.error(f"Fehler beim Content-Ersetzen: {e}")
            return {"error": str(e)}
    
    async def _search_in_file(self, file_path: Path, pattern: str, case_sensitive: bool) -> List[Dict[str, Any]]:
        """Sucht Pattern in einer Datei"""
        try:
            matches = []
            
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            import re
            flags = 0 if case_sensitive else re.IGNORECASE
            
            for line_num, line in enumerate(lines, 1):
                if re.search(pattern, line, flags):
                    matches.append({
                        'file': str(file_path),
                        'line': line_num,
                        'content': line.strip(),
                        'pattern': pattern
                    })
            
            return matches
            
        except Exception as e:
            logger.error(f"Fehler bei Datei-Suche: {e}")
            return []