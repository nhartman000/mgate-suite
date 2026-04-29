class NychSymbol:
    """Symbolic representation for self-editing logic"""
    def __init__(self, name: str, meaning: str, action: str):
        self.name = name
        self.meaning = meaning
        self.action = action

    def __str__(self):
        return f"[{self.name}] → {self.action}"
