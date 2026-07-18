#!/usr/bin/env python3
"""leak_scan.py — 发布前防泄漏全文闸。

用法: python3 leak_scan.py <目录> [--deny deny_list.txt]
deny_list.txt: 每行一个禁词(人名/公司/邮箱域/内部路径/船名…),# 开头为注释。
命中任何禁词 → 列出文件:行 → exit 1(CI/发布脚本据此挡住)。

模式(在真实系统里验证过):白名单渲染 + 发布前全文扫描双闸——
只有明确该去的内容才进发布目录,然后仍然全文扫一遍,两层都过才出门。
"""
import argparse, os, re, sys

DEFAULT_DENY = os.path.join(os.path.dirname(os.path.abspath(__file__)), "deny_list.txt")
SKIP_DIRS = {".git", "node_modules", "__pycache__", ".venv"}
SKIP_EXT = {".png", ".jpg", ".jpeg", ".gif", ".pdf", ".db", ".sqlite", ".zip", ".xls", ".xlsx"}

def load_deny(path):
    terms = []
    with open(path, encoding="utf-8") as f:
        for ln in f:
            t = ln.strip()
            if t and not t.startswith("#"):
                terms.append(t.lower())
    return terms

def scan(root, terms):
    hits = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for fn in filenames:
            if os.path.splitext(fn)[1].lower() in SKIP_EXT:
                continue
            p = os.path.join(dirpath, fn)
            try:
                txt = open(p, encoding="utf-8", errors="replace").read()
            except OSError:
                continue
            low = txt.lower()
            for t in terms:
                if t in low:
                    for i, ln in enumerate(low.splitlines(), 1):
                        if t in ln:
                            hits.append((os.path.relpath(p, root), i, t))
                            break   # 每文件每词报一次
    return hits

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("root")
    ap.add_argument("--deny", default=DEFAULT_DENY)
    a = ap.parse_args()
    terms = load_deny(a.deny)
    if not terms:
        print("⚠ deny list 为空——闸没有牙齿"); sys.exit(2)
    hits = scan(a.root, terms)
    if hits:
        print(f"❌ LEAK SCAN 命中 {len(hits)} 处:")
        for f, i, t in hits:
            print(f"  {f}:{i}  ← '{t}'")
        sys.exit(1)
    print(f"✅ leak scan 通过({len(terms)} 禁词,0 命中)")

if __name__ == "__main__":
    main()
