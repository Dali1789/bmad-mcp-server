"""
BMAD-Serena Bridge Agent
Integriert Serena MCP Server direkt als BMAD Agent für maximale Code-Analyse Power
"""

import asyncio
import json
import logging
import subprocess
import tempfile
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
import os
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

logger = logging.getLogger(__name__)

class BMadSerenaAgent:
    """
    BMAD Agent der Serena MCP Server direkt einbindet
    
    Vorteile:
    - 100% Serena Funktionalität 
    - Echte Language Server Integration
    - Semantische Code-Analyse auf Professional-Level
    - Alle Serena Tools verfügbar
    - BMAD-native Integration
    """
    
    def __init__(self):
        self.serena_process = None
        self.mcp_session = None
        self.mcp_context = None
        self.read_stream = None
        self.write_stream = None
        self.active_project = None
        self.serena_command = self._get_serena_command()
        self.is_initialized = False
        self.available_tools = []
        
    def _get_serena_command(self) -> List[str]:
        """Bestimmt den Serena-Kommando basierend auf Installation"""
        uvx_path = r"C:\Users\Faber\.local\bin\uvx.exe"
        
        if os.path.exists(uvx_path):
            return [
                uvx_path,
                "--from", "git+https://github.com/oraios/serena",
                "serena", "start-mcp-server",
                "--context", "agent",
                "--transport", "stdio"
            ]
        else:
            # Fallback falls uvx nicht gefunden wird
            return [
                "uvx",
                "--from", "git+https://github.com/oraios/serena", 
                "serena", "start-mcp-server",
                "--context", "agent",
                "--transport", "stdio"
            ]
    
    async def initialize(self) -> Dict[str, Any]:
        """Initialisiert die Serena Bridge mit echter MCP-Verbindung"""
        try:
            if self.is_initialized:
                return {"status": "already_initialized", "serena_available": True}
            
            # Test Serena availability first
            test_result = await self._test_serena_availability()
            if not test_result["available"]:
                return {
                    "status": "error",
                    "serena_available": False,
                    "error": test_result.get("error"),
                    "message": "Serena nicht verfügbar - Fallback auf Basic-Tools"
                }
            
            # Start MCP Server and connect
            logger.info("Starte Serena MCP Integration...")
            mcp_started = await self._start_serena_mcp_server()
            
            if mcp_started:
                self.is_initialized = True
                logger.info("Serena Bridge mit echter MCP-Integration erfolgreich initialisiert")
                
                return {
                    "status": "success",
                    "serena_available": True,
                    "mcp_session_active": True,
                    "serena_version": test_result.get("version"),
                    "available_tools": self.available_tools,
                    "available_tools_count": len(self.available_tools),
                    "message": "Serena Bridge mit echter MCP-Integration aktiv - Volle semantische Code-Analyse verfügbar!"
                }
            else:
                return {
                    "status": "error",
                    "serena_available": False,
                    "mcp_session_active": False,
                    "error": "MCP Server konnte nicht gestartet werden",
                    "message": "Serena MCP-Integration fehlgeschlagen - Fallback auf Basic-Tools"
                }
                
        except Exception as e:
            logger.error(f"Fehler bei Serena-Initialisierung: {e}")
            return {
                "status": "error", 
                "serena_available": False,
                "mcp_session_active": False,
                "error": str(e)
            }
    
    async def activate_project(self, project_path: str, project_name: str = None) -> Dict[str, Any]:
        """
        Aktiviert ein Projekt in Serena
        
        Args:
            project_path: Absoluter Pfad zum Projekt
            project_name: Optionaler Projektname
            
        Returns:
            Projekt-Aktivierungsresult
        """
        try:
            if not self.is_initialized:
                init_result = await self.initialize()
                if not init_result.get("serena_available"):
                    return init_result
            
            # Serena-Projekt-Aktivierung
            result = await self._call_serena_tool("activate_project", {
                "project_path": project_path,
                "project_name": project_name or Path(project_path).name
            })
            
            if result.get("success"):
                self.active_project = {
                    "path": project_path,
                    "name": project_name or Path(project_path).name
                }
                
                # Trigger project indexing for better performance
                await self._index_project(project_path)
                
            return result
            
        except Exception as e:
            logger.error(f"Fehler bei Projekt-Aktivierung: {e}")
            return {"error": str(e), "success": False}
    
    async def find_symbol(self, symbol_name: str, symbol_type: str = None, local_only: bool = False) -> Dict[str, Any]:
        """
        Serena's mächtige Symbol-Suche
        
        Args:
            symbol_name: Name des zu suchenden Symbols
            symbol_type: Typ des Symbols (function, class, variable, etc.)
            local_only: Nur in aktueller Datei suchen
            
        Returns:
            Serena's Symbol-Suchergebnisse
        """
        return await self._call_serena_tool("find_symbol", {
            "name": symbol_name,
            "type": symbol_type,
            "local_only": local_only
        })
    
    async def get_symbols_overview(self, file_path: str) -> Dict[str, Any]:
        """
        Serena's Symbol-Übersicht für eine Datei
        
        Args:
            file_path: Pfad zur Datei
            
        Returns:
            Detaillierte Symbol-Übersicht
        """
        return await self._call_serena_tool("get_symbols_overview", {
            "file_path": file_path
        })
    
    async def find_referencing_symbols(self, symbol_location: str, symbol_type: str = None) -> Dict[str, Any]:
        """
        Serena's "Go to References" - findet alle Symbol-Referenzen
        
        Args:
            symbol_location: Position des Symbols (Datei:Zeile:Spalte)
            symbol_type: Optional - Typ des Symbols
            
        Returns:
            Liste aller Referenzen mit Kontext
        """
        return await self._call_serena_tool("find_referencing_symbols", {
            "symbol_location": symbol_location,
            "symbol_type": symbol_type
        })
    
    async def insert_after_symbol(self, symbol_location: str, content: str) -> Dict[str, Any]:
        """
        Serena's präzise Symbol-basierte Code-Insertion
        
        Args:
            symbol_location: Position des Symbols
            content: Einzufügender Code
            
        Returns:
            Ergebnis der präzisen Insertion
        """
        return await self._call_serena_tool("insert_after_symbol", {
            "symbol_location": symbol_location,
            "content": content
        })
    
    async def replace_symbol_body(self, symbol_location: str, new_content: str) -> Dict[str, Any]:
        """
        Serena's intelligente Symbol-Body-Ersetzung
        
        Args:
            symbol_location: Position des Symbols
            new_content: Neuer Symbol-Inhalt
            
        Returns:
            Ergebnis der Ersetzung
        """
        return await self._call_serena_tool("replace_symbol_body", {
            "symbol_location": symbol_location,
            "new_content": new_content
        })
    
    async def execute_shell_command(self, command: str, working_dir: str = None) -> Dict[str, Any]:
        """
        Serena's Shell-Kommando-Ausführung
        
        Args:
            command: Auszuführendes Kommando
            working_dir: Arbeitsverzeichnis
            
        Returns:
            Kommando-Ergebnis
        """
        return await self._call_serena_tool("execute_shell_command", {
            "command": command,
            "working_dir": working_dir or (self.active_project["path"] if self.active_project else None)
        })
    
    async def search_for_pattern(self, pattern: str, file_types: List[str] = None, case_sensitive: bool = False) -> Dict[str, Any]:
        """
        Serena's erweiterte Pattern-Suche
        
        Args:
            pattern: Suchmuster
            file_types: Zu durchsuchende Dateitypen
            case_sensitive: Groß-/Kleinschreibung beachten
            
        Returns:
            Erweiterte Suchergebnisse mit Kontext
        """
        return await self._call_serena_tool("search_for_pattern", {
            "pattern": pattern,
            "file_types": file_types,
            "case_sensitive": case_sensitive
        })
    
    async def write_memory(self, memory_name: str, content: str) -> Dict[str, Any]:
        """
        Serena's Memory-System
        
        Args:
            memory_name: Name des Memory
            content: Memory-Inhalt
            
        Returns:
            Speicher-Status
        """
        return await self._call_serena_tool("write_memory", {
            "memory_name": memory_name,
            "content": content
        })
    
    async def read_memory(self, memory_name: str) -> Dict[str, Any]:
        """
        Serena's Memory-System lesen
        
        Args:
            memory_name: Name des Memory
            
        Returns:
            Memory-Inhalt
        """
        return await self._call_serena_tool("read_memory", {
            "memory_name": memory_name
        })
    
    async def list_memories(self) -> Dict[str, Any]:
        """
        Serena's verfügbare Memories auflisten
        
        Returns:
            Liste der Memory-Namen
        """
        return await self._call_serena_tool("list_memories", {})
    
    async def onboarding(self, project_path: str = None) -> Dict[str, Any]:
        """
        Serena's intelligentes Projekt-Onboarding
        
        Args:
            project_path: Projekt-Pfad (optional, nutzt aktives Projekt)
            
        Returns:
            Onboarding-Ergebnisse und Memories
        """
        return await self._call_serena_tool("onboarding", {
            "project_path": project_path or (self.active_project["path"] if self.active_project else None)
        })
    
    async def get_project_summary(self) -> Dict[str, Any]:
        """
        Umfassende Projekt-Zusammenfassung mit Serena
        
        Returns:
            Detaillierte Projekt-Analyse
        """
        if not self.active_project:
            return {"error": "Kein aktives Projekt. Nutze activate_project zuerst."}
        
        try:
            # Multiple Serena-Tools für umfassende Analyse
            results = {}
            
            # Projekt-Struktur analysieren
            results["onboarding"] = await self.onboarding()
            
            # Memories abrufen
            results["memories"] = await self.list_memories()
            
            # Symbol-Übersicht für Haupt-Dateien
            project_path = Path(self.active_project["path"])
            main_files = []
            
            for pattern in ["*.py", "*.js", "*.ts", "*.java", "*.cpp"]:
                for file_path in project_path.rglob(pattern):
                    if file_path.is_file() and len(main_files) < 5:  # Limit für Performance
                        main_files.append(str(file_path))
            
            results["main_files_symbols"] = {}
            for file_path in main_files[:3]:  # Top 3 files
                results["main_files_symbols"][file_path] = await self.get_symbols_overview(file_path)
            
            return {
                "success": True,
                "project": self.active_project,
                "analysis": results,
                "message": "Vollständige Serena-Projekt-Analyse abgeschlossen"
            }
            
        except Exception as e:
            logger.error(f"Fehler bei Projekt-Zusammenfassung: {e}")
            return {"error": str(e), "success": False}
    
    # Private Helper Methods
    
    async def _test_serena_availability(self) -> Dict[str, Any]:
        """Testet ob Serena verfügbar ist"""
        try:
            # Test Serena Command - use base serena command for help
            cmd = ["C:\\Users\\Faber\\.local\\bin\\uvx.exe", "--from", "git+https://github.com/oraios/serena", "serena", "--help"]
            
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            try:
                stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=10.0)
            except asyncio.TimeoutError:
                process.kill()
                return {
                    "available": False,
                    "error": "Serena command timeout"
                }
            
            if process.returncode == 0:
                return {
                    "available": True,
                    "version": "latest",
                    "output": stdout.decode('utf-8', errors='ignore')[:500]
                }
            else:
                return {
                    "available": False,
                    "error": f"Serena command failed: {stderr.decode('utf-8', errors='ignore')}"
                }
                
        except Exception as e:
            return {
                "available": False,
                "error": f"Serena test failed: {str(e)}"
            }
    
    async def _get_available_serena_tools(self) -> List[str]:
        """Ruft verfügbare Serena Tools ab - wird jetzt über echte MCP-Verbindung erledigt"""
        try:
            if self.mcp_session:
                # Get tools from real MCP session
                tools_result = await self.mcp_session.list_tools()
                return [tool.name for tool in tools_result.tools]
            else:
                # Standard Serena Tools die wir erwarten (Fallback)
                return [
                    "activate_project",
                    "find_symbol", 
                    "get_symbols_overview",
                    "find_referencing_symbols",
                    "insert_after_symbol",
                    "replace_symbol_body", 
                    "execute_shell_command",
                    "search_for_pattern",
                    "write_memory",
                    "read_memory",
                    "list_memories",
                    "onboarding",
                    "create_text_file",
                    "read_file",
                    "list_dir"
                ]
        except Exception as e:
            logger.error(f"Fehler beim Abrufen der Serena Tools: {e}")
            return []
    
    async def _start_serena_mcp_server(self) -> bool:
        """
        Startet den Serena MCP Server und verbindet sich
        """
        try:
            if self.mcp_session:
                logger.info("Serena MCP Session bereits aktiv")
                return True
            
            logger.info("Starte Serena MCP Server...")
            
            # Start Serena MCP Server process
            server_params = StdioServerParameters(
                command=self.serena_command[0],
                args=self.serena_command[1:]
            )
            
            # Create async context manager but store it for persistent use
            self.mcp_context = stdio_client(server_params)
            
            # Enter the context and store read/write streams
            self.read_stream, self.write_stream = await self.mcp_context.__aenter__()
            
            # Create persistent MCP session
            self.mcp_session = ClientSession(self.read_stream, self.write_stream)
            
            # Initialize session
            result = await self.mcp_session.initialize()
            logger.info(f"Serena MCP Server initialisiert: {result.server_info.name} v{result.server_info.version}")
            
            # Get available tools
            tools_result = await self.mcp_session.list_tools()
            self.available_tools = [tool.name for tool in tools_result.tools]
            logger.info(f"Verfügbare Serena Tools: {len(self.available_tools)}")
            
            return True
            
        except Exception as e:
            logger.error(f"Fehler beim Starten des Serena MCP Servers: {e}")
            self.mcp_session = None
            self.mcp_context = None
            return False
    
    async def _call_serena_tool(self, tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Ruft ein Serena Tool über echte MCP-Kommunikation auf
        """
        try:
            # Ensure MCP session is active
            if not self.mcp_session:
                server_started = await self._start_serena_mcp_server()
                if not server_started:
                    return {
                        "success": False,
                        "error": "Serena MCP Server konnte nicht gestartet werden",
                        "tool": tool_name
                    }
            
            logger.info(f"Rufe Serena Tool auf: {tool_name} mit {parameters}")
            
            # Check if tool is available
            if tool_name not in self.available_tools:
                logger.warning(f"Tool {tool_name} nicht in verfügbaren Tools: {self.available_tools}")
                # Try to refresh tools list
                tools_result = await self.mcp_session.list_tools()
                self.available_tools = [tool.name for tool in tools_result.tools]
                
                if tool_name not in self.available_tools:
                    return {
                        "success": False,
                        "error": f"Tool '{tool_name}' nicht verfügbar in Serena",
                        "available_tools": self.available_tools,
                        "tool": tool_name
                    }
            
            # Call the tool via MCP
            result = await self.mcp_session.call_tool(tool_name, parameters)
            
            # Parse result
            if hasattr(result, 'content') and result.content:
                # Extract text content from MCP result
                content_text = ""
                for content_item in result.content:
                    if hasattr(content_item, 'text'):
                        content_text += content_item.text
                    elif hasattr(content_item, 'data'):
                        content_text += str(content_item.data)
                
                return {
                    "success": True,
                    "tool": tool_name,
                    "parameters": parameters,
                    "result": content_text,
                    "mcp_response": str(result),
                    "note": "Echte Serena MCP-Integration aktiv"
                }
            else:
                return {
                    "success": True,
                    "tool": tool_name,
                    "parameters": parameters,
                    "result": str(result),
                    "note": "Echte Serena MCP-Integration aktiv"
                }
            
        except Exception as e:
            logger.error(f"Fehler bei Serena Tool-Call {tool_name}: {e}")
            
            # Try to restart session on error
            if "Connection" in str(e) or "pipe" in str(e).lower():
                logger.info("Versuche Serena MCP Session neu zu starten...")
                self.mcp_session = None
                
            return {
                "success": False,
                "error": str(e),
                "tool": tool_name,
                "note": "MCP-Kommunikationsfehler"
            }
    
    async def _index_project(self, project_path: str):
        """Triggert Serena's Projekt-Indexierung für bessere Performance"""
        try:
            # Serena's Indexing-Kommando (falls verfügbar)
            index_cmd = self.serena_command[:-3] + ["project", "index", project_path]
            
            process = await asyncio.create_subprocess_exec(
                *index_cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            await process.communicate()
            logger.info(f"Serena Projekt-Indexierung für {project_path} gestartet")
            
        except Exception as e:
            logger.warning(f"Serena Indexierung fehlgeschlagen (nicht kritisch): {e}")
    
    async def cleanup(self):
        """Cleanup-Ressourcen"""
        try:
            # Close MCP session
            if self.mcp_session:
                try:
                    await self.mcp_session.close()
                    logger.info("Serena MCP Session geschlossen")
                except Exception as e:
                    logger.warning(f"Fehler beim Schließen der MCP Session: {e}")
                finally:
                    self.mcp_session = None
            
            # Exit MCP context if exists
            if self.mcp_context:
                try:
                    await self.mcp_context.__aexit__(None, None, None)
                    logger.info("Serena MCP Context geschlossen")
                except Exception as e:
                    logger.warning(f"Fehler beim Schließen des MCP Context: {e}")
                finally:
                    self.mcp_context = None
                    self.read_stream = None
                    self.write_stream = None
            
            # Cleanup process
            if self.serena_process and self.serena_process.returncode is None:
                self.serena_process.terminate()
                await self.serena_process.wait()
                logger.info("Serena Prozess beendet")
                
            logger.info("Serena Bridge Cleanup abgeschlossen")
            
        except Exception as e:
            logger.error(f"Fehler bei Serena Cleanup: {e}")
    
    def get_status(self) -> Dict[str, Any]:
        """Status der Serena Bridge"""
        return {
            "initialized": self.is_initialized,
            "mcp_session_active": self.mcp_session is not None,
            "available_tools_count": len(self.available_tools),
            "available_tools": self.available_tools[:10],  # First 10 tools
            "active_project": self.active_project,
            "serena_command": " ".join(self.serena_command),
            "bridge_version": "1.1.0 - Real MCP Integration"
        }