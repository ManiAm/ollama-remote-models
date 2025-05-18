#!/usr/bin/env python3

import sys
import argparse
import re
import requests
import json
from datetime import timedelta
from tabulate import tabulate

model_block_regex = re.compile(r'(?s)<li x-test-model[^>]*>.*?</li>')
title_regex = re.compile(r'<span x-test-search-response-title>(.*?)</span>')
desc_regex = re.compile(r'<p class="max-w-lg break-words[^>]*>(.*?)</p>')
size_regex = re.compile(r'<span[^>]*x-test-size[^>]*>(\d+(?:x\d+)?(?:\.\d+)?[mbB])</span>')
pulls_regex = re.compile(r'<span x-test-pull-count[^>]*>([^<]+)</span>')
tags_regex = re.compile(r'<span x-test-tag-count[^>]*>([^<]+)</span>')
updated_regex = re.compile(r'<span x-test-updated[^>]*>([^<]+)</span>')


class Model:

    def __init__(self, name):
        self.Name = name
        self.Description = ""
        self.Size = ""
        self.Pulls = ""
        self.Tags = ""
        self.Updated = ""

    def __repr__(self):
        return f"<Model name={self.Name}, size={self.Size}, updated={self.Updated}>"

    def to_dict(self):
        return {
            "name": self.Name,
            "description": self.Description,
            "size": self.Size,
            "pulls": self.Pulls,
            "tags": self.Tags,
            "updated": self.Updated
        }


def parse_models(html):

    models = []

    model_blocks = model_block_regex.findall(html)

    if not model_blocks:
        raise ValueError("No models found in response")

    for block in model_blocks:

        title_match = title_regex.search(block)
        if not title_match:
            continue

        name = format_model_name(title_match.group(1))
        model_obj = Model(name)

        desc_match = desc_regex.search(block)
        if desc_match:
            model_obj.Description = desc_match.group(1).strip()

        size_matches = size_regex.findall(block)
        sizes = sorted([s.strip() for s in size_matches], key=extract_numeric_value)
        model_obj.Size = ", ".join(sizes)

        pulls_match = pulls_regex.search(block)
        if pulls_match:
            model_obj.Pulls = pulls_match.group(1).strip()

        tags_match = tags_regex.search(block)
        if tags_match:
            model_obj.Tags = tags_match.group(1).strip()

        updated_match = updated_regex.search(block)
        if updated_match:
            model_obj.Updated = updated_match.group(1).strip()

        models.append(model_obj)

    return models


def format_model_name(name):

    return name.strip().lower().replace(" ", "-")


def extract_numeric_value(size_str):

    size_str = size_str.lower().strip()

    # Composite format: 8x7b, 4x3.5m, etc.
    match = re.match(r'(\d+)x(\d+(?:\.\d+)?)([mb])$', size_str)
    if match:
        count, size, unit = match.groups()
        count = int(count)
        size = float(size)
    else:
        # Simple format: 7b, 344m, etc.
        match = re.match(r'(\d+(?:\.\d+)?)([mb])$', size_str)
        if match:
            count = 1
            size, unit = match.groups()
            size = float(size)
        else:
            raise ValueError(f"Invalid size string format: '{size_str}'")

    if unit == 'b':
        multiplier = 1_000_000_000
    elif unit == 'm':
        multiplier = 1_000_000
    else:
        raise ValueError(f"Unsupported unit '{unit}' in size string '{size_str}'")

    return count * size * multiplier

######################################################

def parse_relative_time(text):

    text = text.lower().strip()

    match = re.match(r"(\d+)\s+(day|month|year|week|hour|minute|second)s?\s+ago", text)
    if not match:
        return timedelta.max  # unknown format goes last

    value, unit = match.groups()
    value = int(value)

    if unit == "year":
        return timedelta(days=365 * value)
    elif unit == "month":
        return timedelta(days=30 * value)
    elif unit == "week":
        return timedelta(weeks=value)
    elif unit == "day":
        return timedelta(days=value)
    elif unit == "hour":
        return timedelta(hours=value)
    elif unit == "minute":
        return timedelta(minutes=value)
    elif unit == "second":
        return timedelta(seconds=value)

    return timedelta.max

