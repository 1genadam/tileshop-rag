#!/usr/bin/env python3
"""
Service Diagnostic Framework - Standardized diagnostics for all system components
"""

import logging
import subprocess
import psutil
import time
from typing import Dict, Any, List, Optional
from abc import ABC, abstractmethod
from datetime import datetime

logger = logging.getLogger(__name__)

class ServiceDiagnostic(ABC):
    """Base class for standardized service diagnostics"""
    
    def __init__(self, service_name: str, service_type: str, description: str):
        self.service_name = service_name
        self.service_type = service_type  # 'microservice', 'runtime', 'prewarm'
        self.description = description
        
    @abstractmethod
    def health_check(self) -> Dict[str, Any]:
        """Perform comprehensive health check with actionable details"""
        pass
    
    @abstractmethod
    def get_filtered_logs(self, lines: int = 50) -> Dict[str, Any]:
        """Get service-specific filtered logs"""
        pass
    
    @abstractmethod
    def debug_panel(self) -> Dict[str, Any]:
        """Advanced troubleshooting information"""
        pass

class ContainerServiceDiagnostic(ServiceDiagnostic):
    """Diagnostic for Docker container-based services"""
    
    def __init__(self, service_name: str, service_type: str, description: str, 
                 container_name: str, ports: List[int] = None):
        super().__init__(service_name, service_type, description)
        self.container_name = container_name
        self.ports = ports or []
        
    def health_check(self) -> Dict[str, Any]:
        """Comprehensive container health check"""
        try:
            # Check container status
            result = subprocess.run([
                'docker', 'inspect', self.container_name, '--format', 
                '{{.State.Status}},{{.State.Health.Status}},{{.Config.Image}}'
            ], capture_output=True, text=True, timeout=10)
            
            if result.returncode != 0:
                return {
                    'success': False,
                    'status': 'container_not_found',
                    'error': f'Container {self.container_name} not found',
                    'suggestion': f'Start the container with: docker start {self.container_name}'
                }
            
            status_parts = result.stdout.strip().split(',')
            container_status = status_parts[0]
            health_status = status_parts[1] if len(status_parts) > 1 else 'none'
            image = status_parts[2] if len(status_parts) > 2 else 'unknown'
            
            # Check port accessibility
            port_status = {}
            for port in self.ports:
                try:
                    import socket
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.settimeout(2)
                    result = sock.connect_ex(('127.0.0.1', port))
                    port_status[port] = result == 0
                    sock.close()
                except Exception:
                    port_status[port] = False
            
            # Get container uptime
            uptime_result = subprocess.run([
                'docker', 'inspect', self.container_name, '--format', 
                '{{.State.StartedAt}}'
            ], capture_output=True, text=True, timeout=5)
            
            uptime = "unknown"
            if uptime_result.returncode == 0:
                try:
                    from dateutil import parser
                    start_time = parser.parse(uptime_result.stdout.strip())
                    uptime_seconds = (datetime.now(start_time.tzinfo) - start_time).total_seconds()
                    uptime = f"{int(uptime_seconds // 60)} minutes"
                except Exception:
                    uptime = "unknown"
            
            overall_status = 'healthy' if container_status == 'running' and all(port_status.values()) else 'issues'
            
            return {
                'success': True,
                'status': overall_status,
                'details': {
                    'container_status': container_status,
                    'health_status': health_status,
                    'image': image,
                    'uptime': uptime,
                    'ports': port_status
                },
                'message': f'Container {container_status}, {len([p for p in port_status.values() if p])}/{len(self.ports)} ports accessible'
            }
            
        except Exception as e:
            return {
                'success': False,
                'status': 'error',
                'error': str(e),
                'suggestion': 'Check Docker daemon status and container configuration'
            }
    
    def get_filtered_logs(self, lines: int = 50) -> Dict[str, Any]:
        """Get container logs with filtering"""
        try:
            result = subprocess.run([
                'docker', 'logs', '--tail', str(lines), '--timestamps', self.container_name
            ], capture_output=True, text=True, timeout=30)
            
            if result.returncode != 0:
                return {
                    'success': False,
                    'error': f'Failed to get logs: {result.stderr}'
                }
            
            # Filter logs for relevance
            logs = result.stdout
            error_count = logs.count('ERROR')
            warning_count = logs.count('WARN')
            
            return {
                'success': True,
                'logs': logs,
                'summary': {
                    'total_lines': len(logs.split('\n')),
                    'errors': error_count,
                    'warnings': warning_count
                }
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Exception getting logs: {str(e)}'
            }
    
    def debug_panel(self) -> Dict[str, Any]:
        """Advanced container troubleshooting"""
        debug_info = {}
        
        try:
            # Container resource usage
            stats_result = subprocess.run([
                'docker', 'stats', '--no-stream', '--format', 
                'table {{.CPUPerc}},{{.MemUsage}},{{.NetIO}},{{.BlockIO}}', 
                self.container_name
            ], capture_output=True, text=True, timeout=10)
            
            if stats_result.returncode == 0:
                lines = stats_result.stdout.strip().split('\n')
                if len(lines) > 1:
                    debug_info['resource_usage'] = lines[1]
            
            # Container configuration
            config_result = subprocess.run([
                'docker', 'inspect', self.container_name, '--format', 
                '{{json .Config.Env}}'
            ], capture_output=True, text=True, timeout=5)
            
            if config_result.returncode == 0:
                debug_info['environment'] = config_result.stdout.strip()
            
            # Recent restart history
            restart_result = subprocess.run([
                'docker', 'inspect', self.container_name, '--format', 
                '{{.RestartCount}}'
            ], capture_output=True, text=True, timeout=5)
            
            if restart_result.returncode == 0:
                debug_info['restart_count'] = restart_result.stdout.strip()
            
            return {
                'success': True,
                'debug_info': debug_info
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Debug panel error: {str(e)}'
            }

