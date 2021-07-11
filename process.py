#!/usr/bin/env python3

import os
import itertools

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
income_order = [
    income_defs["m"],
    income_defs["s"],
    income_defs["t"],
    income_defs["p"],
    income_defs["n"],
    income_defs["h"],
]

terraforming_defs = {
    "h": "Heat",
    "w": "Ocean",
    "o": "Oxygen",
    "tr": "TR",
    "g": "Greenery",
}
terraforming_long_names = {
    terraforming_defs["h"]: "Raise the Heat",
    terraforming_defs["w"]: "Place an Ocean Tile",
    terraforming_defs["o"]: "Raise the Oxygen",
    terraforming_defs["tr"]: "Raise your TR",
    terraforming_defs["g"]: "Place a Greenery Tile",
}
terraforming_order = [
    terraforming_defs["tr"],
    terraforming_defs["h"],
    terraforming_defs["w"],
    terraforming_defs["o"],
    terraforming_defs["g"],
]

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
            s += ", " + ", ".join(terraforming_long_names[n] for n in self.terraforming)
        if self.vps:
            s += ", {}VPs".format(self.vps)
        if not self.is_complete:
            s += " (incomplete)"
        return s

    tsv_column_groups = [
        [
            "name",
            "cost",
        ],
        list(sorted(tag_defs.values(), key=tag_order.index)),
        list(sorted(income_defs.values(), key=income_order.index)),
        list(sorted(terraforming_defs.values(), key=terraforming_order.index)),
    ]
    def to_tsv(self):
        return "\t".join(itertools.chain(
            ({
                "name": self.name,
                "cost": str(self.cost),
            }[column] for column in Card.tsv_column_groups[0]),
            ({
                name: str(sum(1 for tag in self.tags if tag == name))
                for name in tag_defs.values()
            }[column] for column in Card.tsv_column_groups[1]),
            ({
                name: str(sum(amount for n, amount in self.income if n == name))
                for name in income_defs.values()
            }[column] for column in Card.tsv_column_groups[2]),
            ({
                name: str(sum(1 for n in self.terraforming if n == name))
                for name in terraforming_defs.values()
            }[column] for column in Card.tsv_column_groups[3]),
        ))


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
    print("\t".join(itertools.chain(*Card.tsv_column_groups)))
    print("\n".join(card.to_tsv() for card in cards))

if __name__ == "__main__":
    main()
