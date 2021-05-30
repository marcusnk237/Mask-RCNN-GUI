# Mask_RCNN_openCV

Readaptation d'un programme d'implémentation du Mask R-CNN à travers un GUI sur Python.

Le programme fonctionne comme suit :
- L' utilisateur va au préalable charger une vidéo
- Une fois cela fait, il pourra choisir si oui ou non il peut appliquer le Mask-RCNN sur la vidéo.
- Une fois le choix effectuer , en appuyant sur le bouton Démarrer, le Mask R-CNN va s'appliquer sur toute la durée de la vidéo. L' utilisateur a la possibilité d'arrêter ou de mettre en pause la vidéo générée par l'application du masque.
- Une fois la vidéo terminée, il peut choisir de sauvegarder le résultat sous format vidéo.

NOTES : 
Il est essentiel de créer un dossier nommé "weights", qui contiendra le modèle COCO, qui a été utilisé comme poids pour notre Mask R-CNN. 
Le modèle COCO peut être télécharger à partir de cette adresse: https://github.com/matterport/Mask_RCNN/releases
( puis télécharger mask_rcnn_coco.h5)

Installation de pycocotools:

git clone https://github.com/philferriere/cocoapi.git
pip install git+https://github.com/philferriere/cocoapi.git#subdirectory=PythonAPI
pycocotools requiert Visual C++ 2015 Build Tools.

A noter que le GUI a été développé sur Python 3.6

Credits : 
matterport - Mask R-CNN implementation
Rob--/mask-rcnn-wrapper
