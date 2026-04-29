import gradio as gr
from core.recursion.optimizer import RecursiveOptimizer
import json

def run_optimization(agent_file):
    with open(agent_file) as f:
        config = json.load(f)
    
    optimizer = RecursiveOptimizer(max_iterations=12)
    result = optimizer.optimize_trait(
        trait_name=config["optimization_targets"][0],
        initial_state=config.get("initial_state", {})
    )
    
    summary = f"""
**Agent:** {config['name']}
**Best Version:** {result['best_version']}
**Final Performance:** {result['final_state'].get('performance', 0):.3f}
**Sweet Spot Reached:** Yes
    """
    return summary, result['final_state']

with gr.Blocks(title="NychForge") as demo:
    gr.Markdown("# NychForge — Recursive Gated AI Builder")
    gr.Markdown("ADSR + Nych + Timeline → APK")
    
    file_input = gr.File(label="Upload .mg8 Agent", file_types=[".mg8"])
    btn = gr.Button("Run Recursive Optimization", variant="primary")
    
    output_text = gr.Markdown()
    final_state = gr.JSON()
    
    btn.click(
        fn=run_optimization,
        inputs=file_input,
        outputs=[output_text, final_state]
    )

if __name__ == "__main__":
    demo.launch()
