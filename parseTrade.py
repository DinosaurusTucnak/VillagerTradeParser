import os
from root import Root

LOCATION = os.path.dirname(__file__) + '/'
# Assumes desired mods are in a directory sibling to the script "mods/"
SRC = LOCATION + "input/"
DEST = LOCATION + "output/"

def main():
    # Verify Path
    if not os.path.exists(SRC):
        print(f"Error: no directory {SRC}")
        return -1

    if not os.path.exists(DEST):
        print(f"Error: no directory {DEST}")
        return -1

    for trade in os.scandir(SRC):
        # Open Template, Read lines. First line reserved for file name.
        file = open(trade, 'r')
        name = file.readline().strip()
        lines = file.readlines()
        parser = Root(lines)
        file.close()

        # Parse Template, save string to DEST/name
        parser.parse(0)
        parsed = parser.getJSON()
        with open(DEST + name, 'w') as fout:
            fout.write(parsed)

if __name__ == "__main__":
    main()
