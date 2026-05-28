# Script de soutenance — Modélisation stochastique d'un carnet d'ordres
**Durée cible : 25 minutes.** Repères de minutage entre crochets. Le jury a déjà lu le rapport : on ne récite pas, on raconte l'histoire et on commente les chiffres.

---

## Slide 1 — Titre [0:00 → 0:30]
Bonjour à tous. Je m'appelle [—], voici [—]. Notre MODAL porte sur la modélisation stochastique d'un carnet d'ordres : on cherche à comprendre quand et avec quelle probabilité un côté du carnet s'épuise avant l'autre, et à pousser ce modèle jusqu'à un vrai krach de marché.

## Slide 2 — Le fil conducteur [0:30 → 2:00]
Le carnet d'ordres empile à chaque instant des volumes côté acheteur, le bid, et côté vendeur, l'ask. Point clé : le prix ne bouge pas en continu, il saute brutalement dès qu'un de ces deux côtés se vide. Toute notre étude tient donc dans deux instants — tau-a et tau-b, les moments où l'ask ou le bid touche zéro — et une question : lequel arrive le premier, et avec quelle probabilité.

On a structuré le travail en trois temps. D'abord modéliser, du Poisson le plus simple jusqu'au Hawkes couplé. Ensuite estimer le rare : quand la probabilité visée descend à dix puissance moins sept, voire moins treize, le Monte-Carlo naïf s'effondre. Enfin calibrer sur des données réelles. Comme vous avez le rapport, je ne récite pas les définitions : je me concentre sur les résultats charnières et sur ce qu'ils signifient.

## Slide 3 — Divider Partie I [2:00 → 2:10]
Première partie : construire le modèle, couche par couche.

## Slide 4 — Le socle Poisson [2:10 → 3:50]
On part du modèle le plus dépouillé : chaque côté est une marche de Poisson avec un drift négatif — il y a plus d'annulations que d'insertions, donc le carnet tend à se vider. L'intérêt, c'est que tout est calculable analytiquement : le temps d'atteinte de zéro suit une loi inverse-gaussienne, d'espérance 12,5.

Pourquoi je m'y attarde alors que c'est le cas trivial ? Parce que cette formule fermée devient notre **étalon**. Chaque modèle plus riche sera jugé par rapport à elle. Et la simulation valide tout : espérance à 0,14 % près, test de Kolmogorov-Smirnov non rejeté. Le socle est solide.

## Slide 5 — Probabilité de ruine sans simuler [3:50 → 5:20]
Deuxième brique : la probabilité que l'ask se vide avant le bid. En conditionnant sur tau-a, on l'écrit comme une intégrale de la densité IG contre la survie de l'autre côté. Une simple quadrature de Gauss-Legendre — donc un calcul instantané — remplace des millions de simulations.

Le point qui compte est sur le panneau de droite : l'écart maximal entre la formule et le Monte-Carlo est de 0,049, ce qui correspond très exactement à la barre d'erreur statistique du Monte-Carlo lui-même. Autrement dit, il n'y a **aucun biais systématique** : la formule est exacte, pas seulement approchée.

## Slide 6 — Hawkes et le piège du clipping [5:20 → 7:10]
Maintenant on introduit la mémoire. Une annulation rend les annulations suivantes plus probables : c'est l'auto-excitation de Hawkes. La théorie prédit une intensité stationnaire de 2,80.

Or la simulation donne 2,96 — près de 6 % d'écart. Et ce n'est pas du bruit. C'est là qu'on a une honnêteté à avoir : l'écart vient du *clipping*. Quand l'intensité passerait sous zéro, on la tronque à zéro. Ce plancher casse le bilan de flux que suppose la démonstration, qui elle travaille sur toute la droite réelle. D'où un excès systématique. Je tiens à le souligner : identifier l'origine d'un biais, c'est plus utile que de le masquer en ajustant des paramètres.

## Slide 7 — Couplage croisé [7:10 → 9:00]
On couple les deux files. Chaque côté garde sa logique propre — auto-excitation par ses décréments, inhibition par ses incréments — et il est *en plus* excité par tout événement de l'autre côté. C'est cohérent avec la microstructure : une activité intense côté bid signale un déséquilibre qui agite aussi l'ask.

L'effet est net et chiffré : au coin symétrique, le temps moyen d'épuisement passe de 8,3 dans le cas Poisson à 5,8 avec couplage, soit 30 % de moins. La lecture intéressante, c'est que les deux côtés tendent à se vider **ensemble**. C'est exactement la signature d'une cascade : un déséquilibre d'un côté précipite l'autre.

