# Script Anass — Soutenance carnet d'ordres

**Présentation : Modélisation stochastique d'un carnet d'ordres**  
**Durée cible pour Anass : environ 13–14 minutes**  
**Slides concernées : 1–3, 7–9, 12–14, 18–19, 23–24**

---

## Slide 1 — Titre

Bonjour à tous, merci d'être présents.

Aujourd'hui, nous allons vous présenter notre travail sur la **modélisation stochastique d'un carnet d'ordres**, avec trois axes principaux.

Le premier axe est la **construction d'un modèle** de carnet d'ordres, en partant d'un modèle simple de files de Poisson, puis en introduisant progressivement de la mémoire avec des processus de Hawkes.

Le deuxième axe est la **simulation efficace**, puis l'**estimation d'événements rares**. On commence par réduire le budget de simulation sur un cas contrôlable, avant de passer aux mouvements extrêmes du prix, comme plusieurs épuisements successifs du bid.

Enfin, le troisième axe est la **confrontation au réel**, avec une calibration sur un épisode de marché extrême : le Black Thursday du Bitcoin en mars 2020.

L'objectif de cette présentation n'est pas de répéter tout le rapport, mais plutôt de raconter le fil mathématique du projet : comment on passe d'un modèle de volumes dans le carnet à une probabilité de crash, puis à une tentative de calibration sur données réelles.

---

## Slide 2 — Qu'est-ce qu'un carnet d'ordres ?

Avant d'entrer dans la modélisation, je vais vous donner une image concrète de l'objet qu'on étudie.

Un carnet d'ordres à cours limité centralise toutes les intentions d'achat et de vente en attente pour un actif donné.

Sur cette figure, l'axe horizontal représente le prix, et la hauteur de chaque barre représente le volume disponible à ce prix.

À gauche du prix central $p_0$, on trouve les ordres d'achat — c'est le côté **bid**, affiché en vert. Ces acheteurs sont prêts à acheter, mais seulement à un prix inférieur ou égal au prix actuel.

À droite de $p_0$, on trouve les ordres de vente — c'est le côté **ask**, en rouge. Ces vendeurs sont prêts à vendre, mais à un prix supérieur ou égal au prix actuel.

La barre la plus proche de $p_0$ de chaque côté s'appelle la **première limite** : c'est la meilleure offre disponible.

Du côté bid, c'est $Q_{-1}$ — le meilleur acheteur.
Du côté ask, c'est $Q_1$ — le meilleur vendeur.

L'écart entre ces deux premières limites s'appelle le **spread**.

Maintenant, que se passe-t-il quand une transaction arrive ?

Un ordre de marché consomme directement la première limite du côté opposé. Si on achète au prix du marché, on ronge les volumes de $Q_1$. Si $Q_1$ s'épuise entièrement, le prix doit sauter à $p_2$, la limite suivante.

C'est exactement ce phénomène d'**épuisement** d'une première limite qui fait bouger les prix dans notre modèle. Et c'est la dynamique de ces files que l'on va maintenant modéliser.

---

## Slide 3 — Le fil conducteur

Le point de départ est le suivant.

À chaque instant, le carnet contient un volume côté vendeur, donc côté ask, noté $q_a$, et un volume côté acheteur, côté bid, noté $q_b$.

Dans un modèle de type Queue Reactive, le prix bouge lorsqu'une des deux meilleures limites est entièrement consommée.

On se ramène donc à deux temps d'atteinte :

$$
\tau_a = \inf\{t : q_{a,1}(t)=0\},
\qquad
\tau_b = \inf\{t : q_{b,1}(t)=0\}.
$$

Si l'ask s'épuise d'abord, cela correspond à une pression acheteuse, donc à un mouvement de prix vers le haut.

Si le bid s'épuise d'abord, cela correspond à une pression vendeuse, donc à un mouvement de prix vers le bas.

Toute la présentation repose donc sur trois questions.

D'abord : **comment modéliser correctement ces deux files ?**

Ensuite : **comment estimer efficacement des probabilités d'atteinte, surtout quand elles deviennent très petites ?**

Enfin : **jusqu'où ce modèle peut-il expliquer ou interpréter un vrai épisode extrême de marché ?**

Pour construire ce modèle, on commence volontairement par un cas simple, le modèle Poisson, qui servira de référence analytique. Taha va présenter cette première étape.

---

## Transition après la slide 6

