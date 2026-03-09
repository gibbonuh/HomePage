#!/usr/bin/env python3
import argparse
import json
import os
import re
import zipfile


COVER_PRIORITY = [
    "icon.png",
    "icon.jpg",
    "icon.jpeg",
    "icon.webp",
    "splash.png",
    "splash.jpg",
    "logo.png",
    "logo.jpg",
    "thumb.png",
    "thumb.jpg",
    "thumbnail.png",
    "cover.png",
    "cover.jpg",
    "background.png",
    "media.png",
]


def pretty_title(folder_name: str) -> str:
    words = folder_name.replace("-", " ").replace("_", " ").split()
    out = []
    for w in words:
        if w.isdigit():
            out.append(w)
        else:
            out.append(w.capitalize())
    return " ".join(out)


def pick_cover(folder_path: str, folder_name: str) -> str:
    if not os.path.isdir(folder_path):
        return f"https://placehold.co/600x600/1f2937/e5e7eb?text={folder_name}"

    files = set(os.listdir(folder_path))
    for c in COVER_PRIORITY:
        if c in files:
            return f"./games/{folder_name}/{c}"

    img_candidates = sorted(
        f for f in files if re.search(r"\.(png|jpe?g|webp|gif)$", f, re.IGNORECASE)
    )
    if img_candidates:
        return f"./games/{folder_name}/{img_candidates[0]}"
    return f"https://placehold.co/600x600/1f2937/e5e7eb?text={folder_name}"


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Extract the next lightweight game batch from HTML-Games zip and update extra-games.json."
    )
    parser.add_argument(
        "--root",
        default="/Users/emmett/Documents/New project 3",
        help="Project root path.",
    )
    parser.add_argument(
        "--zip",
        dest="zip_path",
        default="/Users/emmett/Downloads/HTML-Games-V2-main.zip",
        help="Path to HTML-Games-V2 zip file.",
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=10,
        help="How many games to add in this run.",
    )
    parser.add_argument(
        "--max-game-mb",
        type=float,
        default=45.0,
        help="Only include games whose uncompressed folder size is <= this MB.",
    )
    parser.add_argument(
        "--label",
        default="next",
        help="Batch label only for printed output (e.g., 7, 8, 9).",
    )
    args = parser.parse_args()

    root = args.root
    zip_path = args.zip_path
    games_root = os.path.join(root, "games")
    catalog_path = os.path.join(root, "extra-games.json")

    if not os.path.isfile(zip_path):
        raise SystemExit(f"Zip not found: {zip_path}")
    if not os.path.isfile(catalog_path):
        raise SystemExit(f"Catalog not found: {catalog_path}")

    os.makedirs(games_root, exist_ok=True)

    with open(catalog_path, "r", encoding="utf-8") as f:
        catalog = json.load(f)

    existing_dirs = set()
    for entry in catalog:
        file_ref = entry.get("file", "")
        if file_ref.startswith("./games/") and file_ref.endswith("/index.html"):
            parts = file_ref.split("/")
            if len(parts) >= 4:
                existing_dirs.add(parts[2])

    with zipfile.ZipFile(zip_path) as zf:
        infos = zf.infolist()
        sizes = {}
        has_index = set()
        for info in infos:
            name = info.filename
            if not name.startswith("HTML-Games-V2-main/"):
                continue
            parts = name.split("/")
            if len(parts) < 3:
                continue
            game_dir = parts[1]
            sizes[game_dir] = sizes.get(game_dir, 0) + info.file_size
            if name.endswith("/index.html"):
                has_index.add(game_dir)

        candidates = []
        for game_dir in sorted(has_index):
            if game_dir in existing_dirs:
                continue
            size_mb = sizes.get(game_dir, 0) / (1024 * 1024)
            if size_mb <= args.max_game_mb:
                candidates.append((game_dir, size_mb))

        selected = [g for g, _ in candidates[: args.batch_size]]
        if not selected:
            print("No eligible games left with current filters.")
            return 0

        all_names = zf.namelist()
        added = []
        for game_dir in selected:
            prefix = f"HTML-Games-V2-main/{game_dir}/"
            for name in all_names:
                if not name.startswith(prefix) or name.endswith("/"):
                    continue
                rel = name[len(prefix) :]
                out_path = os.path.join(games_root, game_dir, rel)
                os.makedirs(os.path.dirname(out_path), exist_ok=True)
                with zf.open(name) as src, open(out_path, "wb") as dst:
                    dst.write(src.read())

            cover_ref = pick_cover(os.path.join(games_root, game_dir), game_dir)
            title = pretty_title(game_dir)
            catalog.append(
                {
                    "id": "extra-" + re.sub(r"[^a-z0-9]+", "-", game_dir.lower()).strip("-"),
                    "title": title,
                    "file": f"./games/{game_dir}/index.html",
                    "cover": cover_ref,
                    "desc": f"Play {title}.",
                }
            )
            added.append((game_dir, sizes.get(game_dir, 0) / (1024 * 1024)))

    with open(catalog_path, "w", encoding="utf-8") as f:
        json.dump(catalog, f, ensure_ascii=True, indent=2)

    added_dirs = [g for g, _ in added]
    added_size_mb = sum(mb for _, mb in added)
    print(f"Batch {args.label}: added {len(added_dirs)} game(s).")
    print("Games:", ", ".join(added_dirs))
    print(f"Approx uncompressed size added: {added_size_mb:.2f} MB")
    print("")
    print("Next commands:")
    print(
        f'git -C "{root}" add extra-games.json ' + " ".join(f"games/{d}" for d in added_dirs)
    )
    print(
        f'git -C "{root}" commit -m "Add batch {args.label} games"'
    )
    print(f'git -C "{root}" push origin main')
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
