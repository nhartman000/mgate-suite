import uuid
import time
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from .audit import AuditLog

# 4th Order System: MCP Memory Server
# Implements Model Context Protocol memory as a 4th order system
# Maintains strict containment invariants while accessible from 1st order environment

KADMON_CENTER = -0.500003

@dataclass
class MemoryEntry:
    """4th order memory entry with invariant coordinate anchor"""
    id: str
    key: str
    value: Any
    timestamp: float
    stability: float
    owner_order: int
    trace_id: str
    locks: List[str] = field(default_factory=list)
    access_count: int = 0
    
    def __post_init__(self):
        self.stability = self._calculate_stability()
    
    def _calculate_stability(self) -> float:
        """Calculate Mandelbrot stability for this memory entry"""
        z = 0j
        c = complex(KADMON_CENTER, self.timestamp % 1.0)
        for i in range(20):
            z = z * z + c
            if abs(z) > 2:
                return i / 20.0
        return 1.0

class MCPMemoryServer:
    """
    4th Order System: MCP Memory Server
    
    Containment Rules:
    - Executes within 3rd order LLM context
    - Accessible via bridge from 1st order environment
    - All operations anchored to invariant center point
    - No upward containment violation
    """
    
    def __init__(self, context_id: str, run_trace_id: str):
        self.context_id = context_id
        self.run_trace_id = run_trace_id
        self.memory: Dict[str, MemoryEntry] = {}
        self.audit = AuditLog(context_id, "mcp_memory_server")
        self.created_at = datetime.utcnow()
        self.center_point = KADMON_CENTER
        self.order_level = 4
        
        # Memory space partitioned by order level
        self.partitions = {
            1: set(),  # 1st order owned memory
            2: set(),  # 2nd order owned memory
            3: set(),  # 3rd order owned memory
            4: set()   # 4th order owned memory
        }
        
        self.audit.log_event({
            "type": "memory_server_initialized",
            "context_id": context_id,
            "run_trace_id": run_trace_id,
            "center_point": self.center_point
        })
    
    def write(self, key: str, value: Any, caller_order: int, trace_id: str) -> str:
        """Write memory entry - caller must specify their order level"""
        if caller_order < 1 or caller_order > 4:
            raise ValueError(f"Invalid order level: {caller_order}")
            
        entry_id = str(uuid.uuid4())
        entry = MemoryEntry(
            id=entry_id,
            key=key,
            value=value,
            timestamp=time.time(),
            stability=0.0,
            owner_order=caller_order,
            trace_id=trace_id
        )
        
        self.memory[entry_id] = entry
        self.partitions[caller_order].add(entry_id)
        
        self.audit.log_event({
            "type": "memory_write",
            "key": key,
            "entry_id": entry_id,
            "caller_order": caller_order,
            "trace_id": trace_id
        })
        
        return entry_id
    
    def read(self, key: str, caller_order: int, trace_id: str) -> Optional[Any]:
        """Read memory entry - containment enforced by order level"""
        # Search from highest stability first
        matching = []
        for entry in self.memory.values():
            if entry.key == key:
                # Containment invariant: lower order cannot read higher order memory
                if caller_order <= entry.owner_order:
                    matching.append(entry)
        
        if not matching:
            self.audit.log_event({
                "type": "memory_read_miss",
                "key": key,
                "caller_order": caller_order,
                "trace_id": trace_id
            })
            return None
        
        # Return most stable entry
        matching.sort(key=lambda e: -e.stability)
        entry = matching[0]
        entry.access_count += 1
        
        self.audit.log_event({
            "type": "memory_read_hit",
            "key": key,
            "entry_id": entry.id,
            "stability": entry.stability,
            "caller_order": caller_order,
            "trace_id": trace_id
        })
        
        return entry.value
    
    def scan(self, prefix: str, caller_order: int, trace_id: str) -> List[Dict]:
        """Scan memory entries by key prefix"""
        results = []
        for entry in self.memory.values():
            if entry.key.startswith(prefix) and caller_order <= entry.owner_order:
                results.append({
                    "key": entry.key,
                    "stability": entry.stability,
                    "timestamp": entry.timestamp,
                    "owner_order": entry.owner_order,
                    "access_count": entry.access_count
                })
        
        results.sort(key=lambda e: -e["stability"])
        
        self.audit.log("memory_scan", {
            "prefix": prefix,
            "count": len(results),
            "caller_order": caller_order,
            "trace_id": trace_id
        })
        
        return results
    
    def lock(self, key: str, lock_holder: str, caller_order: int, trace_id: str) -> bool:
        """Acquire exclusive lock on memory entry"""
        for entry in self.memory.values():
            if entry.key == key and caller_order <= entry.owner_order:
                if not entry.locks:
                    entry.locks.append(lock_holder)
                    self.audit.log("memory_lock_acquired", {
                        "key": key,
                        "lock_holder": lock_holder,
                        "caller_order": caller_order,
                        "trace_id": trace_id
                    })
                    return True
                else:
                    self.audit.log("memory_lock_contended", {
                        "key": key,
                        "current_holder": entry.locks[0],
                        "trace_id": trace_id
                    })
                    return False
        return False
    
    def unlock(self, key: str, lock_holder: str, trace_id: str) -> bool:
        """Release lock on memory entry"""
        for entry in self.memory.values():
            if entry.key == key and lock_holder in entry.locks:
                entry.locks.remove(lock_holder)
                self.audit.log("memory_lock_released", {
                    "key": key,
                    "lock_holder": lock_holder,
                    "trace_id": trace_id
                })
                return True
        return False
    
    def garbage_collect(self, stability_threshold: float = 0.2) -> int:
        """Remove memory entries below stability threshold"""
        removed = 0
        to_remove = []
        
        for entry_id, entry in self.memory.items():
            if entry.stability < stability_threshold and not entry.locks:
                to_remove.append(entry_id)
        
        for entry_id in to_remove:
            entry = self.memory.pop(entry_id)
            self.partitions[entry.owner_order].remove(entry_id)
            removed += 1
        
        if removed > 0:
            self.audit.log("memory_gc", {
                "removed": removed,
                "threshold": stability_threshold,
                "remaining": len(self.memory)
            })
        
        return removed
    
    def get_stats(self) -> Dict:
        """Get memory server statistics"""
        stats = {
            "total_entries": len(self.memory),
            "uptime": (datetime.utcnow() - self.created_at).total_seconds(),
            "center_point": self.center_point,
            "order_level": self.order_level,
            "partitions": {k: len(v) for k, v in self.partitions.items()},
            "average_stability": sum(e.stability for e in self.memory.values()) / len(self.memory) if self.memory else 0.0
        }
        
        self.audit.log("memory_stats", stats)
        return stats