Le modèle Poisson nous donne donc une base de validation, mais il ne capture pas les effets de mémoire du carnet. Je vais maintenant expliquer comment on introduit ces effets avec les processus de Hawkes.

---

## Slide 7 — Processus de Hawkes : mémoire et troncature

Le modèle Poisson est une bonne référence, mais il manque un phénomène essentiel : dans un vrai carnet d'ordres, les événements ne sont pas indépendants dans le temps.

On observe souvent des clusters : une annulation peut être suivie d'autres annulations, et une arrivée d'ordre peut stabiliser temporairement la file.

Pour capturer cela, on introduit un processus de Hawkes.

L'intensité d'annulation devient dépendante du passé :

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

Le premier, $\mu^-$, est l'intensité de fond.

Le deuxième terme correspond à l'auto-excitation : une annulation passée augmente l'intensité d'annulation future.

Le troisième terme correspond à l'inhibition : une insertion passée diminue l'intensité d'annulation.

Le paramètre $\alpha$ mesure l'amplitude de la mémoire, tandis que $\beta$ mesure la vitesse d'oubli.

Un point numérique important apparaît ici : à cause du terme d'inhibition, l'intensité pourrait devenir négative. Or une intensité négative n'a pas de sens. On impose donc un plancher à zéro, avec une mise à jour du type :

$$
\lambda^- \leftarrow \max(\lambda^-_{\text{pre}}-\alpha,0).
$$

Ce choix est nécessaire pour simuler le modèle, mais il modifie légèrement le bilan de flux théorique.

C'est ce qu'on observe dans les résultats : sans troncature, la théorie stationnaire donne une moyenne de $2{,}80$, alors que la simulation donne $2{,}96$, soit environ $5{,}9\%$ de plus.

Ce point est important : on ne prend pas les formules théoriques comme des boîtes noires. On vérifie l'effet des choix numériques sur la dynamique simulée.

---

## Slide 8 — Hawkes couplé : effet du couplage bid/ask

L'étape suivante consiste à coupler les deux côtés du carnet.

Jusqu'ici, le bid et l'ask pouvaient évoluer presque indépendamment. Mais en réalité, une forte activité d'un côté du carnet peut influencer l'autre côté.

On introduit donc une intensité d'annulation côté ask qui dépend aussi des événements côté bid :

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

Le dernier terme est le couplage croisé : les événements du bid excitent aussi l'intensité d'annulation côté ask.

Ce couplage introduit un mécanisme de cascade : un côté du carnet devient instable, et cette instabilité peut se propager à l'autre côté.

Le résultat numérique est parlant. Au point initial $q_0=(10,10)$, le temps moyen du premier épuisement passe de $8{,}3$ dans le modèle Poisson à $5{,}8$ dans le modèle Hawkes couplé.

Cela représente une réduction d'environ $30\%$.

Donc le couplage ne change pas seulement quelques paramètres : il accélère réellement l'épuisement conjoint des deux côtés du carnet.

---

## Slide 9 — Quatre régimes : effet progressif de la mémoire

Cette slide résume l'effet progressif des différents ingrédients du modèle.

On compare quatre régimes.

Dans le modèle Poisson individuel, le temps moyen est environ $12{,}4$.

Si on prend le minimum de deux files de Poisson, la moyenne descend à $8{,}6$, ce qui est attendu puisqu'on regarde le premier de deux événements.

Avec Hawkes individuel, on obtient une moyenne de $8{,}8$. La mémoire crée des clusters d'événements et modifie la distribution.

Enfin, avec Hawkes couplé, la moyenne descend à $5{,}9$.

On voit donc trois effets qui se cumulent : le minimum de deux files, l'auto-excitation, et le couplage bid/ask.

Mais le message le plus important est que la mémoire ne modifie pas seulement la moyenne. Elle modifie aussi la forme de la loi, notamment la queue gauche.

Autrement dit, les épuisements très rapides deviennent beaucoup plus probables.

C'est exactement ce qui motive ensuite le besoin de méthodes de simulation plus efficaces.

Une fois qu'on a compris l'effet de la mémoire sur les temps d'épuisement, il reste à transformer ces épuisements en mouvements de prix. C'est l'objet des deux slides suivantes, que Taha va présenter.

---

## Slide 12 — Transition : simuler les régimes extrêmes

On passe donc à la deuxième partie.

