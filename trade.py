# CONFIGURATION SETTINGS
# This parser as written does not mimic vanilla trades, alternative code which would is commented out.
# See Line 133 for Price Multiplier

from tradeParser import Parser
class MC_Item:
    def __init__(self, name, count = 1.0):
        if ':' not in name:
            name = "minecraft:" + name
        self.name = name
        self.count = float(count)
        print(f"Name: {self.name}")
        print(f"Count: {self.count}")
        if self.count > 64:
            raise ValueError("Item count greater than 64")

    def getJSON(self):
        if self.count == 1.0:
            return f'''{{
                    "type": "minecraft:item",
                    "name": "{self.name}"
}}'''
        else:
            print(f"Name: {self.name}")
            print(f"Count: {self.count}")
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
    def __init__(self, json, name, count = 1.0):
        super().__init__(name, count)
        self.json = f'''{{
    {json}
}}'''

    def getJSON(self):
        return self.json

class Trade(Parser):
    def __init__(self, lines, tier, config):
        super().__init__(lines)
        self.tier = tier
        self.config = config
    costA = None
    costB = None
    result = None

    def parse(self, i):
        raw = False
        json = ""
        while True:
            line = self.getLine(i)
            args = line.split()
            if not args:
                i += 1
                continue
            cmd = args[0].lower()
            args = args[1:]

            # Raw JSON items
            if raw:
                if cmd == "jscost":
                    if not self.costA:
                        if len(args) > 1:
                            self.costA = MC_ItemJSON(json, args[0], args[1])
                        else:
                            self.costA = MC_ItemJSON(json, args[0])
                    else:
                        if len(args) > 1:
                            self.costB = MC_ItemJSON(json, args[0], args[1])
                        else:
                            self.costB = MC_ItemJSON(json, args[0])
                    raw = False
                elif cmd == "jsresult":
                    if len(args) > 1:
                        self.result = MC_ItemJSON(json, args[0], args[1])
                    else:
                        self.result = MC_ItemJSON(json, args[0])
                    raw = False
                else:
                    json += self.lines[i]

            elif cmd in ["js", "jscost", "jsresult"]:
                json = ""
                raw = True

            # Summary Items
            elif cmd == "cost":
                if not self.costA:
                    if len(args) > 1:
                        self.costA = MC_Item(args[0], args[1])
                    else:
                        self.costA = MC_Item(args[0])
                else:
                    if len(args) > 1:
                        self.costB = MC_Item(args[0], args[1])
                    else:
                        self.costB = MC_Item(args[0])
            elif cmd == "result":
                if len(args) > 1:
                    self.result = MC_Item(args[0], args[1])
                else:
                    self.result = MC_Item(args[0])

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
            self.costA.count = float(self.costA.count * self.config["sale_tax"])
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
        ## Intended to use with "No Villager Discounts" Mod
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