######################################################

def generate_size_matrix(models):

    size_set = set()
    model_size_map = {}

    for m in models:
        sizes = extract_all_sizes(m.Size)
        model_size_map[m.Name] = sizes
        size_set.update(sizes)

    sorted_sizes = sorted(size_set, key=size_key)

    headers = ["Model"] + sorted_sizes
    rows = []

    for model in models:
        row = [model.Name]
        for size in sorted_sizes:
            row.append("✅" if size in model_size_map[model.Name] else "")
        rows.append(row)

    return tabulate(rows, headers, tablefmt="github")


def extract_all_sizes(size_str):

    return re.findall(r'\d+(?:x\d+)?[mb]', size_str.lower())


def size_key(size):

    match = re.match(r'(?:(\d+)x)?(\d+(?:\.\d+)?)([mb])', size.lower())
    if not match:
        return float('inf')
    mult, num, unit = match.groups()
    factor = 1_000_000_000 if unit == 'b' else 1_000_000
    mult = int(mult) if mult else 1
    return float(num) * mult * factor

######################################################

def generate_scrollable_html_table(models):

    size_set = set()
    model_size_map = {}

    for m in models:
        sizes = extract_all_sizes(m.Size)
        model_size_map[m.Name] = sizes
        size_set.update(sizes)

    sorted_sizes = sorted(size_set, key=size_key)

    # Header row
    header_html = "<tr><th style='position: sticky; top: 0; left: 0; z-index: 4; background: #f9f9f9; min-width: 140px;'>Model</th>" + "".join(
        f"<th style='position: sticky; top: 0; z-index: 2; background: #f9f9f9; white-space: nowrap; padding: 6px; min-width: 80px;'>{size}</th>"
        for size in sorted_sizes
    ) + "</tr>"

    # Data rows
    rows_html = ""
    for model in models:
        row_html = f"<td style='position: sticky; left: 0; background: #fff; z-index: 1; padding: 6px; white-space: nowrap; min-width: 140px;'>{model.Name}</td>"
        for size in sorted_sizes:
            row_html += "<td style='text-align: center; min-width: 80px;'>✅</td>" if size in model_size_map[model.Name] else "<td style='min-width: 80px;'></td>"
        rows_html += f"<tr>{row_html}</tr>"

    html = f"""
    <div style="max-height: 500px; overflow-y: auto; overflow-x: auto; border: 1px solid #ccc;">
        <table style="border-collapse: collapse; font-family: sans-serif; table-layout: auto;">
            {header_html}
            {rows_html}
        </table>
    </div>
    """

    return html

######################################################

def parse_args():

    parser = argparse.ArgumentParser(description="Get Ollama Remote Models")

    parser.add_argument(
        "--sort",
        choices=["name", "time"],
        default="name",
        help="Sort models by 'name' or 'time' (default: name)"
    )

    parser.add_argument(
        "--output",
        choices=["json", "markdown", "html"],
        default="json",
        help="Sort output format (default: json)"
    )

    parser.add_argument(
        "--filter",
        type=str,
        default="",
        help="Filter models by name substring (case-insensitive)"
    )

    return parser.parse_args()


if __name__ == "__main__":

    args = parse_args()

    response = requests.get("https://ollama.com/search")
    response.raise_for_status()

    models = parse_models(response.text)

    if args.filter:
        models = [
            m for m in models if args.filter.lower() in m.Name.lower()
        ]

    if args.sort == "name":
        models.sort(key=lambda m: m.Name.lower())
    elif args.sort == "time":
        models.sort(key=lambda m: parse_relative_time(m.Updated))

    if args.output == "json":

        models_dicts = [model.to_dict() for model in models]
        json_output = json.dumps(models_dicts, indent=2)
        print(json_output)

    elif args.output == "markdown":

        str = generate_size_matrix(models)
        print(str)

    elif args.output == "html":

        str = generate_scrollable_html_table(models)
        print(str)

    else:

        print(f"Unknown output format {args.output}")
        sys.exit(2)
