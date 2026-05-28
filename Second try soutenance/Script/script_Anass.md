# Script Anass — Soutenance carnet d’ordres

**Présentation : Modélisation stochastique d’un carnet d’ordres**  
**Durée cible pour Anass : environ 13–14 minutes**  
**Slides concernées : 1–2, 6–8, 11–13, 17–18, 22–23**

---

## Slide 1 — Titre

Bonjour à tous, merci d’être présents.

Aujourd’hui, nous allons vous présenter notre travail sur la **modélisation stochastique d’un carnet d’ordres**, avec trois axes principaux.

Le premier axe est la **construction d’un modèle** de carnet d’ordres, en partant d’un modèle simple de files de Poisson, puis en introduisant progressivement de la mémoire avec des processus de Hawkes.

Le deuxième axe est l’**estimation d’événements rares**. En particulier, on veut estimer la probabilité de mouvements extrêmes du prix, comme plusieurs épuisements successifs du bid.

Enfin, le troisième axe est la **confrontation au réel**, avec une calibration sur un épisode de marché extrême : le Black Thursday du Bitcoin en mars 2020.

L’objectif de cette présentation n’est pas de répéter tout le rapport, mais plutôt de raconter le fil mathématique du projet : comment on passe d’un modèle de volumes dans le carnet à une probabilité de crash, puis à une tentative de calibration sur données réelles.

---

## Slide 2 — Le fil conducteur

Le point de départ est le suivant.

À chaque instant, le carnet contient un volume côté vendeur, donc côté ask, noté $q_a$, et un volume côté acheteur, côté bid, noté $q_b$.

Dans un modèle de type Queue Reactive, le prix bouge lorsqu’une des deux meilleures limites est entièrement consommée.

On se ramène donc à deux temps d’atteinte :

$$
\tau_a = \inf\{t : q_{a,1}(t)=0\},
\qquad
\tau_b = \inf\{t : q_{b,1}(t)=0\}.
$$

Si l’ask s’épuise d’abord, cela correspond à une pression acheteuse, donc à un mouvement de prix vers le haut.

Si le bid s’épuise d’abord, cela correspond à une pression vendeuse, donc à un mouvement de prix vers le bas.

Toute la présentation repose donc sur trois questions.

D’abord : **comment modéliser correctement ces deux files ?**

Ensuite : **comment estimer efficacement des probabilités d’atteinte, surtout quand elles deviennent très petites ?**

Enfin : **jusqu’où ce modèle peut-il expliquer ou interpréter un vrai épisode extrême de marché ?**

Pour construire ce modèle, on commence volontairement par un cas simple, le modèle Poisson, qui servira de référence analytique. Taha va présenter cette première étape.

---

## Transition après la slide 5

Le modèle Poisson nous donne donc une base de validation, mais il ne capture pas les effets de mémoire du carnet. Je vais maintenant expliquer comment on introduit ces effets avec les processus de Hawkes.

---

## Slide 6 — Processus de Hawkes : mémoire et troncature

Le modèle Poisson est une bonne référence, mais il manque un phénomène essentiel : dans un vrai carnet d’ordres, les événements ne sont pas indépendants dans le temps.

On observe souvent des clusters : une annulation peut être suivie d’autres annulations, et une arrivée d’ordre peut stabiliser temporairement la file.

Pour capturer cela, on introduit un processus de Hawkes.

L’intensité d’annulation devient dépendante du passé :

$$
\lambda^-(t)
=
\mu^-
+
\alpha \sum_{s\in N^-,\,s<t} e^{-\beta(t-s)}
-
\alpha \sum_{s\in N^+,\,s<t} e^{-\beta(t-s)}.
$$

Il y a trois termes.

Le premier, $\mu^-$, est l’intensité de fond.

Le deuxième terme correspond à l’auto-excitation : une annulation passée augmente l’intensité d’annulation future.

Le troisième terme correspond à l’inhibition : une insertion passée diminue l’intensité d’annulation.

Le paramètre $\alpha$ mesure l’amplitude de la mémoire, tandis que $\beta$ mesure la vitesse d’oubli.

