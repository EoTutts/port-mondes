import shutil
from pathlib import Path
root = Path(__file__).resolve().parents[1]
overlay = root / "overlay"
shutil.copytree(root / "compat/source", overlay, dirs_exist_ok=True, ignore=shutil.ignore_patterns("__pycache__"))
for p in (root / "compat/native").iterdir():
    target = overlay / "compat" / ("lib" if p.name == "libffi.so.6" else "licenses") / p.name
    target.parent.mkdir(parents=True, exist_ok=True); shutil.copyfile(p, target)
print("Overlay: private libffi6, launcher and speech integration only")
