#!/usr/bin/env python3
from glob import glob
import os.path
import os
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


def main():
    shutil.rmtree(build_path, ignore_errors=True)
    os.makedirs(build_path)
    shutil.copy("./style.css", build_path)
    meal_template = get_template("./templates/meal.html")
    plan_template = get_template("./templates/index.html")
    plan = get_yaml(plan_path)

    meal_data = {}
    for meal_path in glob("./meals/*.yaml"):
        print(meal_path)
        meal_filename = os.path.split(meal_path)[1]
        meal_name = os.path.splitext(meal_filename)[0]
        meal_html_name = meal_name + ".html"
        meal_html_path = os.path.join(build_path, meal_html_name)
        meal_data[meal_name] = get_yaml(meal_path)
        write_template(meal_html_path, meal_template, meal_data[meal_name])

    plan_html_path = os.path.join(build_path, "index.html")
    d = {"meal_data": meal_data, "plan": plan}
    write_template(plan_html_path, plan_template, d)


if __name__ == "__main__":
    main()
