import sys
import json
from pathlib import Path
from rich.console import Console
from core.recursion.optimizer import RecursiveOptimizer

console = Console()

def main():
    if len(sys.argv) < 2:
        console.print("[red]Usage: nychforge <agent_file.mg8>[/red]")
        sys.exit(1)

    config = json.loads(Path(sys.argv[1]).read_text())
    console.print(f"[bold cyan]🚀 NychForge → {config['name']}[/bold cyan]")

    optimizer = RecursiveOptimizer(max_iterations=12)
    result = optimizer.optimize_trait(
        trait_name=config["optimization_targets"][0],
        initial_state=config.get("initial_state", {})
    )

    console.print("\n[bold green]✅ Optimization Complete![/bold green]")

    # Timeline Navigation
    if console.input("\nView best version or jump? (b/j/none): ").strip().lower() == "b":
        result['timeline'].get_best()

    # APK Export
    choice = console.input("\nExport APK? (b)uilder / (r)untime / none: ").strip().lower()
    from exporter.android.builder import APKBuilder
    builder = APKBuilder(config['name'])
    if choice.startswith('b'):
        console.print(builder.export_builder_apk(config))
    elif choice.startswith('r'):
        console.print(builder.export_runtime_apk(config))

if __name__ == "__main__":
    main()