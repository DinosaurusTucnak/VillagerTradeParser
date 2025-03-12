class Parser:
    def __init__(self, lines):
        self.lines = lines
        if self is Parser:
            raise TypeError("Can't implement abstract class Parser")

    lines = []

    def getLine(self, i):
        # Check for EOF
        if i > len(self.lines):
            return "end"
        line = self.lines[i]
        # Check for Comments
        if line.lstrip().startswith("//"):
            return ""
        return line

    def parse(self, i):
        raise NotImplementedError("parse function not implemented")

    def getJSON(self):
        raise NotImplementedError("getJSON function not implemented")
