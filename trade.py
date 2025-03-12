# This number is multiplied costs that result in emeralds
SALETAX = 2

# This parser as written does not mimic vanilla trades, alternative code which would is commented out.

class MC_Item:
    def __init__(self, name, count = 1.0):
        if ':' not in name:
            name = "minecraft:" + name

        self.name = name
        self.count = float(count)

    def getJSON(self):
        if self.count == 1.0:
            return f'''{{
                    "type": "minecraft:item",
                    "name": "{self.name}"
}}'''
        else:
            return f'''{{
                    "type": "minecraft:item",
                    "functions": [
                      {{
                        "add": false,
                        "count": {self.count},
                        "function": "minecraft:set_count"
                      }}
                    ],
                    "name": "{self.name}"
}}'''

class MC_ItemJSON(MC_Item):
    def __init__(self, json, name, count):
        super().__init__(name, count)
        self.json = json

    def getJSON(self):
        return self.json

def get(l, i, defValue):
    return l[i] if i < len(l) else defValue

from parser import Parser
class Trade(Parser):
    def __init__(self, lines, tier):
        super().__init__(lines)
        self.tier = tier
    costA = None
    costB = None
    result = None

    def parse(self, i):
        raw = False
        json = ""
        while True:
            line = self.getLine(i)
            if not line:
                i += 1
                continue
            args = line.split()
            cmd = args[0].lower()
            args = args[1:]

            # Raw JSON items
            if raw:
                if cmd == "jscost":
                    if not self.costA:
                        self.costA = MC_ItemJSON(json, args[0], get(args, 1, 1.0))
                    else:
                        self.costB = MC_ItemJSON(json, args[0], get(args, 1, 1.0))
                    raw = False
                elif cmd == "jsresult":
                    self.result = MC_ItemJSON(json, args[0], get(args, 1, 1.0))
                    raw = False
                else:
                    json += self.lines[i] + '\n'

            elif cmd in ["js", "jscost", "jsresult"]:
                json = ""
                raw = True

            # Summary Items
            elif cmd == "cost":
                if not self.costA:
                    self.costA = MC_Item(args[0], get(args, 1, 1.0))
                else:
                    self.costB = MC_Item(args[0], get(args, 1, 1.0))
            elif cmd == "result":
                self.result = MC_Item(args[0], get(args, 1, 1.0))

            elif cmd in ["trade", "tier", "end"]:
                return i - 1
            else:
                raise SyntaxError(f"Parse Error: Unknown keyword {cmd} on line {i}: {line}")

            i += 1

    def getJSON(self):
        if not isinstance(self.costA, MC_Item):
            raise RuntimeError("Parse Error: costA is not a MC_Item. Is a Cost Defined?")
        if not isinstance(self.result, MC_Item):
            raise RuntimeError("Parse Error: result is not a MC_Item. Is a Result Defined?")
        sell = self.result.name == "minecraft:emerald"

        if sell:
            self.cost_a.price *= SALETAX
        cost_a = f'"cost_a": {self.costA.getJSON()}'
        if self.costB is MC_Item:
            cost_b = ",\n" + f'"cost_b": {self.costB.getJSON()}'
        else: cost_b = ''

        ## VANILLA LIKE
        uses = 16.0 if sell else 12.0
        ## CUSTOM 150%
        # uses = 24.0 if sell else 18.0

        xp = 0
        # Tier 1: 1 2, Tier 2: 5 10, Tier 3: 10 20, Tier 5: 15 30

        if self.tier < 2:
            xp = 1 + int(sell)
        else:
            xp = (self.tier - 1) * 5 * (1 + int(sell))
        if xp < 0:
            # This Shouldn't be possible if tiers are data checked to be 1 to 5
            raise ValueError("Negative XP value calculated.")

        ## VANILLA LIKE (0.05 or 0.2)   *or 0.1*
        # multiplier = 0.05 if sell else 0.2

        ## CUSTOM Automated Percentage Multiplier Value (0.00 to 0.40)
        ## NOTE: Max discount by trading (25 reputation) is 12.5% price
        multiplier = float(int(0.125 * self.costA.count) / 20)
        if not multiplier and self.costA.count > 2:
            multiplier = 0.05

        return f'''{{
                {cost_a}{cost_b},
                "max_uses": {uses},
                "price_multiplier": {multiplier},
                "result": {self.result.getJSON()},
                "reward_experience": true,
                "trader_experience": {xp}
}}'''