Un point numérique important apparaît ici : à cause du terme d’inhibition, l’intensité pourrait devenir négative. Or une intensité négative n’a pas de sens. On impose donc un plancher à zéro, avec une mise à jour du type :

$$
\lambda^- \leftarrow \max(\lambda^-_{\text{pre}}-\alpha,0).
$$

Ce choix est nécessaire pour simuler le modèle, mais il modifie légèrement le bilan de flux théorique.

C’est ce qu’on observe dans les résultats : sans troncature, la théorie stationnaire donne une moyenne de $2{,}80$, alors que la simulation donne $2{,}96$, soit environ $5{,}9\%$ de plus.

Ce point est important : on ne prend pas les formules théoriques comme des boîtes noires. On vérifie l’effet des choix numériques sur la dynamique simulée.

---

## Slide 7 — Hawkes couplé : effet du couplage bid/ask

L’étape suivante consiste à coupler les deux côtés du carnet.

Jusqu’ici, le bid et l’ask pouvaient évoluer presque indépendamment. Mais en réalité, une forte activité d’un côté du carnet peut influencer l’autre côté.

On introduit donc une intensité d’annulation côté ask qui dépend aussi des événements côté bid :

$$
\lambda_a^-(t)
=
\mu_a^-
+
\alpha \sum_{s\in D_a} e^{-\beta(t-s)}
-
\alpha \sum_{s\in A_a} e^{-\beta(t-s)}
+
\alpha \sum_{s\in C_b} e^{-\beta(t-s)}.
$$

Les deux premiers termes sont internes au côté ask : les décréments excitent, les incréments inhibent.

Le dernier terme est le couplage croisé : les événements du bid excitent aussi l’intensité d’annulation côté ask.

Ce couplage introduit un mécanisme de cascade : un côté du carnet devient instable, et cette instabilité peut se propager à l’autre côté.

Le résultat numérique est parlant. Au point initial $q_0=(10,10)$, le temps moyen du premier épuisement passe de $8{,}3$ dans le modèle Poisson à $5{,}8$ dans le modèle Hawkes couplé.

Cela représente une réduction d’environ $30\%$.

Donc le couplage ne change pas seulement quelques paramètres : il accélère réellement l’épuisement conjoint des deux côtés du carnet.

---

## Slide 8 — Quatre régimes : effet progressif de la mémoire

Cette slide résume l’effet progressif des différents ingrédients du modèle.

On compare quatre régimes.

Dans le modèle Poisson individuel, le temps moyen est environ $12{,}4$.

Si on prend le minimum de deux files de Poisson, la moyenne descend à $8{,}6$, ce qui est attendu puisqu’on regarde le premier de deux événements.

Avec Hawkes individuel, on obtient une moyenne de $8{,}8$. La mémoire crée des clusters d’événements et modifie la distribution.

Enfin, avec Hawkes couplé, la moyenne descend à $5{,}9$.

On voit donc trois effets qui se cumulent : le minimum de deux files, l’auto-excitation, et le couplage bid/ask.

Mais le message le plus important est que la mémoire ne modifie pas seulement la moyenne. Elle modifie aussi la forme de la loi, notamment la queue gauche.

Autrement dit, les épuisements très rapides deviennent beaucoup plus probables.

C’est exactement ce qui motive ensuite l’étude des événements rares.

Une fois qu’on a compris l’effet de la mémoire sur les temps d’épuisement, il reste à transformer ces épuisements en mouvements de prix. C’est l’objet des deux slides suivantes, que Taha va présenter.

---

## Slide 11 — Transition : Estimer l’improbable

On passe donc à la deuxième partie : l’estimation des événements rares.

Le point central est que le Monte-Carlo direct devient rapidement inutilisable lorsque les probabilités deviennent très petites.

---

## Slide 12 — Limite du Monte-Carlo direct

Le Monte-Carlo direct consiste à simuler beaucoup de trajectoires, puis à compter la proportion de trajectoires où l’événement rare a lieu.

