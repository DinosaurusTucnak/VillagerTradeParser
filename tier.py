from parser import Parser
from trade import Trade

class Tier(Parser):
    def __init__(self, lines, tier):
        super().__init__(lines)
        self.tier = int(tier)
        if self.tier > 5 or self.tier < 1:
            raise ValueError("A Villager's Tier must be on a scale from 1 to 5")
    trades = []

    def parse(self, i):
        while True:
            line = self.getLine(i)
            if not line:
                i += 1
                continue
            args = line.split()
            cmd = args[0].lower()
            args = args[1:]

            if cmd == "trade":
                t = Trade(self.lines, self.tier)
                i = t.parse(i + 1)
                self.trades.append(t)

            elif cmd in ["tier", "end"]:
                return i - 1
            else:
                raise SyntaxError(f"Parse Error: Unknown keyword {cmd} on line {i}: {line}")

            i += 1

    def getJSON(self):
        tradesJSON = [trade.getJSON() for trade in self.trades]
        json = ",\n".join(tradesJSON)
        xpReq = [0,10,70,150,250][self.tier - 1]
        return f'''{{
      "groups": [
        {{
          "num_to_select": 2.0,
          "trades": [
            {json}
          ]
        }}
      ],
      "total_exp_required": {xpReq}
}}'''
