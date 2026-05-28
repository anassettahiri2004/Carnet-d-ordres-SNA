# Script de soutenance - Modélisation stochastique d'un carnet d'ordres

**Durée cible : 25 minutes.**  
Objectif : ne pas relire le rapport, mais expliquer le cheminement, les validations numériques et les limites du modèle.

---

## Slide 1 - Titre [0:00 -> 0:30]

Bonjour. Nous allons présenter notre travail sur la modélisation stochastique d'un carnet d'ordres. L'idée générale est simple : partir d'un modèle minimal où l'on sait tout vérifier, puis ajouter progressivement la mémoire, le couplage entre bid et ask, les événements rares, et enfin une calibration sur données réelles.

## Slide 2 - Le fil conducteur [0:30 -> 1:45]

Dans un carnet d'ordres, on suit les volumes disponibles au meilleur bid et au meilleur ask. Dans le cadre Queue Reactive du sujet, le prix change lorsque la meilleure limite d'un côté est consommée. Le problème se ramène donc aux deux temps d'atteinte affichés ici : tau-a pour l'ask, tau-b pour le bid.

La question principale est : quel côté touche zéro en premier, à quel horizon, et avec quelle probabilité ? Nous avons organisé le travail en trois parties. D'abord construire le modèle, du Poisson au Hawkes couplé. Ensuite estimer des probabilités très petites, où le Monte-Carlo direct n'est plus utilisable. Enfin tester la calibration, d'abord sur données simulées puis sur Bitcoin autour du Black Thursday.

## Slide 3 - Partie I [1:45 -> 1:55]

Première partie : on construit le modèle couche par couche, en gardant à chaque étape une vérification numérique.

## Slide 4 - Point de départ Poisson [1:55 -> 3:25]

On commence avec le cas le plus simple : une file est une différence de deux processus de Poisson, insertions moins annulations. Avec les paramètres du projet, le drift est négatif, donc la file finit par s'épuiser.

L'intérêt de ce cas n'est pas qu'il soit réaliste, mais qu'il donne une référence. La limite diffusive donne une loi inverse-gaussienne pour le temps d'atteinte de zéro, avec une espérance théorique de 12,5. Dans le notebook, la simulation donne 12,52, soit 0,14 % d'écart, et le test de Kolmogorov-Smirnov donne une p-value de 0,0971.

Comme cette p-value est supérieure à 5 %, on ne rejette pas l'adéquation à la loi inverse-gaussienne. C'est un bon résultat pour nous : cela ne prouve pas que la loi est exactement IG, mais cela signifie que l'écart entre la simulation et la référence théorique n'est pas statistiquement significatif au seuil de 5 %. On a donc un premier contrôle : la simulation reproduit correctement le cas où la théorie est connue.

## Slide 5 - Probabilité de ruine [3:25 -> 4:35]

À deux files indépendantes, on veut calculer la probabilité que l'ask s'épuise avant le bid. En conditionnant sur tau-a, on obtient l'intégrale de la densité de tau-a multipliée par la fonction de survie de tau-b.

Nous l'évaluons par quadrature de Gauss-Legendre. La figure compare cette référence au Monte-Carlo sur une grille de conditions initiales. L'écart maximal est de 0,049, du même ordre que l'erreur statistique du Monte-Carlo. Donc la différence visible sur la figure est essentiellement de la variabilité de simulation, pas un biais du calcul par quadrature.

## Slide 6 - Hawkes et troncature [4:35 -> 6:05]

Ensuite on ajoute la mémoire avec un processus de Hawkes. Une annulation augmente temporairement l'intensité d'annulation ; une insertion l'inhibe. C'est le premier mécanisme qui permet d'avoir des épisodes rapides d'épuisement.

Il y a toutefois un point numérique important. La théorie stationnaire, sans troncature, donne une intensité moyenne de 2,80. La simulation donne environ 2,96, donc presque 6 % de plus. Nous avons identifié la cause : dans le simulateur, l'intensité est tronquée à zéro quand l'inhibition la ferait devenir négative. Ce plancher casse le bilan de flux théorique. Ce n'est pas une erreur à cacher, c'est une limite de la convention de simulation qu'il faut garder en tête.

