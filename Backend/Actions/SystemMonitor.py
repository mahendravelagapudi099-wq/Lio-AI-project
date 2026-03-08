import psutil
import os
import platform

def get_cpu_usage():
    """Get current CPU usage percentage."""
    try:
        return psutil.cpu_percent(interval=1)
    except Exception as e:
        print(f"[SystemMonitor] CPU usage error: {e}")
        return 0.0

def get_memory_usage():
    """Get current memory usage percentage."""
    try:
        memory = psutil.virtual_memory()
        return memory.percent
    except Exception as e:
        print(f"[SystemMonitor] Memory usage error: {e}")
        return 0.0

def get_disk_usage():
    """Get disk usage for the main drive."""
    try:
        disk = psutil.disk_usage('/') if platform.system() != 'Windows' else psutil.disk_usage('C:\\')
        return disk.percent
    except Exception as e:
        print(f"[SystemMonitor] Disk usage error: {e}")
        return 0.0

def get_network_activity():
    """Get network activity (sent/received bytes)."""
    try:
        net_io = psutil.net_io_counters()
        return {
            'sent': net_io.bytes_sent,
            'received': net_io.bytes_recv
        }
    except Exception as e:
        print(f"[SystemMonitor] Network activity error: {e}")
        return {'sent': 0, 'received': 0}

def get_battery_status():
    """Get battery status information."""
    try:
        if hasattr(psutil, 'sensors_battery'):
            battery = psutil.sensors_battery()
            if battery:
                return {
                    'percent': battery.percent,
                    'charging': battery.power_plugged
                }
        return {'percent': 100, 'charging': True}
    except Exception as e:
        print(f"[SystemMonitor] Battery status error: {e}")
        return {'percent': 100, 'charging': True}

def get_process_list():
    """Get list of running processes."""
    try:
        processes = []
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
            try:
                processes.append({
                    'pid': proc.info['pid'],
                    'name': proc.info['name'],
                    'cpu_usage': proc.info['cpu_percent'],
                    'memory_usage': proc.info['memory_percent']
                })
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        return processes
    except Exception as e:
        print(f"[SystemMonitor] Process list error: {e}")
        return []

def get_system_info():
    """Get comprehensive system information."""
    try:
        cpu_info = {
            'usage': get_cpu_usage(),
            'cores': psutil.cpu_count(logical=True),
            'freq': psutil.cpu_freq().current if hasattr(psutil, 'cpu_freq') else 0
        }
        
        memory_info = {
            'usage': get_memory_usage(),
            'total': psutil.virtual_memory().total / (1024 * 1024 * 1024),
            'available': psutil.virtual_memory().available / (1024 * 1024 * 1024)
        }
        
        disk_info = {
            'usage': get_disk_usage(),
            'total': psutil.disk_usage('/').total / (1024 * 1024 * 1024) if platform.system() != 'Windows' else psutil.disk_usage('C:\\').total / (1024 * 1024 * 1024),
            'used': psutil.disk_usage('/').used / (1024 * 1024 * 1024) if platform.system() != 'Windows' else psutil.disk_usage('C:\\').used / (1024 * 1024 * 1024)
        }
        
        network_info = get_network_activity()
        battery_info = get_battery_status()
        
        return {
            'cpu': cpu_info,
            'memory': memory_info,
            'disk': disk_info,
            'network': network_info,
            'battery': battery_info,
            'platform': platform.system(),
            'version': platform.version()
        }
    except Exception as e:
        print(f"[SystemMonitor] System info error: {e}")
        return {}

def format_system_info(info):
    """Format system information for display."""
    try:
        cpu = info.get('cpu', {})
        memory = info.get('memory', {})
        disk = info.get('disk', {})
        battery = info.get('battery', {})
        
        formatted = []
        formatted.append(f"CPU Usage: {cpu.get('usage', 0):.1f}%")
        formatted.append(f"Memory Usage: {memory.get('usage', 0):.1f}% ({memory.get('used', 0):.1f}/{memory.get('total', 0):.1f} GB)")
        formatted.append(f"Disk Usage: {disk.get('usage', 0):.1f}% ({disk.get('used', 0):.1f}/{disk.get('total', 0):.1f} GB)")
        formatted.append(f"Battery: {battery.get('percent', 100)}% {'(Charging)' if battery.get('charging', True) else ''}")
        formatted.append(f"Platform: {info.get('platform', 'Unknown')} {info.get('version', 'Unknown')}")
        
        return '\n'.join(formatted)
    except Exception as e:
        print(f"[SystemMonitor] Formatting error: {e}")
        return "Error formatting system information"

if __name__ == "__main__":
    # Test the system monitor
    print("Testing System Monitor...")
    print("\n1. CPU Usage:")
    print(f"   {get_cpu_usage():.1f}%")
    
    print("\n2. Memory Usage:")
    print(f"   {get_memory_usage():.1f}%")
    
    print("\n3. Disk Usage:")
    print(f"   {get_disk_usage():.1f}%")
    
    print("\n4. Network Activity:")
    net = get_network_activity()
    print(f"   Sent: {net['sent']:,} bytes")
    print(f"   Received: {net['received']:,} bytes")
    
    print("\n5. Battery Status:")
    battery = get_battery_status()
    print(f"   {battery['percent']}% {'(Charging)' if battery['charging'] else ''}")
    
    print("\n6. Comprehensive System Info:")
    info = get_system_info()
    print(format_system_info(info))
