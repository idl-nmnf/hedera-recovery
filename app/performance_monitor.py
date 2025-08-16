"""Performance monitoring for the recovery system."""

import psutil
import time
import logging
from typing import Dict, List
from dataclasses import dataclass
from threading import Thread, Event
from config import (
    ENABLE_PERFORMANCE_MONITORING, 
    PERFORMANCE_LOG_INTERVAL,
    CPU_USAGE_THRESHOLD,
    MEMORY_USAGE_THRESHOLD,
    MEMORY_GB,
    CPU_THREADS
)

logger = logging.getLogger(__name__)

@dataclass
class PerformanceMetrics:
    """Performance metrics data structure."""
    timestamp: float
    cpu_percent: float
    memory_percent: float
    memory_gb_used: float
    memory_gb_available: float
    combinations_per_second: float
    gpu_utilization: float = 0.0
    disk_io_read_mb: float = 0.0
    disk_io_write_mb: float = 0.0

class PerformanceMonitor:
    """Real-time performance monitoring for the recovery system."""
    
    def __init__(self):
        self.enabled = ENABLE_PERFORMANCE_MONITORING
        self.interval = PERFORMANCE_LOG_INTERVAL
        self.metrics_history: List[PerformanceMetrics] = []
        self.monitoring = False
        self.stop_event = Event()
        self.monitor_thread = None
        
        # Performance counters
        self.start_time = time.time()
        self.combinations_tested = 0
        self.last_combinations_count = 0
        self.last_check_time = time.time()
        
        # GPU monitoring (if available)
        self.gpu_available = False
        self._init_gpu_monitoring()
    
    def _init_gpu_monitoring(self):
        """Initialize GPU monitoring if available."""
        try:
            import pynvml
            pynvml.nvmlInit()
            self.gpu_available = True
            logger.info("✅ GPU monitoring enabled (NVIDIA)")
        except ImportError:
            try:
                # Alternative: Check for AMD GPU monitoring
                pass
            except:
                logger.info("⚠️ GPU monitoring not available")
    
    def start_monitoring(self):
        """Start performance monitoring in background thread."""
        if not self.enabled:
            return
        
        self.monitoring = True
        self.stop_event.clear()
        self.monitor_thread = Thread(target=self._monitoring_loop, daemon=True)
        self.monitor_thread.start()
        logger.info(f"🔍 Performance monitoring started (interval: {self.interval}s)")
    
    def stop_monitoring(self):
        """Stop performance monitoring."""
        if self.monitoring:
            self.monitoring = False
            self.stop_event.set()
            if self.monitor_thread:
                self.monitor_thread.join(timeout=5)
            logger.info("🔍 Performance monitoring stopped")
    
    def _monitoring_loop(self):
        """Main monitoring loop."""
        while self.monitoring and not self.stop_event.is_set():
            try:
                metrics = self._collect_metrics()
                self.metrics_history.append(metrics)
                
                # Keep only last 100 metrics to prevent memory bloat
                if len(self.metrics_history) > 100:
                    self.metrics_history = self.metrics_history[-100:]
                
                self._log_metrics(metrics)
                self._check_thresholds(metrics)
                
            except Exception as e:
                logger.error(f"Error in performance monitoring: {e}")
            
            self.stop_event.wait(self.interval)
    
    def _collect_metrics(self) -> PerformanceMetrics:
        """Collect current system metrics."""
        current_time = time.time()
        
        # CPU and Memory
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        memory_percent = memory.percent
        memory_gb_used = memory.used / (1024**3)
        memory_gb_available = memory.available / (1024**3)
        
        # Calculate combinations per second
        combinations_delta = self.combinations_tested - self.last_combinations_count
        time_delta = current_time - self.last_check_time
        combinations_per_second = combinations_delta / time_delta if time_delta > 0 else 0
        
        self.last_combinations_count = self.combinations_tested
        self.last_check_time = current_time
        
        # GPU utilization (if available)
        gpu_utilization = self._get_gpu_utilization()
        
        # Disk I/O
        disk_io = psutil.disk_io_counters()
        disk_read_mb = disk_io.read_bytes / (1024**2) if disk_io else 0
        disk_write_mb = disk_io.write_bytes / (1024**2) if disk_io else 0
        
        return PerformanceMetrics(
            timestamp=current_time,
            cpu_percent=cpu_percent,
            memory_percent=memory_percent,
            memory_gb_used=memory_gb_used,
            memory_gb_available=memory_gb_available,
            combinations_per_second=combinations_per_second,
            gpu_utilization=gpu_utilization,
            disk_io_read_mb=disk_read_mb,
            disk_io_write_mb=disk_write_mb
        )
    
    def _get_gpu_utilization(self) -> float:
        """Get GPU utilization percentage."""
        if not self.gpu_available:
            return 0.0
        
        try:
            import pynvml
            handle = pynvml.nvmlDeviceGetHandleByIndex(0)
            utilization = pynvml.nvmlDeviceGetUtilizationRates(handle)
            return utilization.gpu
        except:
            return 0.0
    
    def _log_metrics(self, metrics: PerformanceMetrics):
        """Log performance metrics."""
        runtime = time.time() - self.start_time
        
        logger.info(
            f"📊 Performance - Runtime: {runtime/3600:.1f}h | "
            f"CPU: {metrics.cpu_percent:.1f}% | "
            f"RAM: {metrics.memory_gb_used:.1f}GB ({metrics.memory_percent:.1f}%) | "
            f"Speed: {metrics.combinations_per_second:.1f} combo/s"
        )
        
        if metrics.gpu_utilization > 0:
            logger.info(f"🎮 GPU: {metrics.gpu_utilization:.1f}%")
    
    def _check_thresholds(self, metrics: PerformanceMetrics):
        """Check if metrics exceed warning thresholds."""
        if metrics.cpu_percent > CPU_USAGE_THRESHOLD:
            logger.warning(f"⚠️ High CPU usage: {metrics.cpu_percent:.1f}%")
        
        if metrics.memory_percent > MEMORY_USAGE_THRESHOLD:
            logger.warning(f"⚠️ High memory usage: {metrics.memory_percent:.1f}%")
        
        # Performance degradation warning
        if metrics.combinations_per_second < 10 and self.combinations_tested > 1000:
            logger.warning(f"⚠️ Low processing speed: {metrics.combinations_per_second:.1f} combo/s")
    
    def update_combinations_count(self, count: int):
        """Update the total combinations tested counter."""
        self.combinations_tested = count
    
    def get_current_metrics(self) -> Dict:
        """Get current performance metrics."""
        if not self.metrics_history:
            return {}
        
        latest = self.metrics_history[-1]
        runtime = time.time() - self.start_time
        
        return {
            'runtime_hours': runtime / 3600,
            'cpu_percent': latest.cpu_percent,
            'memory_percent': latest.memory_percent,
            'memory_gb_used': latest.memory_gb_used,
            'combinations_per_second': latest.combinations_per_second,
            'total_combinations': self.combinations_tested,
            'gpu_utilization': latest.gpu_utilization
        }
    
    def get_performance_summary(self) -> str:
        """Get a formatted performance summary."""
        if not self.metrics_history:
            return "No performance data available"
        
        metrics = self.get_current_metrics()
        
        return (
            f"🚀 Performance Summary:\n"
            f"⏱️  Runtime: {metrics['runtime_hours']:.1f} hours\n"
            f"💻 CPU Usage: {metrics['cpu_percent']:.1f}% (Target: <{CPU_USAGE_THRESHOLD}%)\n"
            f"🧠 Memory: {metrics['memory_gb_used']:.1f}GB / {MEMORY_GB}GB ({metrics['memory_percent']:.1f}%)\n"
            f"⚡ Speed: {metrics['combinations_per_second']:.1f} combinations/second\n"
            f"📊 Total Tested: {metrics['total_combinations']:,} combinations\n" +
            (f"🎮 GPU: {metrics['gpu_utilization']:.1f}%\n" if metrics['gpu_utilization'] > 0 else "")
        )

# Global performance monitor instance
performance_monitor = PerformanceMonitor()
