"""Pin the old Python ABI dependency from Ubuntu's official archived index."""
import hashlib
import io
import json
import lzma
from pathlib import Path
import tarfile
import urllib.request

HERE = Path(__file__).resolve().parent
BASE = "https://old-releases.ubuntu.com/ubuntu/"
index = urllib.request.urlopen(BASE+"dists/eoan/main/binary-arm64/Packages.xz", timeout=60).read()
text = lzma.decompress(index).decode("utf-8")
paragraph = next(p for p in text.split("\n\n") if p.startswith("Package: libffi6\n"))
meta = dict(line.split(": ",1) for line in paragraph.splitlines() if ": " in line and not line.startswith(" "))
data = urllib.request.urlopen(BASE+meta["Filename"], timeout=60).read()
assert hashlib.sha256(data).hexdigest() == meta["SHA256"]
(HERE/"libffi6-arm64.deb").write_bytes(data)
assert data[:8] == b"!<arch>\n"
offset = 8
target = HERE/"port-compat"
target.mkdir(exist_ok=True)
while offset < len(data):
    header=data[offset:offset+60]; size=int(header[48:58]); name=header[:16].decode().strip().rstrip("/")
    body=data[offset+60:offset+60+size]; offset += 60+size+size%2
    if not name.startswith("data.tar"): continue
    with tarfile.open(fileobj=io.BytesIO(body), mode="r:*") as archive:
        library=next(m for m in archive.getmembers() if m.isfile() and "/libffi.so.6." in m.name)
        content=archive.extractfile(library).read()
        assert content[:4] == b"\x7fELF" and int.from_bytes(content[18:20], "little") == 183
        (target/"libffi.so.6").write_bytes(content)
        copyright=next(m for m in archive.getmembers() if m.isfile() and m.name.endswith("/copyright"))
        (target/"libffi6-COPYRIGHT.txt").write_bytes(archive.extractfile(copyright).read())
receipt={"url":BASE+meta["Filename"], "package":meta["Package"], "version":meta["Version"],
    "package_sha256":meta["SHA256"], "library_sha256":hashlib.sha256(content).hexdigest(),
    "private_path":"compat/lib/libffi.so.6", "scope":"Only private CPython 3.8; no system install, no libffi8 alias"}
(target/"libffi6-origin.json").write_text(json.dumps(receipt,indent=2),encoding="utf-8")
print(json.dumps(receipt),flush=True)
