import os
from root import Root

LOCATION = f"{os.path.dirname(__file__)}/"
# Assumes desired mods are in a directory sibling to the script "mods/"
SRC = f"{LOCATION}input/"
DEST = f"{LOCATION}output/"

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
        with open(trade, 'r', encoding='utf-8') as file:
            name = file.readline().strip()
            print(f"Reading {trade} to {DEST + name}")
            lines = file.readlines()
            parser = Root(lines)

        # Parse Template, save string to DEST/name
        parser.parse(0)
        parsed = ''
        parsed = parser.getJSON()
        with open(DEST + name, 'w', encoding='utf-8') as fout:
            fout.write(parsed)

if __name__ == "__main__":
    main()
