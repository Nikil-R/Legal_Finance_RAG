from pathlib import Path
base = Path("data/raw")
summary = {}
for f in sorted(base.rglob("*")):
    if f.is_file() and not f.name.startswith("."):
        parts = f.relative_to(base).parts
        key = parts[0] + ("/" + parts[1] if len(parts) > 2 else "")
        summary.setdefault(key, {"n": 0, "good": 0})
        summary[key]["n"] += 1
        if f.stat().st_size >= 300:
            summary[key]["good"] += 1
print("\nFINAL DATA/RAW AUDIT")
print("=" * 60)
for k, v in sorted(summary.items()):
    print(f"{k:45s} {v['n']:4d} files  ({v['good']:4d} substantive)")
print(f"\nTOTAL DOCUMENTS: {sum(v['n'] for v in summary.values())}")