class ConceptualServiceDiagnostic(ServiceDiagnostic):
    """Diagnostic for conceptual/system-level services"""
    
    def __init__(self, service_name: str, service_type: str, description: str, 
                 health_check_func: callable):
        super().__init__(service_name, service_type, description)
        self.health_check_func = health_check_func
        
    def health_check(self) -> Dict[str, Any]:
        """System-level health check"""
        try:
            result = self.health_check_func()
            return {
                'success': True,
                'status': 'healthy' if result.get('healthy', False) else 'issues',
                'details': result,
                'message': result.get('message', 'System check completed')
            }
        except Exception as e:
            return {
                'success': False,
                'status': 'error',
                'error': str(e),
                'suggestion': 'Check system dependencies and configuration'
            }
    
    def get_filtered_logs(self, lines: int = 50) -> Dict[str, Any]:
        """System/application logs"""
        return {
            'success': True,
            'logs': f"Service Type: Conceptual Service\nStatus: System-level service\nNote: Logs are integrated into application logging system.",
            'summary': {
                'type': 'conceptual_service',
                'log_location': 'Integrated with application logs'
            }
        }
    
    def debug_panel(self) -> Dict[str, Any]:
        """System-level debugging information"""
        debug_info = {}
        
        try:
            if self.service_name == 'docker_engine':
                # Docker system info
                result = subprocess.run(['docker', 'system', 'df'], capture_output=True, text=True, timeout=10)
                if result.returncode == 0:
                    debug_info['docker_usage'] = result.stdout
                    
            elif self.service_name == 'web_server':
                # Process information
                debug_info['process_info'] = f"PID: {psutil.Process().pid}, Memory: {psutil.Process().memory_info().rss // 1024 // 1024}MB"
                
            return {
                'success': True,
                'debug_info': debug_info
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Debug panel error: {str(e)}'
            }

