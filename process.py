#!/usr/bin/env python3

import os

tag_defs = {
    "!": "Event",
    # building tags
    "b": "Building",
    "*": "Space",
    "c": "City",

    # ???
    "s": "Science",
    "n": "Power",

    # planet tags
    "e": "Earth",
    "j": "Jovian",
    #"v": "Venus",

    # green tags
    "a": "Animal",
    "p": "Plant",
    "m": "Microbe",
}
tag_order = [
    tag_defs["b"],
    tag_defs["*"],
    tag_defs["!"],
    tag_defs["s"],
    tag_defs["n"],
    tag_defs["e"],
    tag_defs["p"],
    tag_defs["m"],
    tag_defs["j"],
    tag_defs["c"],
    tag_defs["a"],
]

income_defs = {
    "m": "M€",
    "s": "Steel",
    "t": "Titanium",
    "p": "Plant",
    "n": "Energy",
    "h": "Heat",
}
terraforming_defs = {
    "h": "Raise the Heat",
    "w": "Place an Ocean Tile",
    "o": "Raise the Oxygen",
    "tr": "Raise your TR",
    "g": "Place a Greenery Tile",
}

class Card:
    def __init__(self, cost):
        self.cost = cost
        self.requirements = []
        self.tags = []
        self.name = None
        self.income = []
        self.terraforming = []
        self.vps = 0
        self.is_complete = True
    def __repr__(self):
        s = self.name + ": " + str(self.cost) + "M€"
        if self.requirements:
            s += " " + ", ".join("{}{}{}".format(*req) for req in self.requirements)
        if self.tags:
            s += " [{}]".format(", ".join(self.tags))
        if self.income:
            s += ", " + ", ".join(
                "{}{} {} income".format(
                    ("+" if x[1] >= 0 else ""), x[1], x[0],
                )
            for x in self.income)
        if self.terraforming:
            s += ", " + ", ".join(self.terraforming)
        if self.vps:
            s += ", {}VPs".format(self.vps)
        if not self.is_complete:
            s += " (incomplete)"
        return s

    tsv_columns = [
        "name",
        "cost",
    ] + list(sorted(tag_defs.values(), key=tag_order.index)) + [
    ]
    def to_tsv(self):
        return "\t".join(
            {
                "name": self.name,
                "cost": str(self.cost),
                **{
                    name: str(sum(1 for tag in self.tags if tag == name))
                    for name in tag_defs.values()
                }
            }[column]
            for column in Card.tsv_columns
        )


def parse_stream(stream):
    cards = []
    for line in stream:
        tokens = line.split()
        card = Card(int(tokens[0]))
        for i, token in enumerate(tokens[1:]):
            if token.startswith("[") and token.endswith("]"):
                for t in token[1:-1]:
                    card.tags.append(tag_defs[t])
            elif token.endswith("vp"):
                card.vps = int(token[:-2])
            elif token == "*":
                card.is_complete = False
            elif token.startswith((">=", "<=")):
                if token.endswith("%"):
                    card.requirements.append(("O2", token[:2], int(token[2:-1])))
                elif token.endswith("w"):
                    card.requirements.append(("Oceans", token[:2], int(token[2:-1])))
                elif token.endswith("C"):
                    card.requirements.append(("Temp", token[:2], int(token[2:-1])))
                elif token.endswith("g"):
                    card.requirements.append(("Your Greenery", token[:2], int(token[2:-1])))
                elif token.endswith("c"):
                    card.requirements.append(("Cities", token[:2], int(token[2:-1])))
                elif token.endswith("]"):
                    card.requirements.append((tag_defs[token[-2]] + " tags", token[:2], int(token[2:-3])))
                elif token.endswith("i"):
                    card.requirements.append((income_defs[token[-2]] + " income", token[:2], int(token[2:-2])))
                else:
                    assert False, "requirement code: " + token[-1]
            elif token.startswith(("+", "-")) and token.endswith("i"):
                card.income.append((income_defs[token[-2]], int(token[:-2])))
            elif token in ("h", "w", "o", "tr", "g"):
                card.terraforming.append(terraforming_defs[token])
            else:
                card.name = " ".join(tokens[i+1:])
                break
        cards.append(card)
    return cards

def main():
    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "data.txt")) as f:
        cards = parse_stream(f)
    print("\t".join(Card.tsv_columns))
    print("\n".join(card.to_tsv() for card in cards))

if __name__ == "__main__":
    main()
