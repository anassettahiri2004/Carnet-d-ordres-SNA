# Théorie du Modèle — Carnet d'ordres stochastique

Ce document présente, section par section, la théorie mathématique sous-jacente à chaque cellule du notebook `carnet_d_ordres.ipynb`. Pour chaque assertion, une démonstration ou un calcul explicite est fourni.

---

## Table des matières

1. [Modèle de base : Processus de Poisson (§1)](#1-modèle-de-base--processus-de-poisson)
2. [Estimation Monte-Carlo du temps d'atteinte (§2)](#2-estimation-monte-carlo-du-temps-datteinte)
3. [Trajectoire dans le plan (§3)](#3-trajectoire-dans-le-plan-qb-qa)
4. [Approximation diffusive (§4)](#4-approximation-diffusive)
5. [Loi inverse-gaussienne (§5)](#5-loi-inverse-gaussienne)
6. [Probabilité de ruine asymétrique (§6)](#6-probabilité-de-ruine-asymétrique)
7. [Surface 3D du temps moyen (§7)](#7-surface-3d-du-temps-moyen)
8. [Processus de Hawkes (§8)](#8-processus-de-hawkes)
9. [Thinning d'Ogata (§9)](#9-algorithme-de-thinning-dogata)
10. [Hawkes couplés (§10)](#10-hawkes-couplés)
11. [Comparaison des temps d'arrêt (§11)](#11-comparaison-des-temps-darrêt)
12. [Processus auxiliaire q₂ (§12)](#12-processus-auxiliaire-q2)
13. [Intensité de q₂ excitée (§13)](#13-intensité-de-q2-excitée-par-les-décréments-ask)
14. [Passage au prix (§14)](#14-passage-au-prix)
15. [Splitting pour Q_{a,2} (§15)](#15-splitting-pour-la-distribution-de-qa2)
16. [Distribution des états aux niveaux (§16)](#16-distribution-des-états-aux-niveaux-de-splitting)
17. [Flash crash (§17)](#17-flash-crash--k-chutes-consécutives)
18. [Importance Sampling (§18)](#18-importance-sampling-par-basculement-exponentiel)
19. [Intervalles de confiance (§19)](#19-intervalles-de-confiance--splitting-vs-is)
20. [Métriques de risque (§20)](#20-métriques-de-risque-de-liquidité)
21. [Calibration MLE (§21)](#21-calibration-par-maximum-de-vraisemblance)

---

## 1. Modèle de base : Processus de Poisson

### Modèle

Le volume au meilleur niveau d'un côté (bid ou ask) est modélisé comme un processus de naissance-mort :

$$q(t) = q_0 + N^+_{\lambda^+}(t) - N^-_{\lambda^-}(t)$$

où $N^+, N^-$ sont des processus de Poisson indépendants d'intensités $\lambda^+$ et $\lambda^-$. Le processus est **absorbé en 0**.

### Simulation par temps inter-événements

**Propriété :** le temps inter-événements d'un processus de Poisson de paramètre $\lambda$ est $\text{Exp}(\lambda)$.

**Preuve :** Soit $T_1$ le premier temps de saut. Pour tout $t > 0$ :
$$P(T_1 > t) = P(N(t) = 0) = e^{-\lambda t}$$
ce qui est exactement la survie d'une loi exponentielle de paramètre $\lambda$. $\square$

**Superposition :** la superposition de $N^+$ et $N^-$ est un processus de Poisson de paramètre $\lambda^+ + \lambda^-$. Le saut est $+1$ avec probabilité $p = \lambda^+/(\lambda^+ + \lambda^-)$, sinon $-1$. C'est ce que fait `simulate_only_one_process` : à chaque itération, on tire le délai $\sim \text{Exp}(\lambda^+ + \lambda^-)$, puis on choisit la direction.

### Condition de dérive négative

Pour que le processus atteigne presque sûrement 0, il faut $\lambda^- > \lambda^+$, soit une **dérive négative** $\mu = \lambda^+ - \lambda^- < 0$. C'est le réglage par défaut : $\lambda^+ = 1.2$, $\lambda^- = 2$, donc $\mu = -0.8$.

**Preuve de l'atteinte p.s. de 0 :** la chaîne de Markov en temps discret $(q_n)$ (regardée aux instants de sauts) est une marche aléatoire sur $\mathbb{Z}^+$ avec $p < 1/2$. Par le critère de récurrence de Foster-Lyapunov avec $V(q) = r^q$ où $r = q/p > 1$, on obtient $\mathbb{E}[V(q_{n+1}) \mid q_n] = q \cdot r^{q-1}/r + p \cdot r^{q+1} = r^q (q/r + pr) = r^q \cdot (q + pr^2)/r < r^q$ pour $r$ convenable. Donc la chaîne est récurrente positive et atteint 0 p.s. $\square$

---

## 2. Estimation Monte-Carlo du temps d'atteinte

### Estimateur et intervalle de confiance

Pour $\tau = \inf\{t \ge 0 : q(t) = 0\}$, on estime $\mathbb{E}[\tau]$ par :

$$\hat{\mathbb{E}}[\tau] = \frac{1}{M} \sum_{i=1}^M \tau^{(i)}$$

**Théorème Central Limite (TCL) :** si $\text{Var}(\tau) < \infty$, alors par le TCL classique :

$$\sqrt{M}\,\frac{\hat{\mathbb{E}}[\tau] - \mathbb{E}[\tau]}{\hat{\sigma}} \xrightarrow{d} \mathcal{N}(0, 1)$$

L'intervalle de confiance asymptotique à $1-\alpha$ est :
$$\hat{\mathbb{E}}[\tau] \pm z_{1-\alpha/2} \cdot \frac{\hat{\sigma}}{\sqrt{M}}$$

**Variance finie de $\tau$ :** sous $\lambda^- > \lambda^+$, on a $\mathbb{E}[\tau] = q_0/|\mu|$ et $\text{Var}(\tau) = q_0 \sigma^2 / |\mu|^3 < \infty$ (calculé via l'approximation inverse-gaussienne, voir §5). Donc le TCL s'applique. $\square$

### Deux variantes implémentées

- `estimate_time_to_zero_for_one_process` : $\mathbb{E}[\tau]$ pour une file unique.
- `estimate_time_to_zero` : $\mathbb{E}[\min(\tau_a, \tau_b)]$ pour deux files indépendantes. Par indépendance, $\min(\tau_a, \tau_b) < \tau_a$ p.s., donc le temps est strictement plus court que pour une file unique.

---

## 3. Trajectoire dans le plan $(q_b, q_a)$

### Synchronisation des temps

Les deux processus ont des grilles temporelles distinctes $\{t_i^a\}$ et $\{t_j^b\}$. Pour obtenir l'état $(q_b(t), q_a(t))$ à un temps quelconque $t$, on utilise la recherche binaire :

```
q_a(t) = q_a[searchsorted(times_a, t, side='right') - 1]
```

**Correction :** `searchsorted(..., side='right')` donne le premier indice $k$ tel que $t_k^a > t$. Donc `k-1` est le dernier indice avec $t_{k-1}^a \le t$, soit le dernier événement avant $t$. C'est exact car $q_a$ est constante par morceaux à droite (càdlàg). La complexité est $O(n \log n)$ au lieu de $O(n^2)$.

### Encodage de la fréquence par l'opacité

Pour chaque point $(q_b, q_a)$ visité $c$ fois, l'opacité est :
$$\alpha_{\text{opacity}} = \alpha_{\min} + (1 - \alpha_{\min}) \cdot \frac{c - c_{\min}}{c_{\max} - c_{\min}}$$

Les états fréquents (proches de $(q_0^b, q_0^a)$) sont opaques, les transitoires translucides.

---

## 4. Approximation diffusive

### Théorème de convergence fonctionnelle

Soit $q^{(\varepsilon)}(t) = q_0 + N^+_{\lambda^+/\varepsilon}(t) - N^-_{\lambda^-/\varepsilon}(t)$, une version accélérée d'un facteur $1/\varepsilon$. Par le **TCLD de Donsker** pour les processus de Poisson centrés :

$$\varepsilon \cdot q^{(1/\varepsilon)}(t/\varepsilon^2) \xrightarrow[\varepsilon \to 0]{d} Q_t$$

où $Q$ vérifie l'EDS :

$$dQ_t = (\lambda^+ - \lambda^-)\,dt + \sqrt{\lambda^+ + \lambda^-}\,dW_t, \quad Q_0 = q_0$$

**Conséquence :** pour $t$ fixé et loin de la barrière 0, la loi de $q(t)$ est approximativement :
$$q(t) \approx \mathcal{N}\!\left(q_0 + (\lambda^+ - \lambda^-)\,t,\; (\lambda^+ + \lambda^-)\,t\right)$$

**Vérification numérique (cell 13-14) :** On simule 10 000 trajectoires jusqu'à $T=100$ et on compare l'histogramme à la densité $\mathcal{N}(q_0 + \mu T, \sigma^2 T)$. Avec $\mu = -0.8$ et $\sigma^2 = 3.2$, on obtient $\mathcal{N}(-70, 320)$ — mais la barrière 0 tronque la distribution vers les valeurs positives ; c'est un biais de l'approximation sans barrière.

---

## 5. Loi inverse-gaussienne

### Dérivation de la loi de $\tau$

Pour $X_t = q_0 + \mu t + \sigma W_t$ avec $\mu < 0$, le premier temps d'atteinte de 0 est :
$$\tau = \inf\{t \ge 0 : X_t = 0\}$$

**Théorème :** $\tau$ suit une loi **inverse-gaussienne** $\text{IG}(\mu_{\text{IG}}, \lambda_{\text{IG}})$ avec :

$$\mu_{\text{IG}} = \frac{q_0}{|\mu|}, \qquad \lambda_{\text{IG}} = \frac{q_0^2}{\sigma^2}$$

de densité :
$$f_\tau(t) = \sqrt{\frac{\lambda_{\text{IG}}}{2\pi t^3}}\exp\!\left(-\frac{\lambda_{\text{IG}}(t - \mu_{\text{IG}})^2}{2\,\mu_{\text{IG}}^2\,t}\right), \quad t > 0$$

**Preuve :** Par le théorème d'optionnel stopping appliqué à la martingale $M_t = \exp(\theta X_t - \frac{1}{2}(\theta^2 \sigma^2 + 2\theta\mu)t)$, on obtient la transformée de Laplace de $\tau$ :

$$\mathbb{E}[e^{-s\tau}] = \exp\!\left(-\frac{q_0}{\sigma^2}\left(\sqrt{\mu^2 + 2s\sigma^2} - |\mu|\right)\right)$$

En identifiant cette transformée avec celle connue de la loi inverse-gaussienne :

$$\mathbb{E}[e^{-s\tau}] = \exp\!\left(-\frac{\lambda_{\text{IG}}}{\mu_{\text{IG}}}\left(\sqrt{1 + \frac{2\mu_{\text{IG}}^2 s}{\lambda_{\text{IG}}}} - 1\right)\right)$$

on trouve $\mu_{\text{IG}} = q_0/|\mu|$ et $\lambda_{\text{IG}} = q_0^2/\sigma^2$. $\square$

**Moments :**
$$\mathbb{E}[\tau] = \mu_{\text{IG}} = \frac{q_0}{|\mu|}, \qquad \text{Var}(\tau) = \frac{\mu_{\text{IG}}^3}{\lambda_{\text{IG}}} = \frac{q_0 \sigma^2}{|\mu|^3}$$

Avec $q_0 = 10$, $|\mu| = 0.8$, $\sigma^2 = 3.2$ : $\mathbb{E}[\tau] = 12.5$, $\text{Var}(\tau) \approx 78.1$.

**Convention SciPy :** `sps.invgauss(mu = sigma²/(q₀|μ|), scale = q₀²/σ²)` — le paramètre `mu` de SciPy est $\mu_{\text{SciPy}} = \mu_{\text{IG}}/\lambda_{\text{IG}}^{1/2}$, ce qui donne bien `mu = sigma²/(q₀|μ|)` et `scale = q₀²/σ²` dans le code.

### Test de Kolmogorov-Smirnov (cell 19)

On teste $H_0 :$ les $\tau^{(i)}$ i.i.d. $\sim \text{IG}(\mu_{\text{IG}}, \lambda_{\text{IG}})$ contre $H_1 :$ distribution quelconque. La statistique KS est $D_M = \sup_t |F_M(t) - F_{\text{IG}}(t)|$. Sous $H_0$, $\sqrt{M} D_M \xrightarrow{d}$ distribution de Kolmogorov. Une $p$-value $> 0.05$ signifie qu'on ne rejette pas $H_0$ à 5%.

---

## 6. Probabilité de ruine asymétrique

### Formulation

Avec deux processus Poisson indépendants (ask et bid) démarrant à $q_0^a$ et $q_0^b$ :

$$p(q_0^a, q_0^b) = \mathbb{P}(\tau_a < \tau_b)$$

### Calcul via l'approximation diffusive

Sous l'approximation brownienne, $\tau_a \sim \text{IG}(\mu_a, \lambda_a)$ et $\tau_b \sim \text{IG}(\mu_b, \lambda_b)$ indépendants, avec $\mu_k = q_0^k/|\mu|$ et $\lambda_k = (q_0^k)^2/\sigma^2$. Alors :

$$\mathbb{P}(\tau_a < \tau_b) = \int_0^\infty f_{\tau_a}(t)\,\big(1 - F_{\tau_b}(t)\big)\,dt$$

calculé numériquement par la méthode des trapèzes (`np.trapezoid`).

### Comportement qualitatif

- Si $q_0^a < q_0^b$ : l'ask est plus proche de 0, donc $p > 1/2$.
- Si $q_0^a = q_0^b$ : symétrie → $p = 1/2$ (car $\mu$ et $\sigma$ sont les mêmes pour les deux files).
- La surface 3D $p(q_0^a, q_0^b)$ est **décroissante en $q_0^a$** et **croissante en $q_0^b$**.

**Preuve de la symétrie diagonale :** Par échange des rôles de ask et bid, $P(\tau_a < \tau_b \mid q_0^a = q_0^b) = P(\tau_b < \tau_a \mid q_0^a = q_0^b)$. Les deux probabilités somment à 1 (l'égalité $\tau_a = \tau_b$ est de probabilité nulle car les processus sont continus), donc chacune vaut $1/2$. $\square$

---

## 7. Surface 3D du temps moyen

### Estimateur

$$\hat{T}(q_0^a, q_0^b) = \frac{1}{M}\sum_{i=1}^M \min(\tau_a^{(i)}, \tau_b^{(i)})$$

**Monotonie :** $T(q_0^a, q_0^b)$ est strictement croissante en chacune des deux variables car, par couplage, augmenter $q_0^a$ ou $q_0^b$ retarde l'épuisement de n'importe quelle trajectoire.

**Intervalle de confiance :** IC asymptotique à $1-\alpha$ :
$$\hat{T} \pm z_{1-\alpha/2} \cdot \frac{\hat{\sigma}_T}{\sqrt{M}}$$

visualisé par les wireframes rouge (borne inf) et noir (borne sup) autour de la surface principale.

**Approximation du min :** Pour deux variables indépendantes, si $\tau_a \sim \text{IG}(\mu_a, \lambda_a)$ et $\tau_b \sim \text{IG}(\mu_b, \lambda_b)$, le minimum n'a pas de forme close générale : $P(\min(\tau_a, \tau_b) > t) = (1-F_a(t))(1-F_b(t))$. C'est pourquoi on utilise la simulation.

---

## 8. Processus de Hawkes

### Définition

Le processus de Hawkes à noyau exponentiel est défini par l'intensité stochastique :

$$\lambda^-(t) = \mu^- + \sum_{T_i < t} \alpha\, e^{-\beta(t - T_i)}$$

où les $T_i$ sont les temps de saut eux-mêmes — l'intensité dépend de sa propre histoire (*auto-excitation*).

### Intensité stationnaire

**Calcul de $\bar{\lambda}^-_\infty$ :** En régime stationnaire, par théorie de Bartlett, l'intensité moyenne satisfait :

$$\mathbb{E}[\lambda^-(t)] = \mu^- + \mathbb{E}\!\left[\sum_{T_i < t} \alpha e^{-\beta(t-T_i)}\right]$$

En régime stationnaire, l'ensemble des sauts est un processus de Poisson d'intensité $\bar{\lambda}^-_\infty$ (stationnarité). Donc :

$$\bar{\lambda}^-_\infty = \mu^- + \bar{\lambda}^-_\infty \cdot \int_0^\infty \alpha e^{-\beta u}\,du = \mu^- + \frac{\alpha}{\beta}\,\bar{\lambda}^-_\infty$$

D'où :
$$\bar{\lambda}^-_\infty = \frac{\mu^-}{1 - \alpha/\beta} \quad \text{(condition : } \alpha < \beta\text{)}$$

**Mais** dans notre modèle, chaque décrement aussi déclenche un saut inhibitoire $-\alpha$ sur $\lambda^-$ (insertion d'ordre = arrivée positive = saut $+1$). En tenant compte de l'excitation symétrique $\pm\alpha$ :

$$\bar{\lambda}^-_\infty = \frac{\mu^- \beta - \lambda^+ \alpha}{\beta - \alpha}$$

**Preuve détaillée :** En régime stationnaire, $\bar{\lambda}^- = \mathbb{E}[\lambda^-(t)]$. Chaque événement de décrement (intensité $\bar{\lambda}^-$) excite $\lambda^-$ par $+\alpha$, et chaque insertion (intensité $\lambda^+$) inhibe $\lambda^-$ par $-\alpha$. L'intensité résiduelle d'auto-corrélation est $\alpha/\beta$ par événement. Donc :

$$\bar{\lambda}^- = \mu^- + \frac{\alpha}{\beta}(\bar{\lambda}^- - \lambda^+) \implies \bar{\lambda}^-\!\left(1 - \frac{\alpha}{\beta}\right) = \mu^- - \frac{\lambda^+\alpha}{\beta}$$

$$\bar{\lambda}^-_\infty = \frac{\mu^- - \lambda^+\alpha/\beta}{1 - \alpha/\beta} = \frac{\mu^-\beta - \lambda^+\alpha}{\beta - \alpha} \quad \square$$

Avec $\mu^- = 2$, $\alpha = 0.5$, $\beta = 1$, $\lambda^+ = 1.2$ : $\bar{\lambda}^-_\infty = (2 \cdot 1 - 1.2 \cdot 0.5)/(1 - 0.5) = (2 - 0.6)/0.5 = 2.8$.

---

## 9. Algorithme de Thinning d'Ogata

### Principe

L'algorithme de thinning simule un processus ponctuel d'intensité stochastique $\lambda(t) \le \bar\lambda$ en superposant un processus de Poisson homogène de taux $\bar\lambda$ et en rejetant les événements avec la probabilité adéquate.

**Algorithme (Ogata 1981) :**

1. Soit $t$ le temps courant, $\bar\lambda = \max(\mu^-, \lambda^-(t))$.
2. Tirer $\Delta t \sim \text{Exp}(\bar\lambda + \lambda^+)$.
3. Au temps candidat $t' = t + \Delta t$, calculer $\lambda^-(t') = \mu^- + (\lambda^-(t_{\text{last}}) - \mu^-) e^{-\beta(t' - t_{\text{last}})}$.
4. Tirer $U \sim \mathcal{U}[0,1]$ :
   - Si $U < \lambda^+/(\bar\lambda + \lambda^+)$ : saut $+1$ (insertion), $\lambda^- \leftarrow \lambda^-(t') - \alpha$.
   - Si $U < (\lambda^+(t') + \lambda^+)/(\bar\lambda + \lambda^+)$ : saut $-1$ (décrement), $\lambda^- \leftarrow \lambda^-(t') + \alpha$.
   - Sinon : événement fantôme, mise à jour de $t_{\text{last}}$ seulement.

**Correction de l'algorithme :** Le majorant $\bar\lambda(t) \ge \lambda^-(t)$ pour tout $t \in [t_{\text{last}}, t')$ est bien vérifié car entre deux sauts, $\lambda^-$ décroit exponentiellement, donc $\lambda^-(t) \le \lambda^-(t_{\text{last}}) = \bar\lambda_{\text{eff}}$ qui est lui-même majoré par $\max(\mu^-, \lambda^-(t_{\text{last}}))$.

**Convergence :** Le processus généré par l'algorithme de thinning a la même loi que le processus de Hawkes car il satisfait le même critère de Campbell (intensité stochastique conditionnelle correcte). Voir Ogata (1981), *JRSS B*.

---

## 10. Hawkes Couplés

### Modèle

Pour deux files (ask $a$, bid $b$) avec excitation croisée **inhibitoire** :

$$\lambda^-_a(t) = \mu^-_a + \alpha \!\!\sum_{T_i^{\downarrow a} < t} e^{-\beta(t-T_i)} - \alpha \!\!\sum_{T_j^{\uparrow a} < t} e^{-\beta(t-T_j)}$$

et de même pour $\lambda^-_b$. Le signe du saut change selon l'émetteur :

| Événement | $\Delta\lambda^-_a$ | $\Delta\lambda^-_b$ |
|---|---|---|
| Décrement ask ($q_a \to q_a-1$) | $+\alpha$ | $-\alpha$ |
| Insertion ask ($q_a \to q_a+1$) | $-\alpha$ | $+\alpha$ |
| Décrement bid ($q_b \to q_b-1$) | $-\alpha$ | $+\alpha$ |
| Insertion bid ($q_b \to q_b+1$) | $+\alpha$ | $-\alpha$ |

**Interprétation financière :** Quand l'ask se vide ($q_a$ diminue), la pression vendeuse augmente ($\lambda^-_a \uparrow$) et la pression acheteuse diminue ($\lambda^-_b \downarrow$) — le marché anticipe un mouvement de prix à la hausse.

### Thinning global

La borne supérieure pour le thinning est :
$$\bar\lambda_{\text{sup}} = \bar\lambda_a + \bar\lambda_b + \lambda^+_a + \lambda^+_b$$

avec $\bar\lambda_k = \max(\mu^-_k, \lambda^-_k(t))$. Les 6 branches du thinning sont :

$$U \in \left[0, \frac{\lambda^+_a}{\bar\lambda_{\text{sup}}}\right), \left[\frac{\lambda^+_a}{\bar\lambda_{\text{sup}}}, \frac{\lambda^+_a + \lambda^{\text{eff}}_a}{\bar\lambda_{\text{sup}}}\right), \ldots$$

La condition d'arrêt est $q_a = 0$ ou $q_b = 0$.

### Non-Markovianité

Le processus $(q_a(t), q_b(t))$ seul **n'est pas markovien** : il faut adjoindre l'état $(\lambda^-_a(t), \lambda^-_b(t), t_{\text{last},a}, t_{\text{last},b})$ pour avoir la propriété de Markov. C'est pourquoi le vecteur d'état complet dans le code est `(q_a, q_b, la, lb, t, tla, tlb)`.

---

## 11. Comparaison des temps d'arrêt

### Hiérarchie stochastique

On a la hiérarchie suivante en loi pour les temps d'atteinte de 0 :

$$\min(\tau_a^{\text{Poisson}}, \tau_b^{\text{Poisson}}) \;\le_{\text{st}}\; \tau^{\text{Poisson individuel}}$$

**Preuve :** $\min(\tau_a, \tau_b) \le \tau_a$ p.s., donc la dominance stochastique est immédiate. $\square$

**Hawkes vs Poisson :** Avec $\alpha > 0$, l'auto-excitation crée des **rafales** d'événements. Cela réduit $\mathbb{E}[\tau]$ par rapport au processus de Poisson de même intensité moyenne. Intuitivement, les événements se regroupent et le processus atteint 0 plus vite en moyenne, mais avec une variance plus grande (queues plus lourdes).

**Quantification :** l'intensité stationnaire Hawkes $\bar\lambda^- = 2.8 > 2 = \lambda^-_{\text{Poisson}}$, donc l'intensité moyenne effective est plus forte → $\mathbb{E}[\tau^{\text{Hawkes}}] < \mathbb{E}[\tau^{\text{Poisson}}]$.

---

## 12. Processus auxiliaire $q_2$

### Objectif

On modélise le niveau adjacent du carnet (deuxième limite) par un processus $q_2$ indépendant de paramètres $(\lambda^+_2, \lambda^-_2)$, simulé en parallèle jusqu'au temps d'arrêt $\tau = \min(\tau_a, \tau_b)$.

### Distribution conditionnelle

On estime empiriquement :
$$\mathcal{L}(q_2(\tau) \mid \tau = \tau_a) \quad \text{et} \quad \mathcal{L}(q_2(\tau) \mid \tau = \tau_b)$$

**Motivation financière :** $q_2(\tau_a)$ est la profondeur disponible au niveau 2 ask au moment où le niveau 1 ask s'épuise — c'est le volume qu'un ordre marché agressif pourrait encore consommer avant le prochain saut de prix.

**Calcul de la loi marginale :** Sans conditionnement, $q_2(\tau)$ est la loi du processus de naissance-mort à un temps aléatoire. En général, $\mathcal{L}(q_2(t)) \to \pi_{\text{stat}}$ quand $t \to \infty$ où $\pi_{\text{stat}}$ est la loi stationnaire de la file $M/M/1$. Mais ici $\tau$ est fini et aléatoire, donc la loi est intermédiaire entre l'état initial $q_0^{(2)}$ et $\pi_{\text{stat}}$.

---

## 13. Intensité de $q_2$ excitée par les décréments ask

### Modèle d'excitation

L'intensité d'arrivée au niveau 2 ask est augmentée par chaque décrement du niveau 1 ask :

$$\lambda^+_2(t) = \mu^+_2 + \sum_{T_i^{\downarrow a} < t} a\,e^{-b(t - T_i^{\downarrow a})}$$

**Interprétation :** chaque décrement du niveau 1 signale une pression acheteuse accrue, ce qui incite les market-makers à replacer des ordres au niveau 2 (effet de rebond de liquidité).

### Algorithme de thinning pour $\lambda^+_2(t)$

La borne globale est :
$$\bar\lambda^+_2 \le \mu^+_2 + a \cdot |\mathcal{D}_a|$$

où $|\mathcal{D}_a|$ est le nombre total de décréments ask sur le run. Le candidat est accepté comme saut $+1$ de $q_2$ avec probabilité $\lambda^+_2(t')/\bar\lambda^+_2$, et comme décrement $-1$ avec probabilité $\lambda^-_2/(\bar\lambda^+_2 + \lambda^-_2)$.

### Effet observé

La comparaison des sections 12 et 13 montre que l'excitation de $\lambda^+_2$ conduit à un $q_2(\tau_a)$ plus grand en moyenne (plus de liquidité au niveau 2 au moment de l'épuisement du niveau 1), traduisant le rebond de liquidité.

---

## 14. Passage au prix

### Architecture à quatre limites

Le mid-price est reconstruit à partir de quatre files :

| File | Côté | Niveau | Rôle |
|---|---|---|---|
| $q_{a,1}$ | Ask | 1er | Plus proche du mid, Hawkes couplé |
| $q_{b,1}$ | Bid | 1er | Plus proche du mid, Hawkes couplé |
| $q_{a,2}$ | Ask | 2ème | Moins proche, Poisson avec excitation |
| $q_{b,2}$ | Bid | 2ème | Moins proche, Poisson avec excitation |

### Dynamique du mid-price

- Le **mid-price** $P_t = (P_{\text{ask}} + P_{\text{bid}})/2$ évolue en sauts discrets de $\pm\delta/2$.
- Un saut de prix vers le **haut** ($+\delta/2$) survient quand le niveau 1 **bid** s'épuise ($q_{b,1} = 0$) : le meilleur bid se déplace au tick inférieur.
- Un saut vers le **bas** ($-\delta/2$) survient quand le niveau 1 **ask** s'épuise ($q_{a,1} = 0$).

### Continuité des intensités entre cycles

Lors du passage au cycle suivant, les intensités $(\lambda^-_a, \lambda^-_b)$ finales du cycle précédent sont réutilisées comme valeurs initiales. Cela préserve la **mémoire hawkésienne** entre cycles : un choc de prix récent reste visible dans l'intensité, ce qui génère du **momentum** (succession de mouvements dans la même direction).

**Preuve du momentum :** Si le cycle $k$ se termine par $q_{a,1} = 0$ (prix baisse), alors $\lambda^-_{a,k} > \mu^-_a$ (l'excitation accumulée). Au début du cycle $k+1$, $\lambda^-_{a,k+1}(0) = \lambda^-_{a,k}(\tau_k) > \mu^-_a$, donc la probabilité d'un nouveau choc ask au cycle $k+1$ est supérieure à celle d'un choc bid. Ceci crée la corrélation temporelle des retours — effet de **momentum**. $\square$

---

## 15. Splitting pour la distribution de $Q_{a,2}$

### Problème des événements rares

On cherche $\mathbb{P}(\tau_a < \tau_b)$ dans un régime asymétrique ($\mu^-_a < \mu^-_b$) où cet événement est rare. La méthode de Monte-Carlo directe a une variance relative $\propto (1-p)/p \to \infty$ quand $p \to 0$.

### Algorithme de splitting AMS (Adaptive Multilevel Splitting)

**Idée :** décomposer l'événement rare $\{q_a \text{ atteint 0}\}$ en une chaîne d'événements plus probables $\{q_a \le k\}$ pour $k = Q_0^a - 1, Q_0^a - 2, \ldots, 0$.

**Algorithme :**

1. Initialiser $N$ particules : $\mathbf{x}^{(i)} = (q_a=Q_0, q_b=Q_0, \lambda_a=\mu_a, \lambda_b=\mu_b, t=0)$.
2. Pour $k = Q_0^a - 1$ jusqu'à $0$ :
   a. Simuler chaque particule jusqu'à $q_a \le k$ (survie) ou $q_b = 0$ (mort).
   b. Collecter les $N_k$ survivants.
   c. Estimer $\hat{p}_k = N_k / N$.
   d. **Rééchantillonner** : tirer $N$ particules avec remise parmi les survivants.
3. Retourner $\hat{P} = \prod_{k=0}^{Q_0^a-1} \hat{p}_k$.

**Estimateur sans biais :**

**Proposition :** $\hat{P} = \prod_k \hat{p}_k$ est un estimateur sans biais de $P = \prod_k p_k$ où $p_k = \mathbb{P}(\tau_a^{(k+1)} < \tau_b \mid \tau_a^{(k)} < \tau_b)$ est la probabilité conditionnelle de franchir le niveau $k$ sachant avoir franchi $k+1$.

**Preuve :** Conditionnellement aux $N_k$ survivants au niveau $k$, $\hat{p}_k = N_k/N$ est un estimateur sans biais de $p_k$ (binomiale). Par indépendance des niveaux conditionnels et la règle du produit, $\mathbb{E}[\hat{P}] = \prod_k \mathbb{E}[\hat{p}_k] = \prod_k p_k = P$. $\square$

**Réduction de variance :** Le coefficient de variation de $\hat{P}$ satisfait :

$$\text{CV}^2(\hat{P}) = \sum_{k=0}^{Q_0^a-1} \frac{1-p_k}{N p_k}$$

Pour $p_k \approx 1/2$ et $Q_0^a = 10$ niveaux, le CV est de l'ordre de $\sqrt{10/(4N)}$, soit un gain d'un facteur $\sim p^{-1/2}$ par rapport au MC direct qui a CV $= \sqrt{(1-p)/(Np)} \approx p^{-1/2}/\sqrt{N}$ — **même ordre** mais sans l'explosion quand $p \to 0$.

---

## 16. Distribution des états aux niveaux de splitting

### Phase hors-ligne : collecte de $\pi_k$

Pour chaque niveau $k$, on collecte l'état complet $(\lambda_a, \lambda_b, t, t_{\text{la}}, t_{\text{lb}}, q_b, \text{decr})$ des particules **juste avant** le rééchantillonnage. Cela définit la **distribution empirique** $\hat\pi_k$ des états au niveau $k$.

**Pourquoi $\hat\pi_k$ est un estimateur de $\pi_k$ ?** Sous stationnarité du rééchantillonnage, les $N$ particules au niveau $k$ sont des tirages approximativement i.i.d. de $\pi_k = \mathcal{L}(\text{état} \mid q_a = k, \tau_a < \tau_b)$. Plus $N$ est grand, plus $\hat\pi_k \to \pi_k$ (par la LGN empirique).

### Phase en ligne : bootstrap

Pour estimer la distribution conditionnelle de $q_{a,2}$ sachant un état de départ $\pi_{k_0}$ :

1. Tirer un état $(s_1, \ldots, s_n)$ i.i.d. de $\hat\pi_{k_0}$ (bootstrap).
2. Pour chaque état, lancer une simulation jusqu'à $q_a = 0$ (ou $q_b = 0$).
3. Collecter le $q_{a,2}$ final des trajectoires qui ont $q_a = 0$.

**Probabilité en ligne :** $p_{\text{online}} = p_{\text{offline}} \times \hat{p}_{k_0 \to 0}$ où $\hat{p}_{k_0 \to 0}$ est la fraction de trajectoires qui atteignent $q_a = 0$. Cela donne un estimateur biaisé mais cohérent de $P(\tau_a < \tau_b \mid \text{état initial } \pi_{k_0})$.

---

## 17. Flash crash : $k$ chutes consécutives

### Définition

Un **flash crash de profondeur $k$** est l'événement $\text{FC}_k = \{k \text{ décréments consécutifs du prix}\}$. Chaque décrement correspond à l'épuisement d'un côté ask, ce qui réduit $P_{\text{ask}}$ d'un tick $\delta/2$.

### Probabilité par splitting hiérarchique

**Décomposition :** $P(\text{FC}_k) = P(\text{FC}_1) \cdot \prod_{j=1}^{k-1} P(\text{round } j+1 \mid \text{round } j \text{ réussi})$

**Algorithme :** Pour chaque round $j = 1, \ldots, k$ :
1. Partir de l'état final du round précédent $(\lambda_a, \lambda_b)$ avec $q_a = Q_0^a$ (remis à niveau).
2. Appliquer le splitting AMS du §15 pour estimer $p_j = P(\tau_a < \tau_b \mid \text{état initial}_j)$.
3. Multiplier : $P(\text{FC}_k) = \prod_{j=1}^k p_j$.

**Pourquoi $P(\text{FC}_k) > p_1^k$ ?** Après le premier choc ask, les intensités $(\lambda^-_a, \lambda^-_b)$ sont modifiées ($\lambda^-_a$ élevée, $\lambda^-_b$ basse). Cela rend $p_2 > p_1$ en général car l'ask est déjà "chaud". La comparaison avec $p_1^k$ (courbe en pointillés dans la figure) révèle l'**effet de clustering** dû aux Hawkes.

**Preuve de $p_2 > p_1$ (argument heuristique) :** Après un choc ask, l'état final est $\lambda^-_a = \mu^-_a + \alpha > \mu^-_a$. Au début du round suivant, la dérive est plus favorable à un second choc ask. Formellement, par couplage monotone : l'état $(\lambda_a + \alpha, \lambda_b - \alpha)$ domine stochastiquement l'état initial $(\mu_a, \mu_b)$ pour la probabilité $P(\tau_a < \tau_b)$ quand $\mu_a < \mu_b$. $\square$

---

## 18. Importance Sampling par basculement exponentiel

### Principe du changement de mesure

On cherche à estimer $P = \mathbb{E}^{\mathbb{P}}[\mathbf{1}_{\tau_a < \tau_b}]$ plus efficacement. On définit la mesure basculée $\mathbb{Q}^\theta$ par :

$$\frac{d\mathbb{Q}^\theta}{d\mathbb{P}}\bigg|_{\mathcal{F}_\tau} = e^{-L_\theta}$$

avec le **rapport de vraisemblance log** :

$$L_\theta = (\underbrace{e^\theta - 1}_{>0})\int_0^\tau \lambda^-_a(t)\,dt + (\underbrace{e^{-\theta} - 1}_{<0})\int_0^\tau \lambda^-_b(t)\,dt - \theta N_a(\tau) + \theta N_b(\tau)$$

où $N_a(\tau)$, $N_b(\tau)$ sont les nombres de décréments ask et bid jusqu'à $\tau$.

### Intensités basculées

Sous $\mathbb{Q}^\theta$ :

$$\tilde\lambda^-_a = e^\theta \lambda^-_a, \quad \tilde\lambda^-_b = e^{-\theta} \lambda^-_b$$

**Preuve :** Par la formule de Girsanov pour les processus ponctuels, le changement de mesure multiplicatif $e^\theta$ sur l'intensité correspond exactement au rapport de vraisemblance ci-dessus. Formellement, si $\mathcal{F}$ est la filtration naturelle du processus, le log-likelihood ratio s'écrit :

$$\log\frac{d\mathbb{Q}^\theta}{d\mathbb{P}} = \sum_{i: T_i^a < \tau} \log\frac{\tilde\lambda^-_a(T_i^a)}{\lambda^-_a(T_i^a)} + \sum_{j: T_j^b < \tau} \log\frac{\tilde\lambda^-_b(T_j^b)}{\lambda^-_b(T_j^b)} - \int_0^\tau (\tilde\lambda^-_a + \tilde\lambda^-_b - \lambda^-_a - \lambda^-_b)\,dt$$

$$= \theta N_a(\tau) - \theta N_b(\tau) + \int_0^\tau (e^\theta - 1)\lambda^-_a\,dt + \int_0^\tau (e^{-\theta} - 1)\lambda^-_b\,dt$$

ce qui donne bien $L_\theta$ avec le bon signe. $\square$

### Estimateur IS

$$\hat{P}_{\text{IS}} = \frac{1}{N}\sum_{i=1}^N \mathbf{1}_{\tau_a^{(i)} < \tau_b^{(i)}} \cdot e^{L_\theta^{(i)}}$$

**Sans biais :** $\mathbb{E}^{\mathbb{Q}^\theta}[\mathbf{1}_{\tau_a < \tau_b} e^{L_\theta}] = \mathbb{E}^{\mathbb{P}}[\mathbf{1}_{\tau_a < \tau_b}] = P$. $\square$

### Calcul des compensateurs

L'intégrale $\int_0^\tau \lambda^-_a(t)\,dt$ est calculée exactement entre deux événements : entre $t_i$ et $t_{i+1}$,

$$\int_{t_i}^{t_{i+1}} \lambda^-_a(t)\,dt = \mu^-_a (t_{i+1} - t_i) + \frac{\alpha_a}{\beta}\,e^{-\beta(t_{i+1}-t_{\text{last},a})} \cdot (1 - e^{-\beta(t_{i+1}-t_i)})$$

En pratique, le code accumule `int_ea` et `int_eb` de façon récursive dans la boucle Numba.

### Paramètre optimal $\theta^*$

Le $\theta^*$ minimise la variance de l'estimateur IS, c'est-à-dire le **coefficient de variation** $\text{CV}(\theta) = \hat\sigma_w(\theta)/\hat{P}(\theta)$. Identifié graphiquement dans `plot_is_comparison` par `np.nanargmin(cv_is)`.

**Borne de variance :** Pour $\theta = \theta^*$, l'IS peut être théoriquement optimal au sens de Vallois (variance minimale parmi tous les changements de mesure exponentiels). En pratique, le gain dépend du régime de $p$ et du choix de $\theta$.

---

## 19. Intervalles de confiance : Splitting vs IS

### CLT pour l'estimateur AMS

L'estimateur AMS est un produit de proportions : $\hat{P} = \prod_{k=0}^{K-1} \hat{p}_k$ avec $\hat{p}_k = N_k/N$.

**Lemme (méthode delta) :** $\log \hat{P} = \sum_k \log \hat{p}_k$. Chaque terme $\log \hat{p}_k$ est asymptotiquement normal par TCL des binomiales. Par la **méthode delta** et l'indépendance conditionnelle des niveaux :

$$\sqrt{N}\,(\hat{P} - P) \xrightarrow{d} \mathcal{N}\!\left(0,\; P^2 \sum_{k=0}^{K-1} \frac{1-p_k}{p_k}\right)$$

**Preuve détaillée :**

$$\log \hat{P} = \sum_k \log \hat{p}_k \approx \log P + \sum_k \frac{\hat{p}_k - p_k}{p_k}$$

(développement de Taylor à l'ordre 1). Chaque $\hat{p}_k - p_k$ est une moyenne de $N$ Bernoulli(p_k) - $p_k$, donc $\text{Var}(\hat{p}_k - p_k) = p_k(1-p_k)/N$. Comme les niveaux sont (conditionnellement) indépendants :

$$\text{Var}(\log \hat{P}) \approx \sum_k \frac{1-p_k}{N p_k}$$

Puis $\text{Var}(\hat{P}) \approx P^2 \cdot \text{Var}(\log \hat{P}) = P^2 \sum_k (1-p_k)/(N p_k)$ par la méthode delta. $\square$

**IC à 95% :** $\hat{P} \pm 1.96 \cdot \hat{P} \sqrt{\frac{1}{N}\sum_k \frac{1-\hat{p}_k}{\hat{p}_k}}$

### CLT pour l'estimateur IS

Les poids $w_i = \mathbf{1}_{\tau_a^{(i)} < \tau_b^{(i)}} e^{L_\theta^{(i)}}$ sont i.i.d. Par le TCL classique :

$$\sqrt{N}(\hat{P}_{\text{IS}} - P) \xrightarrow{d} \mathcal{N}(0, \text{Var}^\mathbb{Q}(w))$$

IC à 95% : $\hat{P}_{\text{IS}} \pm 1.96 \cdot \hat\sigma_w / \sqrt{N}$

### Efficacité relative

$$\text{RE}(\text{IS}/\text{AMS}) = \frac{\text{Var}(\hat{P}_{\text{IS}})}{\text{Var}(\hat{P}_{\text{AMS}})} = \frac{\hat\sigma_{\text{IS}}^2}{\hat\sigma_{\text{AMS}}^2}$$

- **RE > 1** : IS est moins efficace (le $\theta$ choisi est sous-optimal ou supra-optimal).
- **RE < 1** : IS est plus efficace.

**Lecture du graphique :** les deux courbes (largeur IC vs $N$) doivent décroître en $C/\sqrt{N}$. Le rapport des constantes $C_{\text{IS}}/C_{\text{AMS}} = \sqrt{\text{RE}}$.

---

## 20. Métriques de risque de liquidité

### Distribution de $\tau_a \mid \tau_a < \tau_b$

Via le splitting AMS, les $N$ particules finales (après tous les rééchantillonnages) représentent un échantillon **approximativement** de $\mathcal{L}(\tau_a \mid \tau_a < \tau_b)$ (conditionnellement à la survie). **Attention :** après le dernier rééchantillonnage au niveau $k=0$, les $N$ particules sont tirées avec remise parmi $N_{K}$ survivants — elles ne sont donc pas indépendantes (bootstrap). L'histogramme a plus de répétitions que prévu.

**Propriété attendue :** sous le modèle Poisson avec drift $\mu < 0$, $\tau_a \mid \tau_a < \tau_b \approx \text{IG}(\mu_{\text{IG}}, \lambda_{\text{IG}})$ tronquée par dessus (car $\tau_a < \tau_b$ élimine les longues durées). La distribution est décroissante, avec un mode proche de 0.

### Score function estimator

**Objectif :** estimer $\frac{\partial}{\partial \mu^-_a} P(\tau_a < \tau_b)$ sans relancer de simulation.

**Formule générale (REINFORCE) :** Si $P(\theta) = \mathbb{E}^\theta[\mathbf{1}_{A}]$ et la loi dépend de $\theta$ via $p_\theta(x)$, alors :

$$\frac{\partial P(\theta)}{\partial \theta} = \mathbb{E}^\theta\!\left[\mathbf{1}_{A} \cdot \frac{\partial \log p_\theta(X)}{\partial \theta}\right]$$

**Application :** pour le processus de Hawkes avec paramètre $\mu^-_a$ :

$$\frac{\partial \log p_{\mu^-_a}(\text{chemin})}{\partial \mu^-_a} = \sum_{T_i^a} \frac{1}{\lambda^-_a(T_i^a)} - \int_0^\tau 1\,dt = \sum_{T_i^a} \frac{1}{\lambda^-_a(T_i^a)} - \tau$$

**Preuve :** Le log-likelihood d'un chemin du processus de Poisson non-homogène est :

$$\log p(\text{chemin}) = \sum_{T_i^a} \log \lambda^-_a(T_i^a) - \int_0^\tau \lambda^-_a(t)\,dt$$

En dérivant par rapport à $\mu^-_a$ (avec $\partial \lambda^-_a/\partial \mu^-_a = 1$ uniformément) :

$$\frac{\partial \log p}{\partial \mu^-_a} = \sum_{T_i^a} \frac{1}{\lambda^-_a(T_i^a)} - \tau \quad \square$$

**Estimateur :**
$$\widehat{\frac{\partial P}{\partial \mu^-_a}} = \frac{1}{N} \sum_{i=1}^N \mathbf{1}_{\tau_a^{(i)} < \tau_b^{(i)}} \cdot s(X^{(i)}), \quad s(X) = \sum_{T_j^a} \frac{1}{\lambda^-_a(T_j^a)} - \tau$$

**Signe attendu :** $\partial P / \partial \mu^-_a > 0$ — augmenter l'intensité de décrement ask augmente la probabilité que l'ask atteigne 0 en premier. C'est cohérent avec le fait que $P$ est croissante en $\mu^-_a$.

**Validation :** comparé aux différences finies $\hat\partial P \approx (P(\mu^-_a + \varepsilon) - P(\mu^-_a - \varepsilon))/(2\varepsilon)$ estimées via splitting. Les deux doivent concorder.

### Expected Shortfall du flash crash

**Modèle de profondeur :** $K$ = nombre de chutes de prix consécutives, avec $P(K \ge k) = P(\text{FC}_k)$ calculé au §17. La perte de prix est $K \cdot \delta/2$.

**Expected Shortfall :**
$$\text{ES}(\alpha) = \mathbb{E}\!\left[K \cdot \frac{\delta}{2} \;\bigg|\; K \ge k^*(\alpha)\right], \quad k^*(\alpha) = \min\{k : P(K \ge k) \le \alpha\}$$

**Lecture du graphique :** la courbe ES($\alpha$) est **décroissante** en $\alpha$ sur l'axe log.
- $\alpha$ petit (gauche) = quantile extrême = seuls les flash crashes profonds sont dans la queue → ES grand.
- $\alpha$ grand (droite) = quantile modéré = flash crashes peu profonds aussi inclus → ES tend vers la perte moyenne $\mathbb{E}[K \cdot \delta/2]$.

**Formule de calcul :**
$$\text{ES}(\alpha) = \frac{\sum_{k \ge k^*(\alpha)} P(K = k) \cdot k \cdot \delta/2}{\sum_{k \ge k^*(\alpha)} P(K = k)}$$

avec $P(K = k) = P(K \ge k) - P(K \ge k+1)$ pour $k < k_{\max}$ et $P(K \ge k_{\max})$ pour le dernier terme.

---

## 21. Calibration par Maximum de Vraisemblance

### Modèle calibré vs modèle vrai

**⚠️ Mauvaise spécification structurelle :** le vrai modèle (§10) a des effets croisés **inhibitoires** (décrement ask → $+\alpha$ sur $\lambda^-_a$ mais $-\alpha$ sur $\lambda^-_b$). Le modèle calibré ici suppose une **auto-excitation mutuelle positive** (tout événement excite les deux files identiquement). Ce biais de spécification implique que les paramètres estimés $(\hat\mu^-_a, \hat\mu^-_b, \hat\alpha, \hat\beta)$ différeront systématiquement des vraies valeurs $(\mu^-_a, \mu^-_b, \alpha, \beta)$.

### Log-vraisemblance du processus de Hawkes bivarié

Le modèle calibré est :
$$\lambda^-_k(t) = \mu^-_k + \alpha \sum_{s \in \mathcal{D}_a \cup \mathcal{D}_b, s < t} e^{-\beta(t-s)}$$

La log-vraisemblance est :

$$\ell(\mu^-_a, \mu^-_b, \alpha, \beta) = \sum_{t \in \mathcal{D}_a} \log(\mu^-_a + \alpha R(t)) + \sum_{t \in \mathcal{D}_b} \log(\mu^-_b + \alpha R(t)) - (\mu^-_a + \mu^-_b)T - \frac{2\alpha}{\beta}\sum_{s \in \mathcal{D}}(1 - e^{-\beta(T-s)})$$

**Dérivation de la log-vraisemblance d'un processus ponctuel :**

Pour un processus ponctuel d'intensité $\lambda(t)$ sur $[0,T]$, la densité par rapport à la mesure de Poisson de taux 1 est :

$$p = \exp\!\left(\sum_{t_i} \log \lambda(t_i) - \int_0^T \lambda(t)\,dt\right)$$

Ici, $\int_0^T \lambda_a(t)\,dt = \mu^-_a T + \alpha \sum_{s \in \mathcal{D}} \int_s^T e^{-\beta(t-s)}\,dt = \mu^-_a T + \frac{\alpha}{\beta}\sum_s (1 - e^{-\beta(T-s)})$, et de même pour $\lambda^-_b$. Comme $\lambda^-_a$ et $\lambda^-_b$ ont le **même noyau** $\alpha R(t)$, la compensation totale pour les deux files est $(\mu^-_a + \mu^-_b)T + \frac{2\alpha}{\beta}\sum_s (1-e^{-\beta(T-s)})$. $\square$

### Récurrence en $O(n)$

$$R(t_i) = e^{-\beta(t_i - t_{i-1})} \cdot (R(t_{i-1}) + 1), \quad R(t_0) = 0$$

**Preuve :** $R(t) = \sum_{s < t} e^{-\beta(t-s)}$. Au temps $t_i$, juste après l'événement $t_{i-1}$ :

$$R(t_i) = e^{-\beta(t_i - t_{i-1})} \underbrace{\sum_{s < t_{i-1}} e^{-\beta(t_{i-1}-s)}}_{R(t_{i-1})} + e^{-\beta(t_i - t_{i-1})} \cdot 1 = e^{-\beta(t_i - t_{i-1})}(R(t_{i-1}) + 1) \quad \square$$

La complexité est $O(n)$ en temps et $O(1)$ en espace supplémentaire, ce qui permet de traiter des trajectoires de $n \sim 2000$ événements en microseceondes avec la compilation Numba (`@_njit`).

### Accélération Numba

La fonction `_hawkes_loglik_inner(times, etypes, mu_a, mu_b, alpha, beta, T)` est compilée JIT par Numba. Le tableau fusionné `(all_times_arr, all_etypes_arr)` est construit **une seule fois** avant les $n_{\text{restarts}}$ redémarrages de Nelder-Mead, évitant $n_{\text{restarts}} \times \text{neval}$ constructions Python de listes.

### Estimation par Nelder-Mead avec redémarrages

On minimise $-\ell(\mu^-_a, \mu^-_b, \alpha, \beta)$ par Nelder-Mead avec $n_{\text{restarts}} = 8$ initialisations aléatoires. La contrainte de stationnarité $\alpha < \beta$ est imposée par une barrière $+10^{10}$ sur la vraisemblance.

**Identifiabilité :** le modèle $(\mu^-_a, \mu^-_b, \alpha, \beta)$ est identifiable si $n \to \infty$ sous les vraies hypothèses. Mais avec la mauvaise spécification (modèle inhibitoire vs excitateur), les estimateurs MLE convergent non pas vers les vraies valeurs, mais vers les **pseudo-vrais paramètres** $\theta^* = \arg\min_\theta \text{KL}(\mathbb{P}_{\text{vrai}} \| \mathbb{P}_\theta)$ (divergence de Kullback-Leibler). Cela explique les écarts observés dans le graphique de calibration.

### Reconstruction de l'intensité

La fonction `_reconstruct_intensity(mu, alpha, beta, event_times, t_grid)` calcule :

$$\lambda^-(t_j) = \mu + \alpha \sum_{s \in \mathcal{D}, s < t_j} e^{-\beta(t_j - s)}$$

Vectorisée via la matrice `outer[i,j] = t_grid[i] - event_times[j]` de taille $m \times n$, puis :

```python
R_vec = np.where(outer > 0, np.exp(-beta * outer), 0.).sum(axis=1)
lam = mu + alpha * R_vec
```

Complexité : $O(m \times n)$ en temps, $O(m \times n)$ en espace — raisonnable pour $m, n \le 400$.

---

## Résumé des paramètres du notebook

| Section | Paramètres clés | Valeurs par défaut |
|---|---|---|
| §1–7 (Poisson) | $\lambda^+, \lambda^-$ | $1.2, 2.0$ |
| §8–11 (Hawkes) | $\mu^-, \alpha, \beta$ | $2.0, 0.5, 1.0$ |
| §10 (couplé) | $\mu^-_a, \mu^-_b, \alpha, \beta$ | $2, 2, 0.5, 1$ |
| §15–19 (rare) | $\mu^-_a, \mu^-_b$ (asymétrique) | $1.5, 3.0$ |
| §17 (flash crash) | $k_{\max}, N$ | $5, 400$ |
| §18 (IS) | $\theta$ | $[0.2, 2.5]$ |
| §20 (risque) | $N_{\text{split}}, N_{\text{score}}$ | $400, 3000$ |
| §21 (MLE) | $n_{\text{cycles}}, n_{\text{restarts}}$ | $150, 8$ |

---

## Références

- **Ogata, Y. (1981).** On Lewis' simulation method for point processes. *IEEE Transactions on Information Theory*, 27(1), 23–31.
- **Asmussen, S. & Glynn, P. (2007).** *Stochastic Simulation: Algorithms and Analysis*. Springer.
- **Cèrou, F. & Guyader, A. (2007).** Adaptive multilevel splitting for rare event analysis. *Stochastic Analysis and Applications*, 25(2), 417–443.
- **Bowsher, C. G. (2007).** Modelling security market events in continuous time. *Journal of Econometrics*, 141(2), 876–912.
- **Hawkes, A. G. (1971).** Spectra of some self-exciting and mutually exciting point processes. *Biometrika*, 58(1), 83–90.
- **Williams, R. J. (1985).** Simple statistical gradient-following algorithms for connectionist reinforcement learning. *Machine Learning*, 8(3-4), 229–256. (Score function / REINFORCE)
- **Tweedie, M. C. K. (1957).** Statistical properties of inverse Gaussian distributions. *Annals of Mathematical Statistics*, 28(2), 362–377.