Si l’événement a une probabilité $p$, l’erreur relative se comporte comme

$$
\sqrt{\frac{1-p}{Mp}}.
$$

Donc quand $p$ devient très petit, l’erreur relative explose, sauf si le nombre de trajectoires $M$ devient énorme.

Dans notre cas, les probabilités cibles peuvent être de l’ordre de $10^{-7}$ à $10^{-13}$.

Pour obtenir une précision relative raisonnable, par exemple autour de $10\%$, il faudrait entre $10^9$ et $10^{15}$ trajectoires.

C’est totalement irréaliste.

L’événement rare qui nous intéresse est l’épuisement du bid alors qu’il est initialement plus profond et moins fragile.

Intuitivement, cela représente une baisse brutale du prix dans une situation où, au départ, le bid semblait pourtant robuste.

Donc on ne cherche pas seulement à simuler un mouvement de prix. On cherche à estimer un scénario extrême relativement à l’état initial du carnet.

---

## Slide 13 — Splitting AMS : factoriser un événement rare

La première méthode utilisée est le splitting, dans l’esprit de l’AMS.

L’idée est de remplacer une probabilité minuscule par un produit de probabilités conditionnelles plus grandes.

Au lieu de demander directement : quelle est la probabilité que le bid arrive à zéro avant l’ask ?

On introduit des niveaux intermédiaires.

Par exemple, si le bid commence à $12$, on regarde successivement la probabilité d’atteindre $11$, puis $10$, puis $9$, et ainsi de suite jusqu’à zéro, sans que l’ask s’épuise avant.

À chaque niveau, les trajectoires qui ont réussi sont conservées, rééchantillonnées, puis prolongées.

Cela évite de repartir de zéro à chaque fois.

Le point important dans notre modèle est que l’état transporté n’est pas seulement le volume.

Il faut transporter l’état Hawkes complet : les volumes, les intensités courantes, le temps, et éventuellement les variables nécessaires pour reconstruire le carnet.

Sinon, on casserait la mémoire du processus, et le splitting ne simulerait plus le bon modèle.

Mathématiquement, l’estimateur a la forme

$$
\widehat P_{AMS}
=
\prod_k \widehat p_k.
$$

La validation statistique est donnée par la figure : l’écart-type décroît comme une droite de pente environ $-1/2$ en échelle log-log.

C’est le comportement attendu en $1/\sqrt N$, ce qui valide empiriquement la convergence de la méthode.

L’AMS devient particulièrement naturel lorsqu’on définit un flash crash comme une succession d’épuisements du bid. Taha va maintenant présenter cette application.

---

## Transition après la slide 16

Le splitting donne donc une méthode robuste et réutilisable. Pour avoir une comparaison indépendante, on a aussi étudié l’importance sampling.

---

## Slide 17 — Importance Sampling : mesure et poids

L’importance sampling repose sur une idée différente du splitting.

Dans le splitting, on garde la loi de simulation, mais on décompose l’événement en niveaux.

Dans l’importance sampling, on change directement la loi simulée pour rendre l’événement rare plus fréquent, puis on corrige par un poids de vraisemblance.

Dans notre cas, on introduit un paramètre $\theta$, qui tord les intensités.

Pour favoriser l’événement où le bid s’épuise avant l’ask, on augmente l’intensité effective côté bid et on diminue celle côté ask.

On simule donc sous une nouvelle mesure, puis on multiplie par un poids $L$ pour retrouver une estimation sous la vraie mesure.

L’estimateur s’écrit

$$
\widehat p_{IS}
=
\frac{1}{N}
\sum_i L_i \mathbf 1_{\tau_b<\tau_a}.
$$

Le choix de $\theta$ est crucial.

Si $\theta$ est trop faible, l’événement reste rare et on n’a presque rien gagné.

Si $\theta$ est trop grand, on force trop les trajectoires, et les poids deviennent instables.

Dans nos expériences, le meilleur compromis est autour de

$$
\theta^\* \approx 0{,}30.
$$

Au-delà de $0{,}6$, le coefficient de variation devient très grand, ce qui signifie que l’estimateur est dominé par quelques trajectoires avec des poids énormes.

