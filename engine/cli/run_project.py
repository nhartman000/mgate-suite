from .model_adapter import call_model

class Executor:
    def __init__(self, gitson, audit):
        self.gates = {g["gate_id"]: g for g in gitson["gates"]}
        self.audit = audit

    def run(self, entry_gate, user_input):
        current_gate = self.gates[entry_gate]
        context = user_input

        for _ in range(current_gate["execution"]["max_iterations"]):
            for step in current_gate["steps"]:

                if step["type"] == "test":
                    result = "pass" if step.get("condition") in context else "fail"
                    self.audit.log({
                        "gate_id": current_gate["gate_id"],
                        "step_id": step["step_id"],
                        "type": "test",
                        "input": context,
                        "result": result
                    })

                    if result == "fail":
                        break

                elif step["type"] == "operate":
                    output = call_model(step.get("prompt", "") + " " + context)
                    context = output

                    self.audit.log({
                        "gate_id": current_gate["gate_id"],
                        "step_id": step["step_id"],
                        "type": "operate",
                        "input": context,
                        "output": output,
                        "result": "continue"
                    })

                elif step["type"] == "route":
                    next_gate = step.get("next")
                    if next_gate:
                        return self.run(next_gate, context)

        return context
