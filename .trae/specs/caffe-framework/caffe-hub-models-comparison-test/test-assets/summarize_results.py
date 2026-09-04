"""Summarize a net-results JSON: per-model status + key fields."""
import json
import sys


def _get(r, key, default=None):
    d = r.get("detail", {})
    return d.get(key, default)


def main():
    path = sys.argv[1]
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    impl = data.get("impl", "?")
    print(f"## {impl} — {len(data['results'])} models")
    for r in data["results"]:
        name = r["name"]
        status = r["status"]
        if status != "ok":
            err = (r.get("detail", {}).get("error") or "").split("\n")[0][:90]
            print(f"  {status:9s} {name:<28} {err}")
            continue
        d = r.get("detail", {})
        outs = d.get("outputs", {})
        out_desc = "; ".join(
            f"{on}{ods.get('shape')} nan={ods.get('has_nan')} inf={ods.get('has_inf')}"
            for on, ods in outs.items()
        )
        w = d.get("first_conv_weight")
        w_desc = f"w_std={w.get('std'):.4f}" if w else "no_weights"
        print(f"  {'ok':9s} {name:<28} layers={d.get('num_layers')} {w_desc} | {out_desc}")


if __name__ == "__main__":
    main()