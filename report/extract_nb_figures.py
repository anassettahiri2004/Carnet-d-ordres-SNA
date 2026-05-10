"""Extrait certaines images des cellules du notebook (sorties base64) vers PNG."""
import base64
import json
import os

NB = "/home/anass_ettahiri/Carnet_d_ordre_SNA/Carnet-d-ordres-SNA/carnet_d_ordres.ipynb"
OUT = "/home/anass_ettahiri/Carnet_d_ordre_SNA/Carnet-d-ordres-SNA/report/figures"
os.makedirs(OUT, exist_ok=True)

with open(NB) as f:
    nb = json.load(f)

# Cibles : (cell_idx, output_idx, output_name)
TARGETS = [
    (11, 0, "trajectory_plane.png"),     # cellule 11 : trajectory_grid (BId, Ask)
    (31, 0, "hawkes_trajectory.png"),    # cellule 31 : trajectoire q (Hawkes)
    (31, 1, "hawkes_stopping_time.png"), # cellule 31 : distribution temps d'arret Hawkes
    (32, 0, "hawkes_lambda.png"),        # cellule 32 : lambda^-(t)
    (32, 1, "hawkes_lambda_T.png"),      # cellule 32 : distribution lambda^-(T)
    (37, 0, "coupled_hawkes_traj.png"),  # cellule 37 : trajectoires Hawkes couples
    (37, 1, "coupled_hawkes_dist.png"),  # cellule 37 : distribution temps d'arret coupled
    (45, 0, "q2_poisson_cond.png"),      # cellule 45 : q_2 conditionnel (asymetrique)
    (48, 0, "q2_excited_a.png"),         # cellule 48 : q_2 Poisson constant (symmetrique)
    (48, 1, "q2_excited_b.png"),         # cellule 48 : q_2 excite par decrements ask
]

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