## Slide 8 — Les quatre régimes [9:00 → 10:40]
Voici la synthèse de la première partie. On compare quatre modèles. Trois effets se superposent. Premier effet, purement combinatoire : prendre le minimum de deux files indépendantes divise déjà la moyenne par 1,45 ; aucune mémoire là-dedans. Deuxième effet : l'auto-excitation crée une queue gauche épaisse — des avalanches d'annulations très rapides. Troisième effet : le couplage amplifie le tout, pour un facteur de réduction global d'environ 2,1.

Le message à retenir : la mémoire ne se contente pas de déplacer la moyenne, elle **déforme la loi entière** — elle épaissit les extrêmes, ce qui est précisément ce qui nous intéressera pour les événements rares.

## Slide 9 — Du volume au prix [10:40 → 12:10]
Dernière étape de modélisation : passer au prix. On gère quatre limites, et surtout on **transporte la mémoire Hawkes** d'un cycle de prix au suivant. La dérive du mid-price par cycle vaut delta sur deux fois (2p moins 1). Le prix est une martingale si et seulement si p vaut un demi, c'est-à-dire si le carnet est symétrique.

Validation à droite : en régime asymétrique, on prédit une dérive de 0,238 par cycle, on en mesure 0,2375. La conséquence est forte : observer la **seule dérive du prix** suffit à inférer l'asymétrie cachée du carnet. Le modèle est identifiable depuis le prix seul.

## Slide 10 — Divider Partie II [12:10 → 12:20]
Deuxième partie, le cœur méthodologique : estimer l'improbable.

## Slide 11 — Mort du Monte-Carlo naïf [12:20 → 13:50]
Le problème est quantifié simplement : le coefficient de variation de l'estimateur Monte-Carlo se comporte en un sur racine de M-p. Quand p tend vers zéro, il diverge. Pour viser des probabilités de dix puissance moins sept à moins treize, il faudrait entre un milliard et dix puissance quinze trajectoires. C'est mort.

L'événement rare qu'on retient, c'est l'épuisement du bid dans un régime où le bid est justement plus profond et moins fragile — donc difficile à vider. C'est le scénario typique d'un flash crash. On va attaquer ça avec deux méthodes orthogonales, puis les confronter.

## Slide 12 — Splitting AMS [13:50 → 15:30]
Première méthode : le splitting adaptatif multiniveau. L'idée : on découpe l'événement rare en paliers de volume, et à chaque palier on rééchantillonne les trajectoires survivantes — celles qui ont progressé vers l'épuisement — en réinjectant leur état Hawkes complet. On guide ainsi la simulation là où le Monte-Carlo gaspillerait tout.

La figure valide la théorie : en échelle log-log, la pente est de moins un demi, donc l'écart-type décroît bien en un sur racine de N comme le prédit notre CLT par delta-méthode. Concrètement le coefficient de variation chute d'un facteur 7.

## Slide 13 — Non-indépendance des cycles [15:30 → 17:30]
Voici le résultat que je défends le plus. Un flash crash de profondeur k, c'est k épuisements bid d'affilée. La tentation est d'écrire ça comme p-un puissance k, en supposant les cycles indépendants. **C'est faux.**

Parce que la mémoire Hawkes est transportée : après un épuisement bid, le bid se reconstruit plein, mais l'ask, lui, est déjà entamé et a été excité par le couplage. Donc les cycles suivants sont *plus durs*. On mesure c-un égal 0,14, c-deux 0,04, et ça s'effondre. La courbe i.i.d. **surestime** le risque profond.

Et regardez la droite : l'AMS atteint dix puissance moins treize à k égal 8, là où le Monte-Carlo direct, en triangles, s'arrête à k égal 3 faute de trajectoires. C'est exactement pour ça qu'on ne peut pas se contenter d'une hypothèse Bernoulli : il faut l'AMS.

## Slide 14 — Importance sampling [17:30 → 19:00]
Deuxième méthode, indépendante : l'importance sampling par basculement exponentiel. On tord les intensités d'un facteur thêta pour rendre l'événement rare fréquent, et on corrige par la vraisemblance.

Il y a un optimum net à thêta-étoile autour de 0,30, qui fait baisser le coefficient de variation. Mais — et c'est le piège que je veux signaler — au-delà de 0,6 les poids dégénèrent et le CV explose au-dessus de 100. Pire : à thêta égal 2,1 le CV *rechute* artificiellement. Ce n'est pas une amélioration : c'est que presque plus aucune trajectoire n'atteint l'événement, et l'estimateur tend vers zéro. Leçon : une faible variance peut cacher un estimateur mort. Il faut toujours regarder l'estimation, pas seulement sa dispersion.

## Slide 15 — Verdict AMS vs IS [19:00 → 20:40]
On les départage à nombre de trajectoires fixé, sur cinquante réplications. Résultat contre-intuitif : à N égal, l'importance sampling bien réglé **bat** l'AMS — efficacité relative de 0,57, soit 43 % de réplications en moins.

