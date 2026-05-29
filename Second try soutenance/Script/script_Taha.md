# Script Taha — Soutenance carnet d’ordres

**Présentation : Modélisation stochastique d’un carnet d’ordres**  
**Durée cible pour Taha : environ 13–14 minutes**  
**Slides concernées : 3–5, 9–10, 14–16, 19–21, 23**

---

## Slide 3 — Transition : Construire le modèle

On commence donc par la première partie : construire un modèle de carnet d’ordres.

La stratégie est progressive : on part d’un modèle simple, qu’on comprend analytiquement, puis on ajoute les phénomènes de mémoire et de couplage.

---

## Slide 4 — Point de départ : modèle Poisson indépendant

Le premier modèle est volontairement très simple.

On regarde une seule file, dont le volume évolue comme

$$
q(t)=q_0 + N_t^+ - N_t^-.
$$

Ici, $N_t^+$ représente les arrivées d’ordres qui ajoutent du volume dans la file, et $N_t^-$ représente les annulations ou consommations qui retirent du volume.

Dans le cas Poisson indépendant, les deux processus ont des intensités constantes. La dérive moyenne est donc

$$
\mu = \lambda^+ - \lambda^-.
$$

Dans l’exemple de la slide, on a $\mu=-0{,}8$, donc la file a tendance à se vider.

L’intérêt de ce modèle n’est pas son réalisme, mais le fait qu’il donne une référence analytique.

En limite diffusive, le temps d’atteinte de zéro suit une loi inverse-gaussienne. Cette loi nous donne donc un benchmark pour vérifier que notre simulation fonctionne correctement.

Numériquement, l’espérance théorique vaut $12{,}5$, et la simulation donne $12{,}52$, donc un écart relatif d’environ $0{,}14\%$.

Le test de Kolmogorov-Smirnov donne une p-value de $0{,}097$, donc on ne rejette pas l’ajustement inverse-gaussien.

La conclusion de cette slide est simple : avant de passer à des modèles plus riches, on vérifie que le moteur de simulation reproduit bien un cas où la théorie est connue.

---

## Slide 5 — Probabilité de ruine : référence par quadrature

Une fois qu’on sait modéliser une file, on passe à deux files indépendantes, bid et ask.

La quantité qui nous intéresse est

$$
\mathbb P(\tau_a < \tau_b).
$$

Dans le cadre Poisson diffusif, on peut calculer cette probabilité par conditionnement sur le temps d’épuisement de l’ask :

$$
\mathbb P(\tau_a < \tau_b)
=
\int_0^\infty f_{\tau_a}(t)\bigl(1-F_{\tau_b}(t)\bigr)\,dt.
$$

L’interprétation est naturelle : on fixe un temps $t$ où l’ask s’épuise, puis on demande que le bid ne se soit pas encore épuisé avant ce temps.

Cette intégrale est ensuite calculée par quadrature de Gauss-Legendre. Cela donne une référence déterministe qu’on peut comparer au Monte-Carlo.

La comparaison montre un écart maximal d’environ $0{,}049$, ce qui est du même ordre que l’erreur statistique Monte-Carlo, environ $0{,}044$.

Donc la différence observée est compatible avec la variabilité de simulation.

À ce stade, on a donc deux validations : une validation sur la loi du temps d’atteinte, et une validation sur la probabilité d’ordre entre les deux temps d’atteinte.

Le modèle Poisson nous donne donc une base de validation, mais il ne capture pas les effets de mémoire du carnet. Anass va maintenant expliquer comment on introduit ces effets avec les processus de Hawkes.

---

## Transition après la slide 8

Une fois qu’on a compris l’effet de la mémoire sur les temps d’épuisement, il reste à transformer ces épuisements en mouvements de prix.

---

## Slide 9 — Deuxième limite : reconstruire le carnet

Jusqu’ici, on s’arrêtait au moment où une limite était consommée.

Mais si on veut modéliser plusieurs mouvements de prix successifs, il faut reconstruire le carnet après chaque saut.

