"""Extrait toutes les figures du notebook (sorties base64) vers PNG,
plus les sorties stream (print) pour disposer des valeurs numeriques
reproductibles avec la graine du notebook."""
import base64
import json
import os

NB = "/home/anass_ettahiri/Carnet_d_ordre_SNA/Carnet-d-ordres-SNA/carnet_d_ordres.ipynb"
OUT = "/home/anass_ettahiri/Carnet_d_ordre_SNA/Carnet-d-ordres-SNA/report/figures"
os.makedirs(OUT, exist_ok=True)

with open(NB) as f:
    nb = json.load(f)

# Cibles : (cell_idx, output_idx, output_name)
# Indices verifies sur le notebook execute (49 cellules)
TARGETS = [
    (5,  0, "trajectories_subplots.png"),     # subplot q_a, q_b
    (5,  1, "trajectories_combined.png"),     # combined
    (11, 0, "trajectory_plane.png"),          # (Bid, Ask) plane
    (14, 0, "gaussian_approx.png"),           # gaussian approx
    (17, 0, "ig_distribution.png"),           # IG vs Poisson histogram
    (17, 1, "ig_brownian.png"),               # IG vs Brownian histogram
    (22, 0, "proba_3d_poisson.png"),          # 3D probability surface
    (26, 0, "time_proba_3d_poisson.png"),     # 3D combined
    (24, 0, "ruin_validation.png"),           # MC vs theoretical surface
    (31, 0, "hawkes_trajectory.png"),         # q(t) Hawkes
    (31, 1, "hawkes_stopping_dist.png"),      # distribution Hawkes stopping
    (32, 0, "hawkes_lambda.png"),             # lambda^-(t)
    (32, 1, "hawkes_lambda_T.png"),           # distribution lambda^-(T)
    (37, 0, "coupled_hawkes_traj.png"),       # coupled Hawkes trajs
    (37, 1, "coupled_hawkes_stopping.png"),   # coupled Hawkes stopping dist
    (39, 0, "hawkes_coupled_3d.png"),         # 3D Hawkes coupled
    (42, 0, "comparison.png"),                # comparison 4 models
    (45, 0, "q2_asymmetric.png"),             # q_2 conditional asym Hawkes
    (48, 0, "q2_symmetric_poisson.png"),      # q_2 conditional sym Hawkes Poisson
    (48, 1, "q2_symmetric_excited.png"),      # q_2 conditional sym Hawkes excited
]

n_ok = 0
for cell_idx, out_idx, name in TARGETS:
    if cell_idx >= len(nb["cells"]):
        print(f"SKIP {name}: cell {cell_idx} hors limites")
        continue
    cell = nb["cells"][cell_idx]
    outs = cell.get("outputs", [])
    images = []
    for o in outs:
        data = o.get("data", {})
        if "image/png" in data:
            images.append(data["image/png"])
    if out_idx >= len(images):
        print(f"SKIP {name}: cell {cell_idx} a {len(images)} images, demande #{out_idx}")
        continue
    raw = images[out_idx]
    if isinstance(raw, list):
        raw = "".join(raw)
    with open(os.path.join(OUT, name), "wb") as f:
        f.write(base64.b64decode(raw))
    print(f"OK   {name}  (cell {cell_idx} image #{out_idx})")
    n_ok += 1

print(f"\n=> {n_ok} figures extraites\n")

# Maintenant, sorties texte (print) pour chaque cellule de code
print("=== Sorties texte (print) ===")
for i, cell in enumerate(nb["cells"]):
    if cell.get("cell_type") != "code":
        continue
    for o in cell.get("outputs", []):
        if o.get("output_type") == "stream":
            txt = "".join(o.get("text", [])).rstrip()
            if txt:
                print(f"--- cell {i} (stream) ---")
                print(txt)
                print()