Mais attention à la portée de ce résultat. L'IS tord les intensités *uniformément* ; il ne sait pas exploiter la structure géométrique par niveaux du problème. Donc il gagne sur un événement modéré, mais dès qu'on va profond, k supérieur ou égal à 5, c'est l'AMS qui reprend l'avantage de façon décisive. La conclusion honnête, ce n'est pas « telle méthode est la meilleure », c'est : **le bon outil dépend de la profondeur de l'événement rare**.

## Slide 16 — Divider Partie III [20:40 → 20:50]
Troisième partie : confronter le modèle au réel.

## Slide 17 — Calibration [20:50 → 22:10]
Pour calibrer, on a dérivé la log-vraisemblance du Hawkes bivarié couplé, calculable en temps linéaire. La question : sait-on retrouver les vrais paramètres ? Sur données synthétiques, la réponse est claire et visible sur les deux figures. À gauche, les barres : les paramètres de fond mu sont retrouvés à moins d'un pour cent. À droite, et c'est le plus parlant, on superpose l'intensité reconstruite avec les paramètres estimés à la vraie intensité — les deux courbes se suivent presque parfaitement.

En revanche alpha et bêta sont plus bruités, à 6 et 15 % d'erreur, parce qu'ils sont corrélés dans la vraisemblance sur un échantillon court. Je préfère le dire clairement plutôt que de survendre la précision.

## Slide 18 — Black Thursday [22:10 → 23:50]
Et voici l'aboutissement, sur un vrai krach : le 12 mars 2020, le Bitcoin perd 41 % en une journée, par liquidations en cascade — un mécanisme endogène au carnet, exactement notre modèle. On calibre sur les 1696 bougies horaires précédant la crise.

Le résultat est ce que j'appelle le punch de l'exposé : le régime pré-crise est calibré avec un alpha pratiquement nul — un régime quasi-Poisson, sans mémoire d'avalanche. Et sous ce régime calme, la cascade de 5 chutes consécutives effectivement observée avait une probabilité, estimée par AMS, de huit fois dix puissance moins six — environ une chance sur 118 000. Autrement dit : notre modèle confirme quantitativement que Black Thursday **était** un événement rare. C'est précisément ce qu'on voulait pouvoir chiffrer.

## Slide 19 — L'échec GameStop [23:50 → 24:30]
Un mot sur ce qui n'a pas marché, parce que c'est instructif. On a voulu rejouer la procédure sur le squeeze GameStop. Échec assumé, pour deux raisons : 70 observations journalières donnent une vraisemblance trop plate pour identifier alpha et bêta ; et surtout, le moteur de GameStop est une coordination Reddit — un mécanisme **exogène**, hors du carnet. Notre modèle suppose de l'endogène. Savoir où un modèle ne s'applique pas fait partie du travail.

## Slide 20 — Conclusion [24:30 → 25:00]
Pour conclure, trois charnières. Un : la mémoire déforme la loi d'épuisement, et l'asymétrie du carnet devient lisible dans la dérive du prix. Deux : la non-indépendance des cycles est le cœur du problème rare — AMS et IS sont complémentaires, et la référence i.i.d. trompe. Trois : sur Black Thursday, le modèle chiffre la rareté et sait refuser GameStop.

Les pistes naturelles : des données tick-by-tick pour mieux séparer alpha et bêta, l'extension à plus de niveaux, et relier la probabilité de ruine à une surface de volatilité implicite. Je vous remercie, et nous sommes à votre disposition pour vos questions.

---

## Réponses préparées (Q&R)
- **Pourquoi le clipping et pas une intensité bornée proprement ?** Le clipping est la convention standard du thinning d'Ogata inhibitoire ; le biais est documenté et constant, donc contrôlé. Une alternative serait un noyau softplus, au prix de la simulabilité exacte.
- **L'IS qui bat l'AMS, ce n'est pas contradictoire avec la conclusion ?** Non : c'est vrai à profondeur modérée seulement. Le tableau RE=0,57 est mesuré sur l'événement à un seul niveau. Pour les flash crashes profonds (slide 13), seul l'AMS tient.
- **Alpha=0 sur BTC, le modèle Hawkes est-il alors inutile ici ?** Au contraire : c'est le diagnostic. Le pré-crise est sans mémoire ; c'est ce qui rend la cascade observée si improbable sous ce régime, et donc remarquable.
- **Robustesse de la proba 8,5e-6 ?** Estimée par AMS avec IC ; l'ordre de grandeur (1/100 000) est ce qui importe pour l'interprétation, pas le chiffre exact.
- **Pourquoi bougies 1h et pas tick ?** Accès gratuit Binance ; les données tick (TARDIS/Kaiko) sont une perspective explicite pour affiner alpha, bêta.
