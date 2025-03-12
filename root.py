from parser import Parser
from tier import Tier

class Root(Parser):
    def __init__(self, lines):
        super().__init__(lines)
    tiers = []

    def parse(self, i):
        while True:
            line = self.getLine(i)
            args = line.split()
            if not args:
                i += 1
                continue
            cmd = args[0].lower()
            args = args[1:]

            if cmd == "tier":
                t = Tier(self.lines, args[0])
                i = t.parse(i + 1)
                self.tiers.append(t)

            elif cmd == "end":
                return 0
            else:
                raise SyntaxError(f"Parse Error: Unknown keyword {cmd} on line {i}: {line}")

            i += 1

    def getJSON(self):
        tiersJSON = [tiers.getJSON() for tiers in self.tiers]
        json = ",\n".join(tiersJSON)
        return f'''{{
  "tiers": [
    {json}
  ]
}}'''
