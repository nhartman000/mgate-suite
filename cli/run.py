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

    path = Path(sys.argv[1])
    config = json.loads(path.read_text())

    console.print(f"[bold cyan]🚀 Starting NychForge Optimization → {config['name']}[/bold cyan]")

    optimizer = RecursiveOptimizer(max_iterations=12)

    def evaluate(state):
        return (state.get("performance", 0) * 0.5 +
                state.get("coherence", 0) * 0.3 +
                state.get("stability", 0) * 0.2)

    def edit(state, intensity):
        state = state.copy()
        state["performance"] = min(1.0, state.get("performance", 0) + 0.18 * intensity)
        state["coherence"] = min(1.0, state.get("coherence", 0) + 0.12 * intensity)
        state["stability"] = max(0.5, state.get("stability", 0) - 0.08 * intensity)
        return state

    result = optimizer.optimize_trait(
        trait_name=config["optimization_targets"][0],
        initial_state=config.get("initial_state", {}),
        evaluate_fn=evaluate,
        edit_fn=edit
    )

    console.print("\n[bold green]✅ Optimization Complete![/bold green]")
    console.print(f"Best Version: [yellow]{result['best_version']}[/yellow]")
    console.print(f"Final Performance: [bold]{result['final_state'].get('performance'):.3f}[/bold]")

    # Show Nych Symbols
    if result["nych_symbols"]:
        console.print("\n[cyan]Nych Symbols Generated:[/cyan]")
        for sym in result["nych_symbols"][:5]:
            console.print(f"  {sym}")

    # APK Export Prompt
    choice = console.input("\nExport APK? (b)uilder / (r)untime / [none]: ").strip().lower()
    from exporter.android.builder import APKBuilder
    builder = APKBuilder(config['name'])
    
    if choice.startswith('b'):
        console.print(builder.export_builder_apk(config))
    elif choice.startswith('r'):
        console.print(builder.export_runtime_apk(config))

if __name__ == "__main__":
    main()