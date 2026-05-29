# Préparation orale - explication complète

Ce fichier sert à comprendre le fond du projet, pas à réciter le script mot à mot. Les scripts actifs de la soutenance sont `script_Anass.md` et `script_Taha.md`. L'objectif à l'oral est de montrer une progression logique :

1. on part d'un modèle de carnet simple et analytique ;
2. on ajoute de la mémoire avec Hawkes parce que le modèle Poisson est trop pauvre ;
3. on commence par économiser le budget de simulation avec AMS sur un benchmark modéré, puis on l'utilise pour les événements rares ;
4. on termine par une calibration, puis une application prudente à des données réelles.

Les sources cohérentes sont le notebook, le rapport final, le PDF `MODAL_Queue_Reactive-4.pdf` et les slides du cours sur Monte Carlo, splitting, AMS et importance sampling.

## 1. Message central du projet

Le projet étudie un carnet d'ordres simplifié. On regarde principalement les volumes disponibles au meilleur ask et au meilleur bid :

- `q_a` : volume au meilleur ask ;
- `q_b` : volume au meilleur bid ;
- un côté s'épuise quand son volume atteint zéro ;
- si le ask s'épuise avant le bid, le prix monte ;
- si le bid s'épuise avant le ask, le prix baisse.

Le projet ne cherche pas à prédire parfaitement un marché réel. Il cherche à construire une chaîne cohérente :

- un modèle de dynamique du carnet ;
- une loi ou une simulation des temps d'épuisement ;
- une méthode efficace pour réduire le budget de simulation, puis traiter les événements rares ;
- une calibration testable sur données synthétiques et réelles.

Une bonne phrase de défense :

> Notre objectif n'est pas de faire un modèle de trading complet, mais de comprendre comment la dynamique locale du carnet produit des temps d'épuisement, des mouvements de prix et des probabilités de cascade.

## 2. Le modèle Queue Reactive du PDF Modal

Le PDF `MODAL_Queue_Reactive-4.pdf` décrit le cadre Queue Reactive :

- l'état du carnet influence les intensités d'événements ;
- les événements sont des ajouts de limites, des annulations et des trades ;
- quand une meilleure limite est vidée, le niveau adjacent devient la nouvelle meilleure limite ;
- pour plusieurs sauts de prix, il faut reconstruire le carnet après chaque saut.

Dans notre projet, on reprend cette idée avec une version simplifiée :

- premier niveau : dynamique principale d'épuisement ;
- deuxième niveau : réserve de volume qui devient le nouveau premier niveau après un saut ;
- prix : fonction du côté qui s'épuise en premier.

La partie "deuxième limite" vient directement de là. Sans deuxième limite, on peut simuler un seul saut de prix, mais pas une cascade. Avec le deuxième niveau, on peut enchaîner plusieurs cycles.

## 3. Modèle Poisson de base

Dans le premier modèle, les arrivées et les retraits sont des processus de Poisson indépendants.

Pour un côté du carnet :

```text
q(t) = q0 + N+(t) - N-(t)
```

où :

- `N+` représente les ajouts de volume ;
- `N-` représente les retraits de volume ;
- `q0` est le volume initial ;
- le temps d'épuisement est `tau = inf{t : q(t) <= 0}`.

Si `lambda+ < lambda-`, le volume a une dérive négative et finit par atteindre zéro. Dans le notebook et le rapport :

- `lambda+ = 1.2`,
- `lambda- = 2.0`,
- dérive `mu = lambda+ - lambda- = -0.8`,
- variance instantanée `sigma^2 = lambda+ + lambda- = 3.2`,
- `q0 = 10`.

L'approximation brownienne donne :

```text
q(t) approx q0 + mu t + sigma W_t
```

Le temps d'atteinte de zéro d'un brownien avec dérive suit une loi inverse-gaussienne :

```text
tau ~ IG(mu_IG, lambda_IG)
mu_IG = q0 / |mu| = 12.5
lambda_IG = q0^2 / sigma^2 = 31.25
```

Résultats importants :

- moyenne théorique : `12.500` ;
- moyenne simulée : `12.517`, soit `+0.14 %` ;
- variance théorique : `62.500` ;
- variance simulée : `62.706`, soit `+0.33 %` ;
- test KS : statistique `0.0055`, p-valeur `0.0971`.

