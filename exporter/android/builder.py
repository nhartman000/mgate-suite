from pathlib import Path

class APKBuilder:
    def __init__(self, agent_name: str):
        self.agent_name = agent_name
        self.build_dir = Path(f"builds/{agent_name}")
        self.build_dir.mkdir(parents=True, exist_ok=True)

    def export_builder_apk(self, config: dict):
        """Full recursive self-editing APK"""
        manifest = {
            "package": f"com.nychforge.{self.agent_name.lower()}",
            "type": "builder",
            "version": "1.0.0",
            "features": ["recursion", "adsr_gating", "timeline", "nych_protocol"],
            "editable": True,
            "max_iterations": 25
        }
        print(f"📱 Builder APK ready: {self.build_dir}/builder.apk")
        return {"status": "success", "type": "builder", "manifest": manifest}

    def export_runtime_apk(self, config: dict):
        """Locked production agent"""
        manifest = {
            "package": f"com.nychforge.{self.agent_name.lower()}",
            "type": "runtime",
            "version": "1.0.0",
            "features": ["chat", "gated_inference"],
            "editable": False
        }
        print(f"📱 Runtime APK ready: {self.build_dir}/runtime.apk")
        return {"status": "success", "type": "runtime", "manifest": manifest}