"""
Kadmon Plugin Registry — Modular Plugin System
Analogous to Unreal Engine's module system: any system can be plugged into
the Kadmon 1st order runtime environment. Plugins are typed by order level.

Order levels:
    2nd order: PAIR, COUPLE configurations (LLM dual configs)
    3rd order: LLM backends (GPT, Grok, Gemini, Claude, custom)
    4th order: MGATE pipelines, MCPMemoryServer, custom deterministic processors
    5th order: NYCH, custom gestalt encoders, phonetic compressors
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Callable
from enum import Enum
import uuid
from datetime import datetime


# ---------------------------------------------------------------------------
# Enumerations
# ---------------------------------------------------------------------------

class PluginOrder(Enum):
    SECOND = 2
    THIRD  = 3
    FOURTH = 4
    FIFTH  = 5


class PluginStatus(Enum):
    INSTALLED = "installed"
    ENABLED   = "enabled"
    DISABLED  = "disabled"
    ERROR     = "error"


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------

@dataclass
class PluginManifest:
    """
    Declarative description of a Kadmon plugin.
    Every plugin must provide this manifest.
    """
    plugin_id: str                              # unique snake_case identifier e.g. "mcp_memory", "nych_encoder"
    name: str                                   # human readable
    order: PluginOrder                          # which order level it operates at
    version: str                                # semver string "1.0.0"
    description: str
    author: str = "kadmon"
    requires: List[str] = field(default_factory=list)   # plugin_ids this depends on
    config_schema: Dict = field(default_factory=dict)   # JSON schema for config
    singleton: bool = False                     # if True, only one instance allowed


@dataclass
class PluginInstance:
    instance_id: str
    manifest: PluginManifest
    status: PluginStatus
    config: Dict
    installed_at: datetime
    enabled_at: Optional[datetime] = None
    error: Optional[str] = None
    runtime_ref: Any = None                     # the actual running object if enabled


# ---------------------------------------------------------------------------
# Built-in plugin manifests
# ---------------------------------------------------------------------------

BUILTIN_PLUGINS: List[PluginManifest] = [
    PluginManifest(
        "mcp_memory",
        "MCP Memory Server",
        PluginOrder.FOURTH,
        "1.0.0",
        "Mandelbrot-anchored 4th order memory with order-level containment",
        singleton=False,
    ),
    PluginManifest(
        "nych_encoder",
        "NYCH Gestalt Encoder",
        PluginOrder.FIFTH,
        "1.0.0",
        "Zero-API natural language → gestalt emoji encoder",
        singleton=True,
    ),
    PluginManifest(
        "mgate_runner",
        "MGATE Pipeline Runner",
        PluginOrder.FOURTH,
        "1.0.0",
        "Deterministic boolean gate DAG executor",
        singleton=False,
    ),
    PluginManifest(
        "mobius_tmt",
        "Möbius Transport (TMT)",
        PluginOrder.FOURTH,
        "1.0.0",
        "Triadic Möbius holonomy measurement loop",
        singleton=False,
    ),
    PluginManifest(
        "llm_gpt",
        "OpenAI GPT Backend",
        PluginOrder.THIRD,
        "1.0.0",
        "3rd order LLM: OpenAI GPT-4/GPT-4o",
        singleton=False,
        config_schema={"api_key": "string", "model": "string"},
    ),
    PluginManifest(
        "llm_claude",
        "Anthropic Claude Backend",
        PluginOrder.THIRD,
        "1.0.0",
        "3rd order LLM: Anthropic Claude",
        singleton=False,
        config_schema={"api_key": "string", "model": "string"},
    ),
    PluginManifest(
        "llm_gemini",
        "Google Gemini Backend",
        PluginOrder.THIRD,
        "1.0.0",
        "3rd order LLM: Google Gemini via Vertex AI",
        singleton=False,
        config_schema={"project_id": "string", "location": "string"},
    ),
    PluginManifest(
        "llm_grok",
        "xAI Grok Backend",
        PluginOrder.THIRD,
        "1.0.0",
        "3rd order LLM: xAI Grok",
        singleton=False,
        config_schema={"api_key": "string"},
    ),
    PluginManifest(
        "pair_config",
        "PAIR Dual Configuration",
        PluginOrder.SECOND,
        "1.0.0",
        "Standard 2nd order PAIR: two LLMs share invariant center",
        singleton=False,
    ),
    PluginManifest(
        "couple_config",
        "COUPLE Dual Configuration",
        PluginOrder.SECOND,
        "1.0.0",
        "Advanced 2nd order COUPLE: projective cross-validation binding",
        singleton=False,
    ),
    PluginManifest(
        "training_router",
        "Training Router",
        PluginOrder.FOURTH,
        "1.0.0",
        "ML router trained on QSON trajectories to predict optimal Mandelbrot coordinates",
        singleton=True,
    ),
]


# ---------------------------------------------------------------------------
# Registry
# ---------------------------------------------------------------------------

class KadmonPluginRegistry:
    """
    Central module registry for the Kadmon 1st order runtime.
    Manages install, enable, disable, uninstall of all pluggable systems.
    Maintains strict order-level containment invariants.
    """

    def __init__(self, environment) -> None:
        self.environment = environment
        self.manifests: Dict[str, PluginManifest] = {}
        self.instances: Dict[str, PluginInstance] = {}
        self._event_subscribers: Dict[str, List[Callable]] = {}
        self._register_builtins()

    # ------------------------------------------------------------------
    # Internal setup
    # ------------------------------------------------------------------

    def _register_builtins(self) -> None:
        """Register manifests for all built-in Kadmon plugins."""
        for m in BUILTIN_PLUGINS:
            self.manifests[m.plugin_id] = m

    # ------------------------------------------------------------------
    # Manifest management
    # ------------------------------------------------------------------

    def register_manifest(self, manifest: PluginManifest) -> None:
        """Add a custom plugin manifest to the registry."""
        self.manifests[manifest.plugin_id] = manifest
        self.emit("plugin_manifest_registered", {"plugin_id": manifest.plugin_id})

    def list_available(self) -> List[PluginManifest]:
        """Return all registered manifests (available to install)."""
        return list(self.manifests.values())

    # ------------------------------------------------------------------
    # Lifecycle: install → enable → disable → uninstall
    # ------------------------------------------------------------------

    def install(self, plugin_id: str, config: Dict = None) -> PluginInstance:
        """
        Install a plugin by its manifest plugin_id.

        Validates:
        - plugin_id is registered
        - singleton constraint is not violated
        - all required dependencies are already installed
        """
        if plugin_id not in self.manifests:
            raise ValueError(f"Unknown plugin_id '{plugin_id}'. Register its manifest first.")

        manifest = self.manifests[plugin_id]
        config = config or {}

        # Singleton guard: only one enabled instance is allowed
        if manifest.singleton:
            for inst in self.instances.values():
                if inst.manifest.plugin_id == plugin_id and inst.status == PluginStatus.ENABLED:
                    raise RuntimeError(
                        f"Plugin '{plugin_id}' is marked singleton and already has an enabled instance "
                        f"(instance_id={inst.instance_id})."
                    )

        # Dependency check: all required plugin_ids must be installed
        installed_plugin_ids = {i.manifest.plugin_id for i in self.instances.values()}
        for dep_id in manifest.requires:
            if dep_id not in installed_plugin_ids:
                raise RuntimeError(
                    f"Plugin '{plugin_id}' requires '{dep_id}', which is not yet installed."
                )

        instance = PluginInstance(
            instance_id=str(uuid.uuid4()),
            manifest=manifest,
            status=PluginStatus.INSTALLED,
            config=config,
            installed_at=datetime.utcnow(),
        )

        self.instances[instance.instance_id] = instance
        self.emit("plugin_installed", {"instance_id": instance.instance_id, "plugin_id": plugin_id})
        return instance

    def enable(self, instance_id: str) -> PluginInstance:
        """
        Enable an installed or disabled plugin instance.
        Wires up the runtime object via _activate().
        """
        instance = self._get_instance_or_raise(instance_id)

        if instance.status not in (PluginStatus.INSTALLED, PluginStatus.DISABLED):
            raise RuntimeError(
                f"Instance '{instance_id}' cannot be enabled from status '{instance.status.value}'. "
                "Expected INSTALLED or DISABLED."
            )

        try:
            self._activate(instance)
            instance.status = PluginStatus.ENABLED
            instance.enabled_at = datetime.utcnow()
            instance.error = None
        except Exception as exc:
            instance.status = PluginStatus.ERROR
            instance.error = str(exc)
            self.emit("plugin_error", {"instance_id": instance_id, "error": str(exc)})
            raise

        self.emit("plugin_enabled", {"instance_id": instance_id, "plugin_id": instance.manifest.plugin_id})
        return instance

    def _activate(self, instance: PluginInstance) -> None:
        """
        Wire the runtime object for the given plugin instance based on plugin_id.
        """
        pid = instance.manifest.plugin_id

        if pid == "mcp_memory":
            instance.runtime_ref = self.environment.create_memory_server()

        elif pid == "nych_encoder":
            self.environment.enable_nych()
            instance.runtime_ref = self.environment.nych_bridge

        elif pid == "mgate_runner":
            instance.runtime_ref = {"type": "mgate_runner", "config": instance.config}

        elif pid == "mobius_tmt":
            from .mobius import TriadicMobiusTransport  # local import to avoid circular deps
            instance.runtime_ref = {"type": "mobius_tmt", "class": TriadicMobiusTransport}

        elif pid.startswith("llm_"):
            instance.runtime_ref = {"type": pid, "config": instance.config}

        elif pid in ("pair_config", "couple_config"):
            mode = pid.split("_")[0].upper()
            instance.runtime_ref = {"mode": mode, "config": instance.config}

        else:
            # Generic fallback: expose config dict as runtime ref
            instance.runtime_ref = instance.config

    def disable(self, instance_id: str) -> PluginInstance:
        """
        Disable an enabled plugin instance, clearing its runtime reference.
        """
        instance = self._get_instance_or_raise(instance_id)
        instance.status = PluginStatus.DISABLED
        instance.runtime_ref = None
        self.emit("plugin_disabled", {"instance_id": instance_id, "plugin_id": instance.manifest.plugin_id})
        return instance

    def uninstall(self, instance_id: str) -> None:
        """
        Uninstall a plugin instance. The instance must be disabled first.
        """
        instance = self._get_instance_or_raise(instance_id)

        if instance.status == PluginStatus.ENABLED:
            raise RuntimeError(
                f"Instance '{instance_id}' is currently ENABLED. Disable it before uninstalling."
            )

        plugin_id = instance.manifest.plugin_id
        del self.instances[instance_id]
        self.emit("plugin_uninstalled", {"instance_id": instance_id, "plugin_id": plugin_id})

    # ------------------------------------------------------------------
    # Queries
    # ------------------------------------------------------------------

    def get_instances(self, order: PluginOrder = None) -> List[PluginInstance]:
        """Return all instances, optionally filtered by order level."""
        instances = list(self.instances.values())
        if order is not None:
            instances = [i for i in instances if i.manifest.order == order]
        return instances

    def get_instance(self, instance_id: str) -> Optional[PluginInstance]:
        """Return a single instance by instance_id, or None if not found."""
        return self.instances.get(instance_id)

    # ------------------------------------------------------------------
    # Serialisation
    # ------------------------------------------------------------------

    def to_dict(self) -> Dict:
        """Return a serialisable snapshot of the registry state."""
        return {
            "available_plugins": [
                {
                    "plugin_id":    m.plugin_id,
                    "name":         m.name,
                    "order":        m.order.value,
                    "version":      m.version,
                    "description":  m.description,
                    "singleton":    m.singleton,
                    "config_schema": m.config_schema,
                }
                for m in self.manifests.values()
            ],
            "installed": [
                {
                    "instance_id":  i.instance_id,
                    "plugin_id":    i.manifest.plugin_id,
                    "name":         i.manifest.name,
                    "order":        i.manifest.order.value,
                    "status":       i.status.value,
                    "config":       i.config,
                    "installed_at": i.installed_at.isoformat(),
                    "error":        i.error,
                }
                for i in self.instances.values()
            ],
        }

    # ------------------------------------------------------------------
    # Event bus
    # ------------------------------------------------------------------

    def emit(self, event: str, data: Dict = None) -> None:
        """
        Emit an event to all direct subscribers and wildcard ('*') subscribers.
        """
        data = data or {}
        for callback in self._event_subscribers.get(event, []):
            try:
                callback(event, data)
            except Exception:
                pass  # subscribers must not crash the registry

        if event != "*":
            for callback in self._event_subscribers.get("*", []):
                try:
                    callback(event, data)
                except Exception:
                    pass

    def subscribe(self, event: str, callback: Callable) -> None:
        """
        Subscribe a callback to a named event or '*' for all events.

        The callback signature is: callback(event: str, data: Dict) -> None
        """
        self._event_subscribers.setdefault(event, []).append(callback)

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _get_instance_or_raise(self, instance_id: str) -> PluginInstance:
        instance = self.instances.get(instance_id)
        if instance is None:
            raise KeyError(f"No installed instance with instance_id='{instance_id}'.")
        return instance