## 4. Comment expliquer le test KS

Le test KS compare la distribution empirique des temps simulés à la distribution inverse-gaussienne théorique.

Hypothèse nulle :

```text
H0 : les temps simulés sont compatibles avec la loi IG proposée.
```

Résultat :

```text
p = 0.0971 > 0.05
```

Donc on ne rejette pas `H0` au seuil de 5 %. C'est un bon résultat pour nous, parce que l'objectif était de valider l'approximation inverse-gaussienne. Cela veut dire que l'écart observé entre la simulation et la loi IG n'est pas statistiquement suffisant pour dire que l'approximation est mauvaise.

Il faut rester précis :

- cela ne prouve pas que la loi IG est exacte ;
- cela dit seulement que les données simulées ne contredisent pas cette approximation au seuil de 5 % ;
- à 10 %, le résultat serait limite, donc il vaut mieux dire "validation numérique raisonnable" plutôt que "preuve parfaite".

Réponse courte si on vous demande :

> Ne pas rejeter à 5 % est positif ici, car on voulait vérifier que l'approximation IG décrit bien les temps d'épuisement. La p-valeur 0.097 signifie que l'écart observé est faible au regard du seuil standard de 5 %, même si ce n'est pas une preuve exacte de la loi.

## 5. Probabilité de ruine

On veut ensuite comparer deux côtés du carnet :

```text
P(tau_a < tau_b)
```

C'est la probabilité que le ask s'épuise avant le bid, donc que le prix monte.

Dans le cas Poisson indépendant, on peut utiliser les lois des temps d'arrêt :

```text
P(tau_a < tau_b) = integral f_a(t) P(tau_b > t) dt
```

Cette formule sert de contrôle. Elle donne une référence analytique ou semi-analytique avant de passer aux modèles plus complexes.

Message oral :

> Le modèle Poisson est utile parce qu'il donne une base vérifiable. Mais il manque un point essentiel : les événements de carnet ne sont pas sans mémoire.

## 6. Pourquoi passer à Hawkes

Le modèle Poisson suppose des intensités constantes. Or dans un carnet réel, les événements arrivent souvent en paquets :

- une annulation peut provoquer d'autres annulations ;
- un trade peut révéler une pression directionnelle ;
- l'arrivée de limites peut ralentir l'épuisement ;
- la dynamique d'un côté peut influencer l'autre côté.

Un processus de Hawkes permet de modéliser cette mémoire par des noyaux exponentiels.

Forme générale :

```text
lambda(t) = mu + somme alpha exp(-beta(t - T_i))
```

Interprétation :

- `mu` : intensité de fond ;
- `alpha` : amplitude de l'effet mémoire ;
- `beta` : vitesse d'oubli ;
- `alpha / beta` mesure l'importance cumulée d'un événement passé.

Dans notre modèle :

- les retraits du même côté peuvent augmenter l'intensité future de retrait ;
- les ajouts de volume peuvent jouer un rôle inhibiteur ;
- on clippe l'intensité à zéro quand l'effet inhibiteur la rendrait négative.

Résultat important du rapport :

- intensité stationnaire théorique : environ `2.80` ;
- intensité empirique simulée : `2.9649 +/- 0.0079` ;
- écart : `+5.89 %`.

Pourquoi cet écart ?

Le clipping à zéro et la troncature numérique modifient légèrement la dynamique. En théorie linéaire pure, l'intensité peut devenir négative si on met une inhibition forte. En simulation, une intensité négative n'a pas de sens, donc on la remplace par zéro. Ce choix rend la simulation réaliste, mais crée un petit biais.

Réponse si on vous challenge :

> L'écart de 5.9 % ne contredit pas le modèle Hawkes. Il vient surtout de la version simulée, qui impose une intensité positive par clipping. C'est un compromis numérique nécessaire.

## 7. Hawkes couplé entre ask et bid

Le Hawkes simple modélise la mémoire d'un côté. Le Hawkes couplé ajoute l'interaction entre ask et bid.

Idée :

- si le ask se vide vite, cela change l'équilibre du carnet ;
- cette pression peut influencer aussi le bid ;
- le modèle crée donc une dynamique de contagion.

Dans le rapport, la comparaison montre :