Avant de s'intéresser aux cascades vraiment rares, on commence par une question plus pratique : comment réduire le coût de simulation ?

Pour ça, on utilise un cas de contrôle avec une probabilité autour de $0{,}14$.

Ce cas est utile parce qu'on peut encore le comparer au Monte-Carlo direct. On peut donc vérifier que l'AMS donne la même loi et une précision comparable, mais avec moins de simulations.

Une fois cette étape validée, on utilise la même logique pour les vrais régimes extrêmes, comme les flash crashes à plusieurs niveaux.

---

## Slide 13 — Réduire le coût de simulation

Cette slide introduit AMS comme outil de réduction du coût de simulation.

Le cas de contrôle a une probabilité autour de $0{,}14$, donc le Monte-Carlo direct est encore possible et sert de référence.

Le Monte-Carlo direct relance toutes les trajectoires depuis zéro. Son erreur décroît comme

$$
\frac{1}{\sqrt M}.
$$

Donc pour gagner un facteur deux en précision, il faut environ quatre fois plus de trajectoires.

L'idée de l'AMS est d'économiser ce budget en recyclant les trajectoires qui ont déjà atteint des paliers intermédiaires.

Dans notre contrôle sur $Q_2(\tau)$, on compare :

- un Monte-Carlo direct avec $10^5$ trajectoires ;
- un splitting AMS avec $3\times 10^4$ trajectoires.

Les distributions obtenues ont la même forme et le même support.

Le résultat est donc : à précision comparable, on réduit le nombre de simulations.

Après cette validation, on applique la même logique aux probabilités rares.

---

## Slide 14 — Splitting AMS : recycler les trajectoires

La première méthode utilisée est le splitting, dans l'esprit de l'AMS.

L'idée est d'éviter de gaspiller des trajectoires déjà informatives.

Au lieu de relancer tout depuis zéro, on introduit des niveaux intermédiaires.

Par exemple, si le bid commence à $12$, on regarde successivement l'atteinte de $11$, puis $10$, puis $9$, et ainsi de suite.

À chaque niveau, les trajectoires qui ont réussi sont conservées, rééchantillonnées, puis prolongées.

Cela évite de repartir de zéro à chaque fois.

Le point important dans notre modèle est que l'état transporté n'est pas seulement le volume.

Il faut transporter l'état Hawkes complet : les volumes, les intensités courantes, le temps, et éventuellement les variables nécessaires pour reconstruire le carnet.

Sinon, on casserait la mémoire du processus, et le splitting ne simulerait plus le bon modèle.

Mathématiquement, l'estimateur a la forme

$$
\widehat P_{AMS}
=
\prod_k \widehat p_k.
$$

La validation statistique est donnée par la figure : l'écart-type décroît comme une droite de pente environ $-1/2$ en échelle log-log.

C'est le comportement attendu en $1/\sqrt N$, ce qui valide empiriquement la convergence de la méthode.

Ici, le cas de contrôle autour de $0{,}14$ sert à vérifier la méthode et le gain de budget.

Taha va maintenant présenter le contrôle de la loi reconstruite avec AMS, puis l'application aux flash crashes.

---

## Transition après la slide 17

Le splitting donne donc une méthode robuste et réutilisable. Pour avoir une comparaison indépendante, on a aussi étudié l'importance sampling.

---

## Slide 18 — Importance Sampling : mesure et poids

L'importance sampling repose sur une idée différente du splitting.

Dans le splitting, on garde la loi de simulation, mais on décompose l'événement en niveaux.

Dans l'importance sampling, on change directement la loi simulée pour rendre l'événement rare plus fréquent, puis on corrige par un poids de vraisemblance.

Dans notre cas, on introduit un paramètre $\theta$, qui tord les intensités.

Pour favoriser l'événement où le bid s'épuise avant l'ask, on augmente l'intensité effective côté bid et on diminue celle côté ask.

On simule donc sous une nouvelle mesure, puis on multiplie par un poids $L$ pour retrouver une estimation sous la vraie mesure.

L'estimateur s'écrit

$$
\widehat p_{IS}
=
\frac{1}{N}
\sum_i L_i \mathbf 1_{\tau_b<\tau_a}.
$$

Le choix de $\theta$ est crucial.

Si $\theta$ est trop faible, l'événement reste rare et on n'a presque rien gagné.

Si $\theta$ est trop grand, on force trop les trajectoires, et les poids deviennent instables.

