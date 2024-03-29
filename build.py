#!/usr/bin/env python3
from collections import defaultdict
from glob import glob
import os.path
import os
import re
import shutil
import yaml
from jinja2 import Template

build_path = "./build"
plan_path = "./plan.yaml"


def get_template(path):
    with open(path) as f:
        return Template(f.read())


def get_yaml(path):
    with open(path) as f:
        return yaml.load(f, yaml.Loader)


def write_template(path, template, d):
    with open(path, "w") as f:
        f.write(template.render(**d))


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
            "L",
            "ml",
            "square",
            "stalks",
            "tbsp",
            "tin",
            "tsp",
        ]
    )
    p = re.compile(rf"(?P<quantity>[0-9./]+)\s?(?P<units>{p_units})?\s(?P<item>.*)")
    m = p.match(ingredient)
    if not m:
        return
    q = float(m.group("quantity"))
    u = m.group("units")
    if u:
        u = u.strip()
    i = m.group("item").strip()
    return q, u, i


def get_weekly_items():
    plan = get_yaml(plan_path)
    ingredient_to_quantity = defaultdict(float)
    ingredient_to_unit = {}
    for day in plan.values():
        for plan_meal in day.values():
            meal_data = get_yaml(f"./meals/{plan_meal['name']}.yaml")
            plan_servings = plan_meal["servings"]
            meal_servings = meal_data["servings"]
            servings_ratio = plan_servings / meal_servings
            for ingredient in meal_data["ingredients"]:
                q, u, i = parse_ingredient(ingredient)
                ingredient_to_quantity[i] += q * servings_ratio
                if u:
                    if i in ingredient_to_unit:
                        assert (
                            ingredient_to_unit[i] == u
                        ), f"{ingredient}:{ingredient_to_unit[i]} != {u}"
                    else:
                        ingredient_to_unit[i] = u
    return [
        {
            "quantity": ingredient_to_quantity[i],
            "unit": ingredient_to_unit.get(i, ""),
            "name": i,
        }
        for i in sorted(ingredient_to_quantity)
    ]


def build():
    shutil.rmtree(build_path, ignore_errors=True)
    os.makedirs(build_path)
    shutil.copy("./style.css", build_path)
    meal_template = get_template("./templates/meal.html")
    plan_template = get_template("./templates/index.html")
    plan = get_yaml(plan_path)

    meal_data = {}
    for meal_path in glob("./meals/*.yaml"):
        meal_filename = os.path.split(meal_path)[1]
        meal_name = os.path.splitext(meal_filename)[0]
        meal_html_name = meal_name + ".html"
        meal_html_path = os.path.join(build_path, meal_html_name)
        meal_data[meal_name] = get_yaml(meal_path)
        write_template(meal_html_path, meal_template, meal_data[meal_name])

    plan_html_path = os.path.join(build_path, "index.html")
    d = {"meal_data": meal_data, "plan": plan}
    write_template(plan_html_path, plan_template, d)

    shopping_list_html_path = os.path.join(build_path, "shopping-list.html")
    shopping_list_template = get_template("./templates/shopping-list.html")
    d = {"items": get_weekly_items()}
    write_template(shopping_list_html_path, shopping_list_template, d)


if __name__ == "__main__":
    build()