| Régime | Temps moyen d'épuisement |
|---|---:|
| Poisson individuel | `12.42` |
| Minimum de deux Poisson | `8.56` |
| Hawkes individuel | `8.80` |
| Hawkes couplé | `5.91` |

Message :

> La mémoire réduit déjà le temps d'épuisement. Le couplage le réduit encore plus, parce qu'un déséquilibre local peut se propager à l'autre côté du carnet.

La slide avec les quatre régimes sert à isoler les effets :

- Poisson individuel : référence sans mémoire ;
- minimum de deux Poisson : effet purement statistique d'avoir deux horloges en compétition ;
- Hawkes individuel : effet mémoire ;
- Hawkes couplé : effet mémoire plus contagion entre côtés.

## 8. Deuxième limite et reconstruction du carnet

Le PDF Modal insiste sur un point : après l'épuisement du meilleur niveau, il faut promouvoir le deuxième niveau.

Exemple côté ask :

```text
si q_a1 atteint 0 :
    le prix monte
    q_a1 <- q_a2(tau_a)
```

La question devient :

```text
Quelle est la distribution de q2 au moment où q1 s'épuise ?
```

Nous comparons deux versions.

### Sans couplage

Le niveau 2 a une intensité d'ajout constante :

```text
lambda^+_{2,0}(t) = mu^+_2
```

C'est une référence autonome. Le niveau 2 évolue sans regarder ce qui arrive au niveau 1.

Résultat symétrique :

- ask : moyenne `7.97` ;
- bid : moyenne `7.92`.

### Avec couplage à l'intensité du premier niveau

Le niveau 2 reçoit un supplément d'intensité quand le niveau 1 subit des décréments :

```text
lambda^+_{2,c}(t)
= mu^+_2 + somme a exp(-b(t - T_i^downarrow))
```

Interprétation :

- quand le meilleur niveau se vide, le modèle suppose que de la profondeur se reconstitue au deuxième niveau ;
- cela représente une réaction du carnet autour du meilleur prix.

Résultat symétrique avec couplage :

- ask : moyenne `11.19` ;
- bid : moyenne `10.16`.

La slide 9 doit donc être lue comme une comparaison de distributions :

- sans couplage : deuxième niveau plus faible, proche d'une référence Poisson ;
- avec couplage : deuxième niveau plus rempli, car les décréments du premier niveau déclenchent des ajouts au deuxième.

## 9. Drift du prix

Quand le ask s'épuise avant le bid, le prix monte. Quand le bid s'épuise avant le ask, le prix baisse.

Si :

```text
p = P(tau_a < tau_b)
```

alors l'espérance du saut de prix est :

```text
E[Delta p] = delta^p / 2 * (2p - 1)
```

Conséquences :

- si `p = 1/2`, le prix est martingale ;
- si `p > 1/2`, le prix a une dérive positive ;
- si `p < 1/2`, le prix a une dérive négative.

Résultats du rapport :

- symétrique : `p_up = 0.518`, drift `+0.0185` ;
- asymétrique : `p_up = 0.738`, drift `+0.2375`.

Message :

> Ce n'est pas une validation indépendante : si `p_up` et le drift sont calculés sur les mêmes cycles avec des sauts fixes `+/- delta^p/2`, l'égalité empirique est mécanique à l'arrondi près. C'est une vérification de cohérence interne : la règle de prix implémentée respecte la formule théorique, et l'asymétrie des intensités se transmet bien au signe de la dérive.

## 10. Réduire le coût de simulation avant les événements rares

Dans la partie II, on introduit AMS avec un cas de contrôle où `p approx 0.14`. Ce cas est assez fréquent pour être vérifié par Monte Carlo direct.

Le Monte Carlo direct sert alors de référence : on vérifie que le splitting AMS donne la même loi et la même précision pratique avec moins de trajectoires.

Message à retenir :

```text
0.14 est un benchmark contrôlé pour mesurer le gain de budget.
```

Dans le contrôle sur la loi de `Q2(tau)` :

- Monte Carlo direct : `N = 10^5` trajectoires ;
- splitting AMS : `N = 3 * 10^4` trajectoires ;
- les histogrammes ont la même forme et le même support ;
- on obtient donc une précision comparable avec environ trois fois moins de trajectoires.

