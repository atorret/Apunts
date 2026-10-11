"""Replace the macro \\phi (not followed by a letter) by \\varphi in the given files."""
import pathlib
import re
import sys

PAT = re.compile(r"\\phi(?![a-zA-Z])")

for name in sys.argv[1:]:
    p = pathlib.Path(name)
    t = p.read_text(encoding="utf-8")
    n = len(PAT.findall(t))
    p.write_text(PAT.sub(lambda m: r"\varphi", t), encoding="utf-8")
    print(f"{name}: {n}")