Lorsqu’une meilleure limite s’épuise, le niveau 2 devient la nouvelle meilleure limite.

Par exemple, si l’ask s’épuise, on effectue une mise à jour du type

$$
q_{a,1} \leftarrow q_{a,2}(\tau_a).
$$

Dans notre convention de slides, le prix monte de $\delta^p/2$ ; l’important est le signe du saut.

La question devient donc : quelle est la loi de $q_2(\tau)$, le volume disponible au deuxième niveau au moment de l’épuisement ?

On compare deux variantes.

Dans la première, le niveau 2 évolue indépendamment avec une intensité constante. C’est une référence simple.

Dans la deuxième, le niveau 2 est couplé au niveau 1 : les décréments du niveau 1 excitent le rechargement du niveau 2.

La différence est visible dans les histogrammes.

Sans couplage, les volumes moyens au niveau 2 sont autour de $8$.

Avec couplage, ils montent plutôt autour de $10$ ou $11$.

Donc la reconstruction du carnet n’est pas un détail secondaire. Elle influence l’état initial du cycle suivant, et donc toute la dynamique de prix sur plusieurs cycles.

---

## Slide 10 — Passage au prix : dérive induite par l’asymétrie

On peut maintenant passer du modèle de carnet au modèle de prix.

À chaque épuisement, le prix bouge.

Si l’ask s’épuise d’abord, le prix monte.

Si le bid s’épuise d’abord, le prix baisse.

La variation moyenne de prix sur un cycle est donc

$$
\Delta p_0
=
\frac{\delta p}{2}(2p-1),
\qquad
p = \mathbb P(\tau_a<\tau_b).
$$

Cette formule est très utile parce qu’elle relie directement une probabilité d’atteinte à une dérive de prix.

Si $p=1/2$, le prix est une martingale : il n’a pas de dérive moyenne.

Si $p>1/2$, l’ask s’épuise plus souvent en premier, donc le prix a une tendance haussière.

Si $p<1/2$, le bid s’épuise plus souvent en premier, donc le prix a une tendance baissière.

Dans le cas asymétrique testé, on a $\hat p>1/2$, donc le drift observé est positif : environ $0{,}2375$ par cycle.

Il faut être précis : ce n’est pas une validation indépendante. Comme la probabilité de hausse et le drift sont calculés sur les mêmes trajectoires, l’égalité est mécanique à l’arrondi près.

Ce que cette slide vérifie, c’est la cohérence interne de l’implémentation : la règle de saut de prix respecte bien la formule théorique, et l’asymétrie du carnet se traduit dans le signe de la dérive.

À ce stade, on dispose d’un modèle capable de produire des mouvements de prix. La question suivante est : comment estimer des mouvements extrêmes ?

---

## Transition après la slide 13

Avant de passer aux flash crashes, on vérifie que le recyclage AMS ne déforme pas l’état du carnet reconstruit.

---

## Slide 14 — Loi de $Q_2$ : contrôle par Monte-Carlo direct

Cette slide sert de contrôle de budget.

La probabilité de référence est autour de $0{,}14$, ce qui permet une comparaison propre avec le Monte-Carlo direct.

Un risque du splitting est de déformer la distribution des états recyclés.

Or, dans notre modèle, cette distribution est importante, parce que le volume du niveau 2 au moment de l’épuisement devient le nouveau volume au niveau 1.

On compare donc la loi de $Q_{a,2}(\tau_a)$ obtenue de deux manières.

D’un côté, un Monte-Carlo direct avec $10^5$ trajectoires.

De l’autre, un splitting AMS avec $3\times 10^4$ trajectoires.

Les histogrammes obtenus ont la même forme et le même support.

Cela suggère que le recyclage ne déforme pas la loi conditionnelle du volume reconstruit.

Et on obtient ce résultat avec environ trois fois moins de trajectoires, donc à précision comparable pour un budget de simulation plus faible.

Cette validation est importante parce qu’elle montre que l’AMS n’est pas seulement efficace pour estimer une probabilité : il conserve aussi correctement la distribution des états nécessaires pour poursuivre la dynamique.