## Slide 7 - Hawkes couplé [6:05 -> 7:25]

On couple ensuite les deux côtés du carnet. Chaque côté garde sa dynamique propre, mais il reçoit aussi une excitation provenant des événements de l'autre côté. Cette étape est importante parce qu'elle transforme deux files presque séparées en un système où l'activité d'un côté peut accélérer l'autre.

L'effet est net : au point initial 10-10, le temps moyen du premier épuisement passe d'environ 8,3 dans le modèle Poisson à 5,8 dans le modèle Hawkes couplé. Ce que l'on retient, c'est que le couplage réduit fortement les temps d'épuisement et introduit un mécanisme de cascade.

## Slide 8 - Quatre régimes [7:25 -> 8:35]

Cette slide résume la première série d'expériences. Le Poisson individuel donne un temps moyen autour de 12,4. Si l'on prend le minimum de deux files Poisson, on descend déjà à 8,6 par effet combinatoire. Le Hawkes individuel donne 8,8, mais avec une loi plus asymétrique. Le Hawkes couplé descend à 5,9.

La moyenne ne raconte donc pas toute l'histoire. La mémoire modifie aussi la forme de la loi, notamment la masse des épuisements rapides. C'est ce point qui rend nécessaire la deuxième partie sur les événements rares.

## Slide 9 - Deuxième limite [8:35 -> 9:45]

Quand la meilleure limite se vide, la deuxième limite devient la nouvelle meilleure limite. Son volume au temps d'épuisement, noté ici Q2, devient donc l'état initial du cycle suivant.

Nous estimons sa loi conditionnelle selon le côté qui s'épuise. Dans le cas de base, les moyennes sont proches de 7,7 côté ask et 7,5 côté bid. Dans la variante où Q2 est aussi excitée par les événements de la première limite, la distribution se déplace vers des volumes plus élevés. Cela montre que le passage d'un cycle au suivant ne peut pas être résumé par une seule constante.

## Slide 10 - Passage au prix [9:45 -> 10:55]

On passe ensuite au prix en enchaînant les cycles. À chaque épuisement, le mid-price saute d'un demi-tick vers le haut ou vers le bas. Les intensités Hawkes sont transportées d'un cycle au suivant, ce qui conserve la mémoire du carnet.

Dans ce cadre, la dérive moyenne par cycle dépend de p, la probabilité que l'ask s'épuise avant le bid. En régime symétrique, p vaut un demi et le prix est une martingale. En régime asymétrique, le rapport prédit une dérive de 0,238 par cycle, et la simulation mesure 0,2375. C'est une validation utile : le signe et l'ordre de grandeur de la dérive observée reflètent bien l'asymétrie introduite dans le carnet.

## Slide 11 - Partie II [10:55 -> 11:05]

Deuxième partie : on garde ce modèle, mais on s'intéresse maintenant à des scénarios très peu probables.

## Slide 12 - Limite du Monte-Carlo direct [11:05 -> 12:25]

Le cours donne la raison de l'échec du Monte-Carlo direct. Pour une probabilité p estimée par M trajectoires, la précision relative se comporte comme racine de (1-p) sur M p. Donc quand p devient très petit, il ne suffit pas de simuler un peu plus : le coût explose.

Les probabilités visées dans le rapport descendent de 10 puissance moins 7 à 10 puissance moins 13. Pour une précision relative de l'ordre de 10 %, on arrive à des coûts de 10 puissance 9 à 10 puissance 15 trajectoires. L'événement retenu est l'épuisement du bid alors qu'il est initialement plus profond et moins fragile. Dans le modèle, cela correspond à une baisse brutale difficile à atteindre par hasard.

## Slide 13 - Splitting AMS [12:25 -> 13:55]

La première méthode est le splitting adaptatif multiniveau. Au lieu d'estimer directement une probabilité minuscule, on la décompose en un produit de probabilités conditionnelles sur des niveaux de volume.

Techniquement, à chaque palier, on conserve les trajectoires qui se rapprochent de l'épuisement et on rééchantillonne leurs états. Le détail important ici est que l'on doit réinjecter l'état Hawkes complet, pas seulement le volume, puisque les intensités transportent la mémoire.