Pourquoi c'est logique ?

Le Monte Carlo direct relance toutes les trajectoires depuis zéro. L'erreur statistique décroît comme `1 / sqrt(M)`, donc pour diviser l'erreur par deux, il faut environ quatre fois plus de simulations. AMS recycle les trajectoires qui ont déjà atteint des niveaux intermédiaires, donc il utilise mieux le budget.

Phrase à dire à l'oral :

> Avant de s'intéresser aux cascades rares, on utilise un cas de contrôle à `p≈0.14` pour comparer AMS au Monte Carlo direct. Le résultat est que l'AMS garde la bonne distribution tout en utilisant moins de simulations. On applique ensuite la même logique aux cascades rares.

## 11. Pourquoi Monte Carlo direct devient insuffisant pour les vrais rares

Le cours explique que l'estimateur Monte Carlo d'une probabilité rare `p` a un coefficient de variation :

```text
CV approx sqrt((1 - p) / (M p))
```

Pour une précision relative `epsilon`, il faut environ :

```text
M approx 1 / (p epsilon^2)
```

Si `p = 10^-7` et `epsilon = 10 %`, il faut environ `10^9` trajectoires.

Si `p = 10^-13`, il faut environ `10^15` trajectoires.

Donc le Monte Carlo direct ne peut pas traiter les cascades profondes. Il est utile pour valider les premiers événements, mais pas pour estimer les probabilités extrêmes.

## 12. AMS : Adaptive Multilevel Splitting

AMS vient du cours sur le splitting. Dans notre projet, il a deux rôles :

- sur le benchmark modéré `p approx 0.14`, il sert à économiser le budget de simulation et à valider le recyclage ;
- sur les flash crashes, il sert à transformer un événement très rare en une suite d'événements moins rares.

Au lieu d'estimer directement :

```text
P(score >= niveau final)
```

on écrit :

```text
P(A) = P(A1) P(A2 | A1) ... P(Ak | A_{k-1})
```

Algorithme conceptuel :

1. simuler `N` trajectoires ;
2. calculer un score pour chaque trajectoire ;
3. supprimer les trajectoires les moins avancées ;
4. les remplacer par des copies de trajectoires meilleures ;
5. reprendre la simulation à partir de l'état sauvegardé ;
6. multiplier les probabilités conditionnelles estimées.

Point très important pour notre projet :

> Dans un modèle Hawkes, il ne suffit pas de sauvegarder le volume. Il faut aussi sauvegarder l'état mémoire : intensités, événements passés utiles, résidus exponentiels.

Sinon, le redémarrage d'une particule casserait la dynamique Hawkes.

Résultats AMS du notebook et du rapport sur le benchmark modéré :

- probabilité cible autour de `0.14`, donc pas rare ;
- coefficient de variation qui diminue comme `1/sqrt(N)` ;
- exemple : `CV = 0.349` pour `N=50`, puis `CV = 0.048` pour `N=3200`.

Message :

> AMS ne change pas le modèle. Il change la façon d'utiliser les trajectoires simulées : d'abord pour réduire le budget sur un cas contrôlé, puis pour rendre accessibles les vraies cascades rares.

## 13. Flash crash de profondeur k

Le flash crash de profondeur `k` est défini comme une séquence de `k` vidages successifs du bid avant le ask :

```text
FC_k = {tau_b^(1) < tau_a, ..., tau_b^(k) < tau_a}
```

On peut écrire :

```text
P(FC_k) = produit c_i
c_i = P(tau_b^(i) < tau_a | FC_{i-1})
```

Résultats du rapport :

| k | Probabilité |
|---:|---:|
| 1 | `1.42e-1` |
| 2 | `6.06e-3` |
| 3 | `1.88e-4` |
| 4 | `4.46e-6` |
| 5 | `1.11e-7` |
| 6 | `1.11e-9` |
| 7 | `1.36e-11` |
| 8 | `1.87e-13` |

Pourquoi `p1^k` n'est pas la bonne formule ?

Parce que les cycles ne sont pas indépendants :

- le niveau 2 promu après un saut n'a pas la même loi qu'un niveau initial ;
- les intensités Hawkes gardent une mémoire ;
- le carnet après un premier vidage n'est pas un reset parfait.