class RuntimeServiceDiagnostic(ServiceDiagnostic):
    """Diagnostic for runtime environment components"""
    
    def __init__(self, service_name: str, description: str, check_func: callable):
        super().__init__(service_name, 'runtime', description)
        self.check_func = check_func
        
    def health_check(self) -> Dict[str, Any]:
        """Runtime environment health check"""
        try:
            result = self.check_func()
            return {
                'success': True,
                'status': 'healthy' if result.get('success', False) else 'issues',
                'details': result,
                'message': result.get('message', 'Runtime check completed')
            }
        except Exception as e:
            return {
                'success': False,
                'status': 'error',
                'error': str(e),
                'suggestion': 'Check runtime environment configuration'
            }
    
    def get_filtered_logs(self, lines: int = 50) -> Dict[str, Any]:
        """Runtime-specific logs"""
        try:
            if self.service_name == 'python_env':
                # Get Python environment info
                import sys
                logs = f"Python Version: {sys.version}\nExecutable: {sys.executable}\nPath: {sys.path[:3]}"
            elif self.service_name == 'system_resources':
                # System resource logs
                cpu_percent = psutil.cpu_percent(interval=1)
                memory = psutil.virtual_memory()
                logs = f"CPU Usage: {cpu_percent}%\nMemory: {memory.percent}% used ({memory.used // 1024 // 1024 // 1024}GB/{memory.total // 1024 // 1024 // 1024}GB)"
            else:
                logs = f"Runtime service: {self.service_name}\nStatus: Operational"
                
            return {
                'success': True,
                'logs': logs,
                'summary': {
                    'type': 'runtime_info',
                    'timestamp': datetime.now().isoformat()
                }
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'Runtime logs error: {str(e)}'
            }
    
    def debug_panel(self) -> Dict[str, Any]:
        """Runtime debugging information"""
        debug_info = {}
        
        try:
            if self.service_name == 'python_env':
                import sys, os
                debug_info.update({
                    'python_version': sys.version,
                    'executable': sys.executable,
                    'platform': sys.platform,
                    'path_count': len(sys.path),
                    'working_directory': os.getcwd()
                })
            elif self.service_name == 'system_resources':
                debug_info.update({
                    'cpu_count': psutil.cpu_count(),
                    'memory_total': f"{psutil.virtual_memory().total // 1024 // 1024 // 1024}GB",
                    'disk_usage': f"{psutil.disk_usage('/').percent}%",
                    'load_average': psutil.getloadavg() if hasattr(psutil, 'getloadavg') else 'N/A'
                })
                
            return {
                'success': True,
                'debug_info': debug_info
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Runtime debug error: {str(e)}'
            }

class PrewarmServiceDiagnostic(ServiceDiagnostic):
    """Diagnostic for pre-warming system components"""
    
    def __init__(self, service_name: str, description: str, prewarm_func: callable):
        super().__init__(service_name, 'prewarm', description)
        self.prewarm_func = prewarm_func
        
    def health_check(self) -> Dict[str, Any]:
        """Pre-warming system health check"""
        try:
            result = self.prewarm_func()
            return {
                'success': True,
                'status': 'ready' if result.get('success', False) else 'not_ready',
                'details': result,
                'message': result.get('message', 'Pre-warming check completed')
            }
        except Exception as e:
            return {
                'success': False,
                'status': 'error',
                'error': str(e),
                'suggestion': 'Run pre-warming initialization to resolve issues'
            }
    
    def get_filtered_logs(self, lines: int = 50) -> Dict[str, Any]:
        """Pre-warming related logs"""
        return {
            'success': True,
            'logs': f"Pre-warming System: {self.service_name}\nLast Check: {datetime.now().isoformat()}\nNote: Pre-warming logs are integrated into main application logs.",
            'summary': {
                'type': 'prewarm_system',
                'component': self.service_name
            }
        }
    
    def debug_panel(self) -> Dict[str, Any]:
        """Pre-warming debugging information"""
        try:
            result = self.prewarm_func()
            return {
                'success': True,
                'debug_info': {
                    'last_check': datetime.now().isoformat(),
                    'prewarm_result': result,
                    'component': self.service_name
                }
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'Pre-warming debug error: {str(e)}'
            }