La figure montre que l'écart-type décroît en 1 sur racine de N, avec une pente log-log proche de moins un demi. Le coefficient de variation baisse nettement quand N augmente. C'est cohérent avec la théorie AMS et avec la CLT utilisée dans le rapport.

## Slide 14 - Loi de Q2 par AMS [13:55 -> 14:55]

Nous avons aussi utilisé AMS pour estimer la loi conditionnelle de Q2. Comme cette loi est importante pour enchaîner les cycles, il fallait vérifier que le splitting ne la déforme pas.

La comparaison avec un Monte-Carlo direct de grande taille donne des histogrammes très proches : même support, même forme générale, mêmes ordres de grandeur. Cette slide sert donc de contrôle croisé. Elle ne prouve pas tout, mais elle donne confiance dans la loi conditionnelle produite par AMS.

## Slide 15 - Splitting en deux phases [14:55 -> 15:55]

Une amélioration pratique consiste à séparer le calcul en deux phases. Les premiers paliers du splitting sont coûteux, mais ils ne dépendent pas toujours de la requête finale. On peut donc les calculer une fois, stocker la distribution empirique des états survivants à un niveau k étoile, puis redémarrer depuis cette distribution.

Dans l'expérience du rapport, le coût hors-ligne est d'environ 7,7 secondes, puis une requête en ligne coûte environ 0,7 seconde. Les moyennes obtenues sont 12,90 et 12,91, donc l'approximation est très proche tout en étant plus pratique pour tester plusieurs scénarios.

## Slide 16 - Importance sampling : mesure et poids [15:55 -> 17:20]

La deuxième méthode est l'importance sampling. Ici, on ne sélectionne pas les trajectoires par niveaux : on modifie directement la loi simulée pour rendre l'événement plus fréquent, puis on corrige par un poids de vraisemblance.

Le paramètre theta règle la force du changement de mesure. Dans nos expériences, le meilleur réglage est autour de 0,30. Au-delà, les poids deviennent instables et le coefficient de variation augmente fortement. Il y a même un cas trompeur : pour theta égal 2,1, le CV redescend, mais l'estimation de probabilité s'effondre presque à zéro. Donc il faut regarder à la fois la probabilité estimée et la dispersion des poids.

## Slide 17 - Comparaison AMS / IS à N fixé [17:20 -> 18:40]

À nombre de trajectoires fixé, l'importance sampling bien réglé donne ici une variance plus faible que l'AMS, avec une efficacité relative de 0,57. Ce résultat est intéressant parce qu'il évite de présenter AMS comme automatiquement meilleur.

La nuance est importante : cette comparaison vaut pour un événement modéré. Pour des cascades plus profondes, l'avantage d'AMS est d'exploiter explicitement les niveaux de volume, alors que l'IS dépend fortement d'un bon changement de mesure. La conclusion du rapport est donc que les deux méthodes sont complémentaires.

## Slide 18 - Partie III [18:40 -> 18:50]

Dernière partie : on vérifie que la calibration est raisonnable avant d'appliquer le modèle à des données réelles.

## Slide 19 - Calibration synthétique [18:50 -> 20:15]

On commence par une validation sur données simulées, où les vrais paramètres sont connus. La log-vraisemblance du modèle Hawkes couplé permet une estimation MLE.

Les paramètres de fond mu-a et mu-b sont retrouvés très précisément, autour de 3,01 et 1,50 pour des vraies valeurs 3,0 et 1,5. Les paramètres alpha et bêta sont moins précis : environ 6 % et 15 % d'erreur. Ce n'est pas surprenant, car ils sont corrélés dans la vraisemblance et l'échantillon est court. La figure de droite montre quand même que l'intensité reconstruite suit bien l'intensité vraie.

## Slide 20 - Bitcoin Black Thursday : données 1h [20:15 -> 22:15]

L'application réelle porte sur le 12 mars 2020, le Black Thursday du Bitcoin, avec une baisse d'environ 41 % sur une journée. Nous utilisons des bougies horaires Binance et nous calibrons le modèle sur les 1696 observations précédant la crise.