Dans les paramètres du rapport, les probabilités conditionnelles au-delà du premier cycle sont plus petites que `p1`, donc `P(FC_k)` tombe plus vite que `p1^k`.

Réponse courte :

> `p1^k` serait la formule d'un modèle indépendant et sans mémoire. Notre modèle garde la mémoire Hawkes et la distribution du deuxième niveau, donc les cycles ne sont pas iid.

## 14. Splitting en deux phases pour le deuxième niveau

La partie "two-phase splitting" sépare :

1. la simulation jusqu'au premier épuisement ;
2. la reprise à partir de l'état atteint pour analyser la suite.

Résultat ask du rapport :

- moyenne complète : `12.90` ;
- moyenne online/two-phase : `12.91` ;
- temps complet : `7.69 s` ;
- temps online : `0.67 s`.

Donc le résultat statistique est conservé, mais le coût est beaucoup plus faible.

Message :

> Le splitting en deux phases ne change pas la loi ciblée. Il réutilise intelligemment des états intermédiaires pour éviter de resimuler toute la trajectoire depuis zéro.

## 15. Importance sampling

L'importance sampling vient aussi du cours. On simule sous une loi modifiée où l'événement rare arrive plus souvent, puis on corrige par un poids de vraisemblance.

Dans notre cas, pour favoriser un vidage bid avant ask :

```text
lambda_a modifiee = exp(-theta) lambda_a
lambda_b modifiee = exp(theta) lambda_b
```

Le log-poids utilisé est :

```text
log L =
(exp(-theta)-1) I_a
+ (exp(theta)-1) I_b
+ theta N_a
- theta N_b
```

Interprétation :

- `theta` faible : on ne favorise pas assez l'événement ;
- `theta` trop grand : l'événement arrive souvent mais les poids deviennent instables ;
- il faut choisir un compromis.

Résultat :

- meilleur theta dans l'expérience : `theta = 0.30` ;
- probabilité estimée : environ `0.139` ;
- comparaison CLT : `Std AMS = 0.01712`, `Std IS = 0.01289`, `RE = 0.57`.

Ici, pour cet événement modéré, IS est plus efficace à coût fixé. Mais pour des cascades profondes, AMS reste plus naturel car il exploite la structure en niveaux.

Piège à éviter :

> Ne pas dire "AMS est toujours meilleur que IS". Dire plutôt : IS est très bon quand on sait bien incliner la mesure ; AMS est plus robuste pour construire progressivement un événement rare structuré.

## 16. Calibration MLE

La calibration cherche à retrouver les paramètres du modèle à partir des temps d'événements.

Pour un processus ponctuel, la log-vraisemblance est :

```text
ell = somme log lambda(t_i) - integral lambda(t) dt
```

Dans le modèle réduit bid/ask :

- `mu_a`, `mu_b` sont les intensités de fond ;
- `alpha` mesure la mémoire ;
- `beta` mesure la vitesse d'oubli ;
- condition de stabilité : `2 alpha < beta`.

Résultat synthétique sur 150 cycles :

| Paramètre | Vrai | MLE |
|---|---:|---:|
| `mu_a` | `3.0` | `3.013` |
| `mu_b` | `1.5` | `1.503` |
| `alpha` | `0.35` | `0.370` |
| `beta` | `1.0` | `1.154` |

Lecture :

- les intensités de fond sont très bien retrouvées ;
- `alpha` et `beta` sont moins précis car ils sont corrélés dans la vraisemblance ;
- sur un échantillon court, plusieurs couples `(alpha, beta)` peuvent produire une mémoire effective assez proche.

Réponse si on demande pourquoi `beta` est moins bon :

> `beta` contrôle la vitesse de décroissance. Sur seulement 150 cycles, on observe peu de longues queues de mémoire, donc la vraisemblance identifie mieux le niveau moyen d'intensité que la forme exacte de la décroissance.

## 17. Bitcoin Black Thursday

Application réelle :

- actif : Bitcoin ;
- épisode : Black Thursday du 12 mars 2020 ;
- données : bougies Binance 1h ;
- calibration : 1696 observations pré-crise ;
- événement regardé : séquence de 5 bougies négatives.

Résultat de calibration pré-crise :

