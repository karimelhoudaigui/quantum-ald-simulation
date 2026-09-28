# Post LinkedIn - Q-CHEM Lab / La Maison du Quantique

## Texte prêt à publier

Et si l'on pouvait explorer une chaîne de chimie quantique directement depuis
un navigateur, sans serveur de calcul à provisionner ?

Je publie aujourd'hui **Q-CHEM Lab**, une plateforme open source qui permet de
construire une molécule, choisir ses espaces actifs et comparer HF, CASCI, FCI
et VQE dans une même interface.

Le calcul s'exécute localement sur le processeur de l'ordinateur ou du téléphone
du visiteur, grâce à WebAssembly et à des Web Workers. Les coordonnées
moléculaires ne sont pas envoyées à une API de calcul distante.

L'objectif n'est pas de masquer la difficulté derrière un unique chiffre. La
plateforme sépare explicitement :

- l'erreur du solveur VQE dans l'espace actif ;
- l'erreur introduite par le choix de cet espace actif ;
- le coût associé en qubits, termes de Pauli, paramètres et portes à deux qubits.

Sur H2/STO-3G, le VQE local retrouve la référence CASCI/FCI avec une erreur
inférieure à `1e-10 Ha`. Sur LiH, le solveur reproduit également les cibles
CASCI, tandis que l'écart à la FCI complète montre que la limitation dominante
reste le modèle d'espace actif. C'est précisément le type de distinction que je
veux rendre visible.

Cette plateforme est une première brique de l'ambition de **La Maison du
Quantique** : créer un lieu où la recherche, l'ingénierie et la pédagogie
quantique deviennent concrètes, manipulables et reproductibles.

La suite est déjà tracée : VQE bruité dans l'interface, mitigation d'erreurs,
connexion à du hardware quantique, puis modèles moléculaires contrôlés inspirés
de l'Atomic Layer Deposition.

La plateforme : https://karimelhoudaigui.github.io/quantum-ald-simulation/

Le code et les résultats :
https://github.com/karimelhoudaigui/quantum-ald-simulation

Je souhaite échanger avec des chercheurs, ingénieurs, enseignants et acteurs
industriels qui veulent contribuer à construire cette passerelle entre science,
logiciel et hardware quantique.

#QuantumComputing #QuantumChemistry #VQE #OpenScience #MaisonDuQuantique

## Ordre des visuels

1. `01-qchem-lab-platform.png` - la plateforme et son exécution locale.
2. `02-h2-validation.png` - la baseline scientifique H2.
3. `03-lih-resources.png` - la croissance des ressources avec l'espace actif.

## Textes alternatifs

1. Capture de Q-CHEM Lab montrant la configuration LiH, la molécule 3D, le pipeline terminé et les résultats CASCI/VQE.
2. Courbe d'énergie potentielle H2 comparant HF, FCI, diagonalisation locale et VQE sur plusieurs distances H-H.
3. Quatre histogrammes montrant l'évolution des qubits, termes de Pauli, paramètres UCCSD et portes à deux qubits pour LiH CAS(2,2), CAS(2,3) et CAS(2,4).

## Format

Les trois exports sont des PNG de `1200 x 1500` pixels, soit un ratio vertical
`4:5`, et restent sous la limite de taille LinkedIn. Le HTML source permet de
les régénérer sans modifier les données scientifiques.
