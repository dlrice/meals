#!/usr/bin/env python3
from collections import defaultdict
from glob import glob
import os.path
import os
import re
import yaml
from jinja2 import Template

plan_path = "./plan.yaml"


def parse_ingredient(ingredient):
    p_units = "|".join(
        [
            "bag",
            "bunch",
            "can",
            "cups",
            "cup",
            "g",
            "handful",
            "ml",
            "square",
            "stalks",
            "tbsp",
            "tin",
            "tsp",
        ]
    )
    p = re.compile(rf"(?P<quantity>[0-9./]+)\s?(?P<units>{p_units})?(?P<item>.*)")
    m = p.match(ingredient)
    if not m:
        return
    q = float(m.group("quantity"))
    u = m.group("units")
    if u:
        u = u.strip()
    i = m.group("item").strip()
    return q, u, i


def get_yaml(path):
    with open(path) as f:
        return yaml.load(f, yaml.Loader)


def build():
    plan = get_yaml(plan_path)
    L = []
    for meal_path in glob("./meals/*.yaml"):
        meal = get_yaml(meal_path)
        L += meal["ingredients"]
    ingredient_to_quantity = defaultdict(float)
    ingredient_to_unit = {}
    for el in set(L):
        q, u, i = parse_ingredient(el)
        if u:
            if i in ingredient_to_unit:
                if ingredient_to_unit[i] != u:
                    print(f"{i}: {ingredient_to_unit[i]} != {u}")
                    continue
            else:
                ingredient_to_unit[i] = u
        ingredient_to_quantity[i] += q
    for i in sorted(ingredient_to_quantity):
        q = ingredient_to_quantity[i]
        u = ingredient_to_unit.get(i, "")
        print(f"{i}: {q} {u}")


if __name__ == "__main__":
    build()