- `alpha approx 0` ;
- le régime pré-crise est donc presque Poisson ;
- probabilité AMS pour 5 bougies négatives consécutives : `8.47e-6`, soit environ `1 / 118000`.

Lecture correcte :

> Le modèle calibré sur la période calme dit que la séquence observée est très rare sous ce régime. Cela ne veut pas dire que le modèle prédit la crise. Cela montre plutôt qu'une calibration calme peut sous-estimer fortement un changement de régime.

Limites à dire clairement :

- données 1h, pas tick-by-tick ;
- les bougies agrègent beaucoup d'information ;
- le modèle ne contient pas les news, liquidations, carnets multi-plateformes, funding, ni contagion macro ;
- donc c'est une illustration de méthode, pas un modèle complet du Black Thursday.

## 18. Pourquoi GameStop a été abandonné

Le rapport explique que GameStop n'était pas adapté :

- trop peu d'observations dans l'épisode disponible ;
- données journalières trop grossières ;
- dynamique fortement exogène, liée à Reddit, options, short squeeze ;
- le modèle local de carnet ne suffit pas à expliquer ce mécanisme.

Bonne phrase :

> On a préféré Bitcoin parce que les données horaires donnent une série plus exploitable pour tester la méthode, même si ce n'est pas encore du vrai carnet tick-by-tick.

## 19. Lien avec les slides de cours

Les slides du cours servent de justification méthodologique.

### Monte Carlo

Le cours montre deux choses utiles ici. D'abord, l'erreur de Monte Carlo décroît lentement en `1/sqrt(M)`, ce qui motive l'économie de budget même sur un benchmark modéré. Ensuite, quand `p` devient très petit, l'erreur relative explose comme `1/sqrt(Mp)`.

Dans notre projet, cela justifie l'abandon du MC direct pour les flash crashes profonds.

### Splitting / AMS

Le cours présente l'idée de décomposer un événement rare en niveaux. Dans notre projet :

- les niveaux sont liés à la progression vers l'épuisement ou vers la cascade ;
- chaque particule transporte l'état complet du carnet ;
- l'estimateur est validé par convergence du CV en `1/sqrt(N)`.

### Importance sampling

Le cours présente le changement de mesure et la correction par vraisemblance. Dans notre projet :

- on incline les intensités ask/bid ;
- on corrige par le log-poids ;
- on compare la variance avec AMS.

## 20. Cohérence des chiffres à retenir

Voici les nombres les plus importants à connaître :

| Sujet | Nombre |
|---|---:|
| IG moyenne théorique | `12.5` |
| IG moyenne simulée | `12.517` |
| IG variance simulée | `62.706` |
| KS p-valeur | `0.0971` |
| Hawkes stationnaire théorique | `2.80` |
| Hawkes empirique | `2.9649` |
| Poisson individuel | `12.42` |
| Hawkes couplé | `5.91` |
| Q2 sans couplage ask/bid | `7.97 / 7.92` |
| Q2 avec couplage ask/bid | `11.19 / 10.16` |
| Price drift symétrique | `+0.0185` |
| Price drift asymétrique | `+0.2375` |
| Benchmark AMS modéré | environ `0.14`, pas rare |
| Flash crash k=5 | `1.11e-7` |
| Flash crash k=8 | `1.87e-13` |
| IS theta optimal | `0.30` |
| RE IS vs AMS | `0.57` |
| BTC 5 bougies négatives | `8.47e-6` |

## 21. Questions possibles et réponses

### Pourquoi commence-t-on par Poisson ?

Parce que c'est le seul modèle simple qui donne une base analytique. Il permet de vérifier la simulation, de tester la loi inverse-gaussienne et de construire une référence avant Hawkes.

### Pourquoi la loi inverse-gaussienne apparaît ?

Parce que la marche de Poisson à grande échelle est approchée par un brownien avec dérive. Le temps d'atteinte d'un seuil par un brownien avec dérive suit une loi inverse-gaussienne.

### Est-ce que le test KS prouve que la loi est correcte ?

Non. Il dit seulement qu'on ne rejette pas l'adéquation au seuil de 5 %. C'est une validation numérique, pas une preuve exacte.

### Pourquoi Hawkes est plus réaliste que Poisson ?

