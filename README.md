


# <div align="center"> [AIC] Projet N°6 : wp_backup.py </div>
# <div align="center"> ![Image](https://upload.wikimedia.org/wikipedia/commons/2/23/Python_powered.svg)  </div>
# <div align="center"> Script de Sauvegarde d'un serveur Wordpress sur un serveur ftp distant </div>



[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](LICENSE)
[![Python 3.6.8](https://badgen.net/badge/python/3.6.8)](https://www.python.org/downloads/release/python-368/)
[![Centos 8](https://badgen.net/badge/CentOS/8)](https://www.centos.org/)
![Contibutions welcom](https://img.shields.io/badge/contributions-welcom-orange.svg)
![Last commit](https://img.shields.io/github/last-commit/hanroy/OC-P6)


## Table des matières
1. [Contexte du projet](#part1)
2. [Configuration de l'environnement](#part2)
  - [La machine webserver](#part2.1)
  - [Le serveur FTP](#part2.2)
 
3. [Fonctionnement du programme wp_backup.py](#part3)
4. [Log](#part4)
5. [Crontab](#part5)
6. [Les limitations du programme](#part6)
7. [Contribution](#part7)

## <a name="part1"> 1. Contexte du projet: </a>
Pour garantir la continuité du service et accès au site web en cas de soucis, une sauvegarde est effectuée tout les soirs via un script python.  

## <a name="part2"> 2. Configuration de l'environnement: </a>
#### <a name="part2.1"> - La machine webserver: </a>
- CentOS 8
- LAMP
- Base de donnée MariaDB
- Python 3.6.8
- Le dossier qui héberge les élements du site : `/var/www/html/wordpress`

#### <a name="part2.2"> - Le serveur FTP: </a>
- CentOS8
- LFTP
- Dossier de sauvegarde wordpress : `/home/wordpress`

## <a name="part3"> 3. Fonctionnement du programme wp_backup.py: </a>
Le programme se compose de 3 fichiers :
- wp_backup.py
- variables.json
- backupbdd.sh

Le programme se déroule ainsi :
- Supprimer les anciens dossiers de sauvegardes en local et ne garder que les 5 derniers jours.
- Créer le nouveau dossier de sauvegarde avec la date du jour 
- Exécuter un script shell qui :
  - Sauvegarde de la base de donnée, en utilisant la commande 'wp' : `BddBackup.$(date +"%m-%d-%Y").sql`
  - Sauvegarder le dossier /var/www/html/wordpress et le compresser avec la date du jour : `WordpressBackup.$(date +"%m-%d-%Y").tar.gz`
- Envoie de la sauvegarde à un serveur FTP distant 
## <a name="part4"> 4. Log: </a>
- Fichier de log généré par le crontab 
- Envoie du log par Email 

## <a name="part5"> 5. Crontab: </a>
via crontab -l (on affiche la tâche planifiée à 5h30 tout les jours)
`30 5 * * 1 sh /root/scriptBackup.py | tee /var/log/scriptBackup.log_$(date +"%m-%d-%y") | mail -s "Backup Log" @EMAIL`

## <a name="part6"> 6. Les limitations du programme: </a>
Des fonctionnalités doivent être rajouté au programme pour avoir une solution plus complète :
- Supprimer les vieilles sauvegarde de plus de 5 jours sur le serveur FTP.
- Affiner les logs.
- Ajouter une fonction pour vérifier l'intégrité des fichiers sauvegardés.
- Compléter le programme par une solution complémentaire de restauration.

## <a name="part7"> 7. Contribution: </a>
Toute [contribution](https://github.com/hanroy/OC-P6/blob/master/CONTRIBUTING.md) est la bienvenue.


