# Soutenance — Carnet d'ordres SNA

Dossier autonome : tout le nécessaire pour compiler la présentation.

## Compilation

Le document se compile avec **pdflatex** (deux passes pour les sections/numéros) :

```bash
pdflatex soutenance.tex
pdflatex soutenance.tex
```

Ou avec `latexmk` :

```bash
latexmk -pdf soutenance.tex
```

Le résultat est `soutenance.pdf` (22 slides, 16:9).

## Remarques

- **Moteur** : pdflatex est recommandé. Le style `beamerx.sty` ne charge les polices
  Muli / DroidSerif / RobotoMono que sous XeLaTeX/LuaLaTeX ; ces polices ne sont pas
  fournies ici, donc en xelatex il faudrait les installer. Sous pdflatex, le rendu
  utilise les polices par défaut (Computer Modern) sans aucune dépendance externe.
- **Paquets requis** (présents dans toute distribution TeX Live / MiKTeX complète) :
  beamer, amsmath, amssymb, booktabs, array, graphicx, geometry, xcolor, etc.
- **Logo** : `beamerxlogo.pdf` affiche actuellement « Université Paris-Saclay ».
  Pour afficher un autre logo, remplacez simplement ce fichier (même nom).

## Contenu du dossier

- `soutenance.tex` — le document principal
- `beamerx.sty` — le thème École Polytechnique
- `beamerxarmes.pdf`, `beamerxbackground.jpg`, `beamerxfiletcourt.pdf`,
  `beamerxlogo.pdf`, `beamerxx.pdf` — éléments graphiques du thème
- `*.png` — les 15 figures de la présentation (extraites du rapport)
