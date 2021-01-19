# Plugin BDTopo Importer pour QGIS

Ce module permet d'importer les couches de la BDTopo de l'IGN dans
une base de données PostGIS. Il automatise l'import de couches multiples dans un schéma donné.

Auteur : Augustin Roche

Code source : https://github.com/aroche/bdtopo_importer

## Compatibilité

Ce plugin ne fonctionne qu'avec la version 3.14 ou supérieure de QGIS.

## Import des couches

Les données doivent d'abord être téléchargées depuis 
[le site de l'IGN](https://geoservices.ign.fr/documentation/diffusion/telechargement-donnees-libres.html#bd-topo).
Ces données sont disponibles par département ou par région, sous forme de fichier compressé au format 7zip.

Une fois les données téléchargées, deux méthode d'import sont disponibles : 
* soit à partir du fichier décompressé : nécessite de décompresser les données au préalable
* soit à partir du fichier compressé. Il faut alors disposer d'un outil de décompression : 7zip ou py7zr (voir ci-dessous)

## Installation d'un outil de décompression

Pour utiliser les données sans avoir à les décompresser, il
faut disposer d'un outil pour lire et extraire les couches.

Deux options sont disponibles : 7zip (programme externe) ou py7zr (librairie python)

Le choix de l'une ou l'autre option est configurable en cliquant sur le bouton [...] à côté de "Sélectionner un fichier".

### Installation et utilisation de 7zip

* Installation pour Windows : téléchargez et installez le programme depuis le site https://www.7-zip.org/download.html.
* Installation pour linux / Ubuntu : https://doc.ubuntu-fr.org/p7zip

Si la commande `7z` n'est pas reconnue par le système, il faut configurer le plugin pour qu'il trouve le programme.
Pour cela, cliquer sur le bouton [...] à côté de "Sélectionner un fichier". Rentrez ensuite le chemin vers l'exécutable 7z (sous Windows,
probablement *c:\Program Files\7-Zip\7z.exe*)

### Installation et utilisation de py7zr

Py7zr</a> est une librairie Python permettant de travailler avec les archives 7zip.

Pour l'installer, entrer la commande `pip install py7zr`, en s'assurant que l'installation a bien lieu pour la version de python utilisée par QGIS.

Pour utiliser cette librairie, sélectionnez "py7zr" dans les options d'extraction du plugin.

## Utilisation du plugin

1. Choisissez la source de données (fichier .7z ou dossier décompressé)
1. Sélectionnez le fichier ou le dossier contenant les données
1. Choisissez les couches à importer
1. Choisissez la base de données et le schéma dans lequel importer les couches. 
La base et le schéma doivent déjà être créés et doivent avoir été configurés dans 
les sources de données de QGIS, y compris les identifiants/mots de passe.
1. Choisissez l'action à réaliser si les tables existent déjà : écraser les données ou les ajouter à la suite
de l'existant ;
1. Cliquez sur "OK": l'import se lance en arrière-plan. 
Plusieurs couches peuvent être importées en parallèle.

## Rapporter un bug

Les problèmes peuvent être signalés sur https://github.com/aroche/bdtopo_importer/issues .