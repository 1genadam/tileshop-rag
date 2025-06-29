#!/usr/bin/env python3
"""
Docker Manager - Container management for Tileshop infrastructure
"""

import docker
import json
import logging
import time
import psutil
from typing import Dict, List, Any, Optional
from docker.errors import DockerException, NotFound, APIError

logger = logging.getLogger(__name__)

class DockerManager:
    """Manages Docker containers for Tileshop scraping infrastructure"""
    
    REQUIRED_CONTAINERS = {
        'postgres': {
            'image_pattern': 'postgres',
            'ports': [5432],
            'health_check': 'database',
            'description': 'Main PostgreSQL database for product data',
            'startup_order': 1
        },
        'supabase': {
            'image_pattern': 'supabase/postgres',
            'ports': [5433],
            'health_check': 'database',
            'description': 'Supabase PostgreSQL with vector extensions',
            'startup_order': 2
        },
        'crawl4ai': {
            'image_pattern': 'unclecode/crawl4ai',
            'ports': [11235],
            'health_check': 'http',
            'description': 'Browser-enabled crawling API service',
            'startup_order': 3
        },
        'supabase-kong': {
            'image_pattern': 'kong',
            'ports': [8000, 8443],
            'health_check': 'http',
            'description': 'Supabase API Gateway',
            'startup_order': 4
        }
    }
    
    def __init__(self):
        try:
            self.client = docker.from_env()
            self.client.ping()  # Test connection
            logger.info("Docker client initialized successfully")
        except DockerException as e:
            logger.error(f"Failed to connect to Docker: {e}")
            raise
    
    def get_all_containers_status(self) -> Dict[str, Any]:
        """Get status of all containers (running and stopped)"""
        try:
            all_containers = self.client.containers.list(all=True)
            container_status = {}
            
            for container in all_containers:
                name = container.name
                status_info = self._get_container_info(container)
                container_status[name] = status_info
            
            return container_status
            
        except DockerException as e:
            logger.error(f"Error getting container status: {e}")
            return {}
    
    def get_required_containers_status(self) -> Dict[str, Any]:
        """Get status of only required containers"""
        all_status = self.get_all_containers_status()
        required_status = {}
        
        for container_name, config in self.REQUIRED_CONTAINERS.items():
            if container_name in all_status:
                required_status[container_name] = all_status[container_name]
                required_status[container_name]['config'] = config
            else:
                # Container not found
                required_status[container_name] = {
                    'status': 'not_found',
                    'state': 'missing',
                    'health': 'unknown',
                    'config': config,
                    'error': f'Container {container_name} not found'
                }
        
        return required_status
    
    def _get_container_info(self, container) -> Dict[str, Any]:
        """Extract detailed information from a container"""
        try:
            container.reload()  # Refresh container state
            
            # Basic info
            info = {
                'name': container.name,
                'status': container.status,
                'state': container.attrs['State']['Status'],
                'image': container.image.tags[0] if container.image.tags else 'unknown',
                'created': container.attrs['Created'],
                'started_at': container.attrs['State'].get('StartedAt', ''),
                'ports': self._get_port_mappings(container),
                'health': self._get_health_status(container),
                'logs_available': True
            }
            
            # Resource usage if running
            if container.status == 'running':
                try:
                    stats = container.stats(stream=False)
                    info['stats'] = self._parse_stats(stats)
                except Exception as e:
                    logger.warning(f"Could not get stats for {container.name}: {e}")
                    info['stats'] = None
            else:
                info['stats'] = None
            
            return info
            
        except Exception as e:
            logger.error(f"Error getting container info for {container.name}: {e}")
            return {
                'name': container.name,
                'status': 'error',
                'error': str(e)
            }
    
    def _get_port_mappings(self, container) -> List[str]:
        """Get port mappings for container"""
        try:
            ports = container.attrs['NetworkSettings']['Ports']
            mappings = []
            for internal, external in ports.items():
                if external:
                    for mapping in external:
                        mappings.append(f"{mapping['HostPort']}:{internal}")
                else:
                    mappings.append(f"unmapped:{internal}")
            return mappings
        except Exception:
            return []
    
    def _get_health_status(self, container) -> str:
        """Get health check status"""
        try:
            health = container.attrs['State'].get('Health', {})
            return health.get('Status', 'unknown')
        except Exception:
            return 'unknown'
    
    def _parse_stats(self, stats: Dict) -> Dict[str, Any]:
        """Parse container stats into readable format"""
        try:
            # Initialize with defaults
            cpu_percent = 0.0
            memory_usage = 0
            memory_limit = 0
            memory_percent = 0
            
            # CPU usage calculation with safe field access
            try:
                cpu_stats = stats.get('cpu_stats', {})
                precpu_stats = stats.get('precpu_stats', {})
                
                cpu_usage = cpu_stats.get('cpu_usage', {})
                precpu_usage = precpu_stats.get('cpu_usage', {})
                
                total_usage = cpu_usage.get('total_usage', 0)
                prev_total_usage = precpu_usage.get('total_usage', 0)
                
                system_cpu_usage = cpu_stats.get('system_cpu_usage', 0)
                prev_system_cpu_usage = precpu_stats.get('system_cpu_usage', 0)
                
                if total_usage and prev_total_usage and system_cpu_usage and prev_system_cpu_usage:
                    cpu_delta = total_usage - prev_total_usage
                    system_delta = system_cpu_usage - prev_system_cpu_usage
                    
                    if system_delta > 0 and cpu_delta > 0:
                        # Check if percpu_usage exists, otherwise use number of CPUs from system
                        percpu_usage = cpu_usage.get('percpu_usage', [])
                        num_cpus = len(percpu_usage) if percpu_usage else psutil.cpu_count()
                        cpu_percent = (cpu_delta / system_delta) * num_cpus * 100.0
                else:
                    # Fallback: use system CPU if container stats unavailable
                    cpu_percent = psutil.cpu_percent(interval=0.1)
                    
            except Exception as cpu_error:
                logger.debug(f"CPU stats calculation failed, using system fallback: {cpu_error}")
                cpu_percent = psutil.cpu_percent(interval=0.1)
            
            # Memory usage calculation with safe field access
            try:
                memory_stats = stats.get('memory_stats', {})
                memory_usage = memory_stats.get('usage', 0)
                memory_limit = memory_stats.get('limit', 0)
                
                if memory_limit > 0:
                    memory_percent = (memory_usage / memory_limit * 100)
                    
            except Exception as mem_error:
                logger.debug(f"Memory stats calculation failed: {mem_error}")
            
            return {
                'cpu_percent': round(min(cpu_percent, 100.0), 2),  # Cap at 100%
                'memory_usage_mb': round(memory_usage / (1024 * 1024), 2),
                'memory_limit_mb': round(memory_limit / (1024 * 1024), 2),
                'memory_percent': round(min(memory_percent, 100.0), 2),  # Cap at 100%
                'timestamp': time.time()
            }
            
        except Exception as e:
            logger.warning(f"Error parsing stats: {e}")
            return {
                'cpu_percent': 0,
                'memory_usage_mb': 0,
                'memory_limit_mb': 0,
                'memory_percent': 0,
                'error': str(e)
            }
    
    def start_container(self, container_name: str) -> Dict[str, Any]:
        """Start a specific container"""
        try:
            container = self.client.containers.get(container_name)
            if container.status == 'running':
                return {'success': True, 'message': f'{container_name} is already running'}
            
            container.start()
            
            # Wait a moment and check status
            time.sleep(2)
            container.reload()
            
            if container.status == 'running':
                return {'success': True, 'message': f'{container_name} started successfully'}
            else:
                return {'success': False, 'error': f'{container_name} failed to start'}
                
        except NotFound:
            return {'success': False, 'error': f'Container {container_name} not found'}
        except APIError as e:
            return {'success': False, 'error': f'Docker API error: {str(e)}'}
        except Exception as e:
            return {'success': False, 'error': f'Unexpected error: {str(e)}'}
    
    def stop_container(self, container_name: str) -> Dict[str, Any]:
        """Stop a specific container"""
        try:
            container = self.client.containers.get(container_name)
            if container.status == 'exited':
                return {'success': True, 'message': f'{container_name} is already stopped'}
            
            container.stop(timeout=10)
            
            # Wait and check status
            time.sleep(2)
            container.reload()
            
            if container.status == 'exited':
                return {'success': True, 'message': f'{container_name} stopped successfully'}
            else:
                return {'success': False, 'error': f'{container_name} failed to stop cleanly'}
                
        except NotFound:
            return {'success': False, 'error': f'Container {container_name} not found'}
        except APIError as e:
            return {'success': False, 'error': f'Docker API error: {str(e)}'}
        except Exception as e:
            return {'success': False, 'error': f'Unexpected error: {str(e)}'}
    
    def restart_container(self, container_name: str) -> Dict[str, Any]:
        """Restart a specific container"""
        try:
            container = self.client.containers.get(container_name)
            container.restart(timeout=10)
            
            # Wait and check status
            time.sleep(3)
            container.reload()
            
            if container.status == 'running':
                return {'success': True, 'message': f'{container_name} restarted successfully'}
            else:
                return {'success': False, 'error': f'{container_name} failed to restart'}
                
        except NotFound:
            return {'success': False, 'error': f'Container {container_name} not found'}
        except APIError as e:
            return {'success': False, 'error': f'Docker API error: {str(e)}'}
        except Exception as e:
            return {'success': False, 'error': f'Unexpected error: {str(e)}'}
    
    def get_container_logs(self, container_name: str, lines: int = 50) -> Dict[str, Any]:
        """Get recent logs from a container"""
        try:
            container = self.client.containers.get(container_name)
            logs = container.logs(tail=lines, timestamps=True).decode('utf-8', errors='ignore')
            
            return {
                'success': True,
                'logs': logs,
                'lines': len(logs.split('\n')) if logs else 0
            }
            
        except NotFound:
            return {'success': False, 'error': f'Container {container_name} not found'}
        except Exception as e:
            return {'success': False, 'error': f'Error getting logs: {str(e)}'}
    
    def start_all_dependencies(self) -> Dict[str, Any]:
        """Start all required containers in proper order"""
        results = []
        
        # Sort by startup order
        ordered_containers = sorted(
            self.REQUIRED_CONTAINERS.items(),
            key=lambda x: x[1]['startup_order']
        )
        
        for container_name, config in ordered_containers:
            result = self.start_container(container_name)
            results.append({
                'container': container_name,
                'result': result
            })
            
            # Wait between starts for dependencies
            if result['success']:
                time.sleep(2)
        
        # Check final status
        successful = sum(1 for r in results if r['result']['success'])
        total = len(results)
        
        return {
            'success': successful == total,
            'message': f'Started {successful}/{total} containers',
            'results': results
        }
    
    def stop_all_dependencies(self) -> Dict[str, Any]:
        """Stop all required containers in reverse order"""
        results = []
        
        # Sort by reverse startup order
        ordered_containers = sorted(
            self.REQUIRED_CONTAINERS.items(),
            key=lambda x: x[1]['startup_order'],
            reverse=True
        )
        
        for container_name, config in ordered_containers:
            result = self.stop_container(container_name)
            results.append({
                'container': container_name,
                'result': result
            })
        
        successful = sum(1 for r in results if r['result']['success'])
        total = len(results)
        
        return {
            'success': successful == total,
            'message': f'Stopped {successful}/{total} containers',
            'results': results
        }
    
    def health_check_container(self, container_name: str) -> Dict[str, Any]:
        """Perform custom health check on container"""
        try:
            container = self.client.containers.get(container_name)
            
            if container.status != 'running':
                return {
                    'healthy': False,
                    'status': container.status,
                    'message': f'Container is {container.status}'
                }
            
            config = self.REQUIRED_CONTAINERS.get(container_name, {})
            check_type = config.get('health_check', 'basic')
            
            if check_type == 'database':
                return self._health_check_database(container, container_name)
            elif check_type == 'http':
                return self._health_check_http(container, container_name)
            else:
                return {
                    'healthy': True,
                    'status': 'running',
                    'message': 'Container is running'
                }
                
        except NotFound:
            return {
                'healthy': False,
                'status': 'not_found',
                'message': f'Container {container_name} not found'
            }
        except Exception as e:
            return {
                'healthy': False,
                'status': 'error',
                'message': f'Health check failed: {str(e)}'
            }
    
    def _health_check_database(self, container, container_name: str) -> Dict[str, Any]:
        """Health check for database containers"""
        try:
            # Use pg_isready command
            exec_result = container.exec_run(['pg_isready', '-U', 'postgres'])
            
            if exec_result.exit_code == 0:
                return {
                    'healthy': True,
                    'status': 'healthy',
                    'message': 'Database is accepting connections'
                }
            else:
                return {
                    'healthy': False,
                    'status': 'unhealthy',
                    'message': f'Database not ready: {exec_result.output.decode()}'
                }
                
        except Exception as e:
            return {
                'healthy': False,
                'status': 'error',
                'message': f'Health check error: {str(e)}'
            }
    
    def _health_check_http(self, container, container_name: str) -> Dict[str, Any]:
        """Health check for HTTP services"""
        # For now, just check if container is running
        # Could be enhanced with actual HTTP requests
        return {
            'healthy': True,
            'status': 'running',
            'message': 'HTTP service is running'
        }
    
    def get_system_resources(self) -> Dict[str, Any]:
        """Get system resource usage"""
        try:
            return {
                'cpu_percent': psutil.cpu_percent(interval=1),
                'memory': {
                    'total': psutil.virtual_memory().total,
                    'available': psutil.virtual_memory().available,
                    'percent': psutil.virtual_memory().percent
                },
                'disk': {
                    'total': psutil.disk_usage('/').total,
                    'free': psutil.disk_usage('/').free,
                    'percent': psutil.disk_usage('/').percent
                },
                'timestamp': time.time()
            }
        except Exception as e:
            logger.error(f"Error getting system resources: {e}")
            return {'error': str(e)}