Dans nos expériences, le meilleur compromis est autour de

$$
\theta^{\ast} \approx 0{,}30.
$$

Au-delà de $0{,}6$, le coefficient de variation devient très grand, ce qui signifie que l'estimateur est dominé par quelques trajectoires avec des poids énormes.

Un point de vigilance apparaît aussi pour $\theta = 2{,}1$ : le coefficient de variation peut sembler baisser alors que l'estimation s'effondre.

Donc il ne faut pas regarder uniquement la dispersion des poids. Il faut regarder simultanément la probabilité estimée et la stabilité des poids.

---

## Slide 19 — Comparaison AMS / IS à $N$ fixé

On compare ensuite les deux méthodes à nombre de trajectoires fixé.

Pour l'événement modéré testé ici, l'importance sampling bien réglé donne une variance plus faible que l'AMS.

La réduction d'erreur relative est environ $0{,}57$, ce qui correspond à une variance plus faible d'environ $43\%$.

Mais cette conclusion doit être interprétée avec prudence.

Pour des événements modérés, si le changement de mesure est bien choisi, l'IS peut être très efficace.

En revanche, pour des cascades plus profondes, l'AMS devient souvent plus robuste, parce qu'il exploite directement la structure par niveaux de l'événement.

Donc les deux méthodes sont complémentaires.

L'AMS est plus géométrique et plus naturel pour des événements de type « atteindre successivement plusieurs seuils ».

L'IS est plus direct, parfois plus efficace, mais plus sensible au choix de la mesure de simulation.

Cela termine la partie méthodes : économie de budget avec AMS, puis événements rares et comparaison avec IS. On passe maintenant à la confrontation au réel, que Taha va présenter.

---

## Transition après la slide 22

Cette application au Bitcoin est pertinente pour des cascades endogènes de marché. En revanche, tous les événements extrêmes ne rentrent pas dans ce cadre, comme le montre l'exemple GameStop.

---

## Slide 23 — GameStop : limite du cadre de modélisation

Nous avons aussi testé la même procédure sur l'épisode GameStop de janvier 2021, mais nous avons choisi de ne pas en faire un résultat principal.

Il y a deux raisons.

La première est statistique : en données journalières, on dispose d'environ 70 observations, ce qui est trop peu pour stabiliser une calibration Hawkes.

La deuxième raison est plus fondamentale : le mécanisme de GameStop est en grande partie exogène au carnet.

Il repose notamment sur une coordination d'investisseurs via Reddit, donc sur un facteur externe que notre modèle ne représente pas.

Notre modèle est adapté à des cascades endogènes de liquidité : des mouvements qui émergent de l'interaction entre les volumes, les annulations et la mémoire du carnet.

Il est beaucoup moins adapté à un événement dont le moteur principal vient d'une coordination extérieure.

Cette comparaison permet donc de clarifier le domaine de validité du modèle.

On peut l'utiliser pour étudier des cascades internes au marché, mais pas pour expliquer tous les événements extrêmes indistinctement.

---

## Slide 24 — Conclusion, première partie

Pour conclure, on retient trois messages.

Premier message : la mémoire Hawkes modifie fortement la dynamique du carnet.

Elle réduit les temps d'épuisement, elle augmente la probabilité d'épuisements rapides, et elle change la forme complète de la loi, pas seulement sa moyenne.

Deuxième message : le couplage bid/ask est essentiel pour faire apparaître des mécanismes de cascade.

Dans le modèle couplé, l'instabilité d'un côté peut accélérer l'épuisement de l'autre côté, ce qui rapproche le modèle de phénomènes extrêmes observés en marché.

Je laisse Taha terminer sur les méthodes de simulation, les événements rares et les perspectives.

---

## Notes de transitions à retenir

- **Après slide 3** : « Pour construire ce modèle, on commence volontairement par un cas simple, le modèle Poisson, qui servira de référence analytique. Taha va présenter cette première étape. »
- **Après slide 9** : « Une fois qu'on a compris l'effet de la mémoire sur les temps d'épuisement, il reste à transformer ces épuisements en mouvements de prix. »
- **Après slide 14** : « L'AMS devient particulièrement naturel lorsqu'on définit un flash crash comme une succession d'épuisements du bid. »
- **Après slide 19** : « Après l'économie de budget avec AMS et la comparaison avec IS, on passe à la dernière étape : la calibration. »