class MemoryServerBridge:
    """
    1st order access bridge to 4th order memory server
    
    Maintains containment invariant:
    - 1st order never executes 4th order code directly
    - All operations pass through bridge with order validation
    - Full trace propagation maintained
    - Center point invariant preserved
    """
    
    def __init__(self, environment):
        self.environment = environment
        self.active_servers: Dict[str, MCPMemoryServer] = {}
    
    def create_memory_server(self, context_id: str = None) -> str:
        """Create new 4th order memory server instance"""
        if not self.environment.running:
            raise Exception("Kadmon environment not started")
            
        context_id = context_id or str(uuid.uuid4())
        server = MCPMemoryServer(context_id, self.environment.run_trace_id)
        
        self.active_servers[context_id] = server
        
        # Register as 4th order system in environment
        self.environment.contained_systems["fourth_order"].append({
            "type": "mcp_memory_server",
            "context_id": context_id,
            "registered": datetime.utcnow()
        })
        
        return context_id
    
    def get_server(self, context_id: str) -> Optional[MCPMemoryServer]:
        """Get memory server instance by context id"""
        return self.active_servers.get(context_id)
    
    def memory_write(self, context_id: str, key: str, value: Any) -> str:
        """1st order write operation"""
        server = self.get_server(context_id)
        if not server:
            raise ValueError(f"No memory server found for context: {context_id}")
            
        return server.write(
            key=key,
            value=value,
            caller_order=1,
            trace_id=self.environment.run_trace_id
        )
    
    def memory_read(self, context_id: str, key: str) -> Optional[Any]:
        """1st order read operation"""
        server = self.get_server(context_id)
        if not server:
            raise ValueError(f"No memory server found for context: {context_id}")
            
        return server.read(
            key=key,
            caller_order=1,
            trace_id=self.environment.run_trace_id
        )
    
    def memory_scan(self, context_id: str, prefix: str) -> List[Dict]:
        """1st order scan operation"""
        server = self.get_server(context_id)
        if not server:
            raise ValueError(f"No memory server found for context: {context_id}")
            
        return server.scan(
            prefix=prefix,
            caller_order=1,
            trace_id=self.environment.run_trace_id
        )