Le résultat principal est que le régime pré-crise est calibré avec alpha presque nul. Autrement dit, à cette résolution, le régime avant crise ressemble plus à un modèle Poisson qu'à un modèle fortement auto-excité.

Sous ce régime pré-crise, la séquence observée de cinq bougies négatives consécutives a une probabilité AMS d'environ 8,5 fois 10 puissance moins 6, soit environ une chance sur 118 000. L'interprétation doit rester prudente, parce qu'on travaille en bougies 1h et non en tick-by-tick, mais l'ordre de grandeur indique que la séquence est rare relativement au régime calibré.

## Slide 21 - GameStop [22:15 -> 23:25]

Nous avons aussi essayé d'appliquer la même logique au cas GameStop. Nous ne l'avons pas retenu, et c'est une limite importante à expliquer.

Première limite : les données journalières disponibles donnent seulement 70 observations, donc une vraisemblance trop plate pour identifier correctement alpha et bêta. Deuxième limite, plus fondamentale : le mécanisme GameStop est largement exogène au carnet, lié à une coordination d'investisseurs. Notre modèle vise des cascades endogènes de liquidité. Dans ce cas, forcer le modèle aurait donné une lecture artificielle.

## Slide 22 - Conclusion [23:25 -> 25:00]

Pour conclure, il y a trois résultats à retenir.

Premier point : partir du Poisson nous donne une référence vérifiable, puis la mémoire Hawkes et le couplage changent fortement la loi d'épuisement. Dans les expériences, le temps moyen de premier épuisement descend jusqu'à environ 5,9 dans le régime couplé.

Deuxième point : pour les événements rares, le Monte-Carlo direct n'est pas adapté. AMS et importance sampling répondent à deux logiques différentes : AMS exploite les niveaux, IS sert de changement de mesure indépendant, mais seulement si les poids restent stables.

Troisième point : sur Bitcoin, le modèle calibré avant crise indique que la séquence du Black Thursday est rare dans le régime pré-crise. En revanche, GameStop montre aussi la limite du cadre : le modèle ne doit pas être utilisé quand le mécanisme dominant est exogène.

Les perspectives naturelles sont les données tick-by-tick pour mieux séparer alpha et bêta, l'extension à plus de deux niveaux, et le lien entre probabilités d'épuisement et mesures de risque de marché. Merci, nous sommes prêts pour vos questions.

---

## Réponses préparées

- **Pourquoi commencer par le Poisson alors que le carnet réel est plus complexe ?** Parce qu'il donne une référence analytique. La loi inverse-gaussienne et la quadrature permettent de vérifier que la simulation est correcte avant d'ajouter Hawkes.
- **Le non-rejet KS est-il un bon résultat ?** Oui, dans ce contexte. On cherche à vérifier que la simulation Poisson est cohérente avec l'approximation IG. Une p-value de 0,0971, supérieure à 5 %, indique qu'on ne détecte pas d'écart significatif. Ce n'est pas une preuve absolue, mais c'est une validation raisonnable de l'étape de base.
- **Le biais de troncature Hawkes invalide-t-il la suite ?** Non, mais il faut le documenter. Il explique l'écart de stationnarité dans le cas inhibiteur. Dans la suite, on compare des modèles simulés avec la même convention, donc l'effet est contrôlé.
- **Pourquoi AMS plutôt que Monte-Carlo direct ?** Pour des probabilités entre 10^-7 et 10^-13, la précision relative du Monte-Carlo direct demanderait un nombre de trajectoires irréaliste. AMS remplace cette probabilité par un produit de probabilités conditionnelles.
- **L'importance sampling meilleur que AMS sur une slide, contradiction ?** Non. Il est meilleur dans l'expérience modérée à N fixé. Pour des cascades plus profondes, AMS est plus robuste parce qu'il exploite la structure par niveaux.
- **Pourquoi alpha vaut presque zéro sur BTC ?** C'est le diagnostic de calibration au pas horaire : le régime pré-crise ressemble à un régime quasi-Poisson. C'est précisément pour cela que la séquence de cinq baisses consécutives ressort comme rare.
- **Pourquoi ne pas garder GameStop ?** Les données sont trop peu nombreuses et le mécanisme dominant est exogène au carnet. Le modèle vise des cascades endogènes de liquidité.