Un point de vigilance apparaît aussi pour $\theta = 2{,}1$ : le coefficient de variation peut sembler baisser alors que l’estimation s’effondre.

Donc il ne faut pas regarder uniquement la dispersion des poids. Il faut regarder simultanément la probabilité estimée et la stabilité des poids.

---

## Slide 18 — Comparaison AMS / IS à $N$ fixé

On compare ensuite les deux méthodes à nombre de trajectoires fixé.

Pour l’événement modéré testé ici, l’importance sampling bien réglé donne une variance plus faible que l’AMS.

La réduction d’erreur relative est environ $0{,}57$, ce qui correspond à une variance plus faible d’environ $43\%$.

Mais cette conclusion doit être interprétée avec prudence.

Pour des événements modérés, si le changement de mesure est bien choisi, l’IS peut être très efficace.

En revanche, pour des cascades plus profondes, l’AMS devient souvent plus robuste, parce qu’il exploite directement la structure par niveaux de l’événement.

Donc les deux méthodes sont complémentaires.

L’AMS est plus géométrique et plus naturel pour des événements de type « atteindre successivement plusieurs seuils ».

L’IS est plus direct, parfois plus efficace, mais plus sensible au choix de la mesure de simulation.

Cela termine la partie méthodes rares. On passe maintenant à la confrontation au réel, que Taha va présenter.

---

## Transition après la slide 21

Cette application au Bitcoin est pertinente pour des cascades endogènes de marché. En revanche, tous les événements extrêmes ne rentrent pas dans ce cadre, comme le montre l’exemple GameStop.

---

## Slide 22 — GameStop : limite du cadre de modélisation

Nous avons aussi testé la même procédure sur l’épisode GameStop de janvier 2021, mais nous avons choisi de ne pas en faire un résultat principal.

Il y a deux raisons.

La première est statistique : en données journalières, on dispose d’environ 70 observations, ce qui est trop peu pour stabiliser une calibration Hawkes.

La deuxième raison est plus fondamentale : le mécanisme de GameStop est en grande partie exogène au carnet.

Il repose notamment sur une coordination d’investisseurs via Reddit, donc sur un facteur externe que notre modèle ne représente pas.

Notre modèle est adapté à des cascades endogènes de liquidité : des mouvements qui émergent de l’interaction entre les volumes, les annulations et la mémoire du carnet.

Il est beaucoup moins adapté à un événement dont le moteur principal vient d’une coordination extérieure.

Cette comparaison permet donc de clarifier le domaine de validité du modèle.

On peut l’utiliser pour étudier des cascades internes au marché, mais pas pour expliquer tous les événements extrêmes indistinctement.

---

## Slide 23 — Conclusion, première partie

Pour conclure, on retient trois messages.

Premier message : la mémoire Hawkes modifie fortement la dynamique du carnet.

Elle réduit les temps d’épuisement, elle augmente la probabilité d’épuisements rapides, et elle change la forme complète de la loi, pas seulement sa moyenne.

Deuxième message : le couplage bid/ask est essentiel pour faire apparaître des mécanismes de cascade.

Dans le modèle couplé, l’instabilité d’un côté peut accélérer l’épuisement de l’autre côté, ce qui rapproche le modèle de phénomènes extrêmes observés en marché.

Je laisse Taha terminer sur les méthodes d’événements rares et les perspectives.

---

## Notes de transitions à retenir

- **Après slide 2** : « Pour construire ce modèle, on commence volontairement par un cas simple, le modèle Poisson, qui servira de référence analytique. Taha va présenter cette première étape. »
- **Après slide 8** : « Une fois qu’on a compris l’effet de la mémoire sur les temps d’épuisement, il reste à transformer ces épuisements en mouvements de prix. »
- **Après slide 13** : « L’AMS devient particulièrement naturel lorsqu’on définit un flash crash comme une succession d’épuisements du bid. »
- **Après slide 18** : « Après ces deux méthodes d’événements rares, on passe à la dernière étape : la calibration. »