---

## Slide 15 — Flash crash de profondeur $k$

Une fois ce contrôle fait, on utilise AMS pour les vraies cascades rares.

On définit un flash crash de profondeur $k$ comme une suite de $k$ épuisements successifs du bid avant qu’un épuisement ask ne casse la séquence.

On écrit :

$$
FC_k
=
\{\tau_b^{(1)}<\tau_a,\ldots,\tau_b^{(k)}<\tau_a\}.
$$

La probabilité se décompose naturellement en produit :

$$
\mathbb P(FC_k)
=
\prod_{i=1}^{k} c_i,
$$

avec

$$
c_i
=
\mathbb P(\tau_b^{(i)}<\tau_a \mid FC_{i-1}).
$$

Le point essentiel est que les cycles ne sont pas i.i.d.

Après chaque épuisement, le carnet est reconstruit, les volumes changent, et les intensités Hawkes sont transportées.

Donc on ne peut pas dire que

$$
\mathbb P(FC_k)=p_1^k.
$$

Cette formule serait seulement une référence naïve sans mémoire ni reconstruction.

Dans le régime présenté, on obtient des ordres de grandeur très faibles :

$$
P(FC_1) \simeq 1{,}4\times 10^{-1},
$$

$$
P(FC_5) \simeq 1{,}1\times 10^{-7},
$$

$$
P(FC_8) \simeq 1{,}9\times 10^{-13}.
$$

C’est précisément l’échelle où le Monte-Carlo direct devient impossible, alors que le splitting reste exploitable.

---

## Slide 16 — Splitting en deux phases

La dernière amélioration consiste à rendre le splitting réutilisable.

L’idée est que les premiers niveaux de l’AMS ne dépendent pas forcément de la cible finale.

On peut donc faire une phase hors-ligne : on simule jusqu’à un niveau intermédiaire $k^{\ast}$, puis on stocke la distribution empirique des états survivants.

Cette distribution empirique est simplement un ensemble de particules complètes :

$$
\widehat{\pi}_{k^{\ast}}
=
\left\{s_{k^{\ast}}^{(i)}\right\}_{i=1}^{N}.
$$


Chaque état contient toutes les composantes nécessaires pour reprendre la simulation : volumes, intensités Hawkes, temps, éventuellement prix.

Ensuite, en phase en ligne, on tire des états depuis cette distribution empirique, et on ne simule que les derniers niveaux.

La probabilité est factorisée sous la forme

$$
\widehat P
=
P_{\mathrm{off}}
\times
\widehat P_{\mathrm{on}}.
$$

Le gain est significatif : le splitting complet coûte environ $7{,}69$ secondes par requête, alors qu’avec la méthode en deux phases, ce coût est payé une fois hors-ligne, puis chaque requête coûte seulement $0{,}67$ seconde.

Cela donne un facteur environ $11$.

Et les distributions restent cohérentes : les moyennes comparées sont $12{,}90$ et $12{,}91$.

Le splitting donne donc une méthode robuste et réutilisable. Pour avoir une comparaison indépendante, Anass va maintenant présenter l’importance sampling.

---

## Slide 19 — Transition : Confronter au réel

La dernière partie consiste à tester jusqu’où cette approche peut être reliée à des données réelles.

On commence par une calibration synthétique, puis on regarde le Black Thursday du Bitcoin.

---

## Slide 20 — Calibration synthétique

Avant de calibrer sur des données réelles, on fait une expérience synthétique.

On simule des trajectoires avec des paramètres connus, puis on essaie de retrouver ces paramètres par maximum de vraisemblance.

Les paramètres estimés sont

$$
\mu_a^-,
\quad
\mu_b^-,
\quad
\alpha,
\quad
\beta.
$$

Sur 150 cycles synthétiques, les intensités de fond sont très bien retrouvées.

On obtient

$$
\mu_a^- = 3{,}01
\quad \text{au lieu de} \quad 3{,}0,
$$

et

$$
\mu_b^- = 1{,}50
\quad \text{au lieu de} \quad 1{,}5.
$$

