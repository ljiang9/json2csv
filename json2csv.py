#!/usr/bin/env python3
"""json2csv — JSON 对象数组转 CSV/TSV。

把一个 JSON 数组（每个元素是一个对象）拍平成表格输出。
纯标准库，离线运行。
"""
import argparse
import csv
import io
import json
import sys

VERSION = "0.1.0"


def flatten(obj, prefix="", sep="."):
    """把嵌套对象拍平成 {\"a.b\": v}。列表/标量原样保留。"""
    flat = {}
    for key, value in obj.items():
        path = f"{prefix}{sep}{key}" if prefix else str(key)
        if isinstance(value, dict):
            flat.update(flatten(value, path, sep))
        else:
            flat[path] = value
    return flat


def cell_str(value):
    """把单元格值转成字符串。嵌套结构（列表）用 JSON 编码，保持可读。"""
    if value is None:
        return ""
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (dict, list)):
        return json.dumps(value, ensure_ascii=False)
    return str(value)


def load_json(source):
    """从文件或 stdin 读取 JSON。返回解析后的对象。"""
    try:
        if source == "-":
            text = sys.stdin.read()
        else:
            with open(source, "r", encoding="utf-8") as f:
                text = f.read()
    except FileNotFoundError:
        print(f"error: 文件不存在：{source}", file=sys.stderr)
        sys.exit(2)
    except OSError as e:
        print(f"error: 无法读取文件：{e}", file=sys.stderr)
        sys.exit(2)
    if not text.strip():
        print("error: 输入为空，没有可转换的数据", file=sys.stderr)
        sys.exit(1)
    try:
        return json.loads(text)
    except json.JSONDecodeError as e:
        print(f"error: 输入不是合法 JSON（第 {e.lineno} 行）：{e.msg}", file=sys.stderr)
        sys.exit(2)


def convert(data, columns=None, flatten_nested=False, no_header=False, tsv=False):
    """data: 对象数组。返回 CSV 文本。"""
    if not isinstance(data, list):
        print("error: 顶层 JSON 必须是数组（对象列表）", file=sys.stderr)
        sys.exit(1)
    if not data:
        print("error: 数组为空，没有可转换的数据", file=sys.stderr)
        sys.exit(1)
    for i, row in enumerate(data):
        if not isinstance(row, dict):
            print(f"error: 第 {i + 1} 个元素不是对象（是 {type(row).__name__}），无法转表格", file=sys.stderr)
            sys.exit(1)

    rows = [flatten(r) if flatten_nested else dict(r) for r in data]

    if columns:
        header = columns
    else:
        # 保持首次出现顺序收集所有键
        header = []
        for r in rows:
            for k in r:
                if k not in header:
                    header.append(k)

    buf = io.StringIO()
    writer = csv.writer(buf, delimiter="\t" if tsv else ",",
                        lineterminator="\n")
    if not no_header:
        writer.writerow(header)
    for r in rows:
        writer.writerow([cell_str(r.get(k)) for k in header])
    return buf.getvalue()


def build_parser():
    p = argparse.ArgumentParser(
        prog="json2csv",
        description="JSON 对象数组转 CSV/TSV。纯本地，离线运行。",
    )
    p.add_argument("file", nargs="?", default="-",
                   help="输入的 JSON 文件（默认从 stdin 读取，也可用 - 显式指定）")
    p.add_argument("--stdin", action="store_true", help="从 stdin 读取（与 file=- 等价）")
    p.add_argument("--out", metavar="FILE", help="输出到文件（默认 stdout）")
    p.add_argument("--columns", metavar="a,b,c",
                   help="只输出这些列，并按给定顺序排列（逗号分隔）")
    p.add_argument("--flatten", action="store_true",
                   help="把嵌套对象拍平为 a.b 形式的列；不加此选项时嵌套值以 JSON 字符串填入单元格")
    p.add_argument("--no-header", action="store_true", help="不输出表头行")
    p.add_argument("--tsv", action="store_true", help="输出 TSV（制表符分隔）而非 CSV")
    p.add_argument("--version", action="version", version=f"%(prog)s {VERSION}")
    return p


def main(argv=None):
    args = build_parser().parse_args(argv)
    source = "-" if args.stdin else args.file
    data = load_json(source)
    columns = [c.strip() for c in args.columns.split(",")] if args.columns else None
    out = convert(data, columns=columns, flatten_nested=args.flatten,
                  no_header=args.no_header, tsv=args.tsv)
    if args.out:
        try:
            with open(args.out, "w", encoding="utf-8", newline="") as f:
                f.write(out)
        except OSError as e:
            print(f"error: 无法写入输出文件：{e}", file=sys.stderr)
            sys.exit(2)
    else:
        sys.stdout.write(out)


if __name__ == "__main__":
    main()