Parce que Hawkes introduit la mémoire. Dans un carnet, les événements ne sont pas indépendants : des retraits peuvent déclencher d'autres retraits, et les effets se dissipent progressivement.

### Pourquoi le Hawkes couplé vide plus vite le carnet ?

Parce qu'il combine mémoire locale et interaction bid/ask. Une pression sur un côté peut modifier l'intensité de l'autre côté, donc les trajectoires extrêmes deviennent plus fréquentes.

### Pourquoi faut-il le deuxième niveau ?

Pour reconstruire le carnet après un saut de prix. Sans deuxième niveau, on peut étudier un seul épuisement, mais pas une séquence de plusieurs mouvements.

### Que représente le couplage du niveau 2 ?

Il représente la réaction de profondeur : quand le premier niveau se dégrade, le modèle augmente les ajouts au deuxième niveau. Cela donne des distributions de `q2` plus élevées.

### Pourquoi le prix est martingale quand `p=1/2` ?

Parce que le saut positif et le saut négatif ont alors la même probabilité. L'espérance du saut vaut zéro.

### Pourquoi Monte Carlo direct échoue ?

Parce que pour une probabilité très petite, il faut énormément de trajectoires pour observer assez d'occurrences. Le coût augmente comme `1/p`.

### Quel rôle joue le cas `p = 0.14` ?

Il sert de benchmark contrôlé pour comparer AMS au Monte Carlo direct. Le résultat intéressant est le gain de budget : même forme de distribution et précision comparable avec moins de trajectoires.

### Qu'est-ce qu'AMS apporte ?

AMS recycle les trajectoires qui ont atteint des paliers intermédiaires. Sur le benchmark modéré, cela économise le budget de simulation. Sur les flash crashes profonds, cela permet aussi d'explorer progressivement un événement vraiment rare.

### Est-ce que AMS biaise le résultat ?

L'algorithme est conçu pour estimer la probabilité de l'événement original en multipliant des probabilités conditionnelles. Le point critique est de bien transporter l'état complet, notamment la mémoire Hawkes.

### Pourquoi `p1^k` est faux pour le flash crash ?

Parce que les cycles ne sont pas indépendants. Après un saut, le carnet a été reconstruit à partir du deuxième niveau et les intensités Hawkes gardent une mémoire.

### Pourquoi IS peut battre AMS dans une expérience ?

Si l'événement n'est pas trop rare et que le changement de mesure est bien choisi, IS peut réduire fortement la variance. Dans l'expérience, `theta=0.30` donne une meilleure variance que AMS.

### Pourquoi IS n'est pas toujours meilleur ?

Parce que si `theta` est mal choisi, les poids explosent ou dégénèrent. Pour les cascades profondes, construire l'événement par niveaux avec AMS est plus robuste.

### Pourquoi `alpha` vaut presque zéro sur Bitcoin ?

Sur des bougies horaires pré-crise, le signal de mémoire auto-excitée est faible ou masqué par l'agrégation. Cela ne veut pas dire que le vrai carnet n'a pas de mémoire, mais que ces données ne l'identifient pas bien.

### Pourquoi ne pas avoir utilisé GameStop ?

Parce que l'épisode est dominé par des facteurs exogènes et les données disponibles sont trop grossières pour calibrer proprement un modèle local de carnet.

### Quelle est la limite principale du projet ?

La limite principale est la simplification des données et du carnet. Le modèle est utile pour comprendre des mécanismes, mais une vraie application marché demanderait du tick-by-tick, plusieurs niveaux et des variables exogènes.

## 22. Formulation finale recommandée

Si on vous demande de résumer le projet en trente secondes :

> On a construit un modèle progressif de carnet d'ordres. Le modèle Poisson donne une référence analytique validée par la loi inverse-gaussienne. Le modèle Hawkes ajoute la mémoire et montre que l'auto-excitation et le couplage bid/ask accélèrent les épuisements. Ensuite, on utilise AMS d'abord comme outil d'économie de budget sur un benchmark modéré, puis comme méthode de splitting pour les flash crashes vraiment rares, avec l'importance sampling comme comparaison. Enfin, on calibre le modèle sur données synthétiques, puis on l'applique prudemment au Bitcoin Black Thursday pour montrer qu'une séquence observée pendant la crise est très rare sous un régime pré-crise calibré.