En revanche, les paramètres de mémoire $\alpha$ et $\beta$ sont moins stables.

On a environ $6\%$ d’erreur sur $\alpha$, et $15\%$ sur $\beta$.

Ce n’est pas très surprenant : sur un échantillon court, $\alpha$ et $\beta$ sont corrélés dans la vraisemblance.

Intuitivement, une excitation forte qui décroît vite peut ressembler à une excitation plus faible qui décroît plus lentement.

Donc cette slide donne deux messages.

D’abord, la méthode MLE retrouve bien les intensités de fond.

Ensuite, identifier précisément la mémoire Hawkes demande davantage de données ou des données de plus haute fréquence.

---

## Slide 21 — Bitcoin Black Thursday : données 1h

On applique ensuite cette logique au Bitcoin pendant le Black Thursday du 12 mars 2020.

Ce jour-là, le BTC perd environ $41\%$ en une journée.

On utilise des données Binance en bougies horaires, et on calibre le modèle sur les 1696 observations pré-crise.

Le résultat principal est que le régime pré-crise calibré donne

$$
\widehat \alpha \approx 0.
$$

Autrement dit, dans cette fenêtre pré-crise, le modèle estimé est presque Poisson.

Cela signifie qu’on ne détecte pas une forte mémoire Hawkes avant le crash.

Ensuite, on utilise l’AMS pour estimer la probabilité d’observer une séquence de 5 bougies négatives consécutives comparable à celle du crash, sous ce régime pré-crise.

On obtient environ

$$
8{,}5\times 10^{-6},
$$

soit à peu près une chance sur $118\,000$.

Le message n’est pas que notre modèle prédit parfaitement le Black Thursday.

Au contraire, le message est que sous un régime pré-crise calme, quasi-Poisson, l’événement observé reste extrêmement rare.

Cela illustre une limite classique : un modèle calibré sur une période calme peut sous-estimer fortement le risque de cascade en période de crise.

Cette application au Bitcoin est pertinente pour des cascades endogènes de marché. En revanche, tous les événements extrêmes ne rentrent pas dans ce cadre, comme le montre l’exemple GameStop, qu’Anass va présenter.

---

## Slide 23 — Conclusion, deuxième partie

Troisième message : AMS sert d’abord à réduire le budget de simulation sur un benchmark modéré, puis les événements vraiment rares nécessitent des méthodes spécifiques.

Le Monte-Carlo direct devient inutilisable dès qu’on atteint des probabilités comme $10^{-7}$ ou $10^{-13}$.

L’AMS permet de factoriser l’événement en niveaux, tandis que l’importance sampling fournit une approche complémentaire, très efficace quand le changement de mesure est bien calibré.

Enfin, la calibration sur Bitcoin montre à la fois l’intérêt et les limites du modèle.

Sous le régime pré-crise, le modèle calibré est presque Poisson, et l’événement observé reste extrêmement rare.

Cela suggère qu’un modèle calibré uniquement sur des périodes calmes peut ne pas couvrir correctement les risques de crise.

Les perspectives naturelles sont donc : utiliser des données tick-by-tick, étendre le modèle à plus de niveaux de carnet, et relier les probabilités d’épuisement à des objets de risque de marché, par exemple la volatilité implicite.

Merci pour votre attention, nous sommes maintenant disponibles pour vos questions.

---

## Notes de transitions à retenir

- **Après slide 5** : « Le modèle Poisson nous donne donc une base de validation, mais il ne capture pas les effets de mémoire du carnet. »
- **Après slide 10** : « On a maintenant un modèle de prix issu de la dynamique du carnet. La question suivante est de savoir comment estimer les scénarios extrêmes. »
- **Après slide 16** : « Le splitting donne donc une méthode robuste et réutilisable. Pour avoir une comparaison indépendante, on a aussi étudié l’importance sampling. »
- **Après slide 21** : « Cette application au Bitcoin est pertinente pour des cascades endogènes, mais tous les événements extrêmes ne rentrent pas dans ce cadre. »
