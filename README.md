# OBSFlowControl

## Description

### FR
Un script Python qui surveille le flux vidéo d'OBS pour détecter des problèmes tels qu'un flux gelé ou une faible qualité, et change automatiquement les scènes en fonction de l'état du flux.

### EN
A Python script that monitors OBS video streams to detect issues such as frozen streams or low quality, and automatically switches scenes based on the stream's status.

---

## Fonctionnalités / Features

### FR
- Détection des scènes gelées via le WebSocket d'OBS.
- Changement automatique de scène vers une scène de type "BRB" si un problème est détecté.
- Possibilité de démarrer et arrêter un stream OBS via des endpoints API. (`/start` // `/stop`)
- Serveur Flask intégré pour les commandes HTTP.

### EN
- Detects frozen scenes using OBS WebSocket.
- Automatically switches to a "BRB" scene if an issue is detected.
- Allows starting and stopping OBS streams through API endpoints. (`/start` // `/stop`)
- Integrated Flask server for HTTP commands.

---

## Prérequis / Prerequisites

### FR
1. **Python**.
2. **OBS avec le plugin WebSocket activé**.
   - Télécharger et installer le plugin [OBS WebSocket](https://github.com/obsproject/obs-websocket).
3. Modules Python nécessaires :
   - Flask
   - websocket-client

### EN
1. **Python**.
2. **OBS with the WebSocket plugin enabled**.
   - Download and install the plugin [OBS WebSocket](https://github.com/obsproject/obs-websocket).
3. Required Python modules:
   - Flask
   - websocket-client

---

## Installation

### FR
1. Téléchargez le fichier `obs_controller.py` et installez les dépendances nécessaires.
2. Activez le WebSocket sur votre OBS et créez les scènes/sources nécessaires. (La source doit être une **Media Source** avec pour Input un lien **SRT** ou **RTMP** (`srt://ip:port` ou `rtmp://ip:port/app/key`)).
3. Modifiez les paramètres suivants dans le script :
   - `APP_PORT`
   - `OBS_WEBSOCKET_URL`
   - `OBS_PASSWORD`
   - Autres paramètres spécifiques à votre configuration.
4. Lancez le script Python. (Sur un serveur comme Ubuntu, il est recommandé d'utiliser des modules comme **PM2** pour gérer l'exécution).
5. **OPTIONNEL** : Si vous souhaitez utiliser le serveur à distance, ouvrez le port défini dans votre configuration Python.

**Accès :**
- Utilisez l'adresse IP de la machine où l'application Python est exécutée (ou l'IP publique si le port est ouvert).
- Ajoutez `/start` ou `/stop` à l'URL pour démarrer ou arrêter un stream.

### EN
1. Download the `obs_controller.py` file and install the required dependencies.
2. Enable WebSocket on your OBS and create the necessary scenes/sources. (The source must be a **Media Source** with an **SRT** or **RTMP** input (`srt://ip:port` or `rtmp://ip:port/app/key`)).
3. Edit the following parameters in the script:
   - `APP_PORT`
   - `OBS_WEBSOCKET_URL`
   - `OBS_PASSWORD`
   - Other configuration values specific to your setup.
4. Run the Python script. (On servers like Ubuntu, using modules like **PM2** to manage the script is recommended).
5. **OPTIONAL**: If you want to use the server remotely, open the port specified in your Python configuration.

**Access:**
- Use the IP address of the machine where the Python application is running (or the public IP if the port is open).
- Append `/start` or `/stop` to the URL to start or stop a stream.

---

## Exemple / Example

### Démarrage du script / Starting the script
```bash
python obs_controller.py
```

### Accès API / API Access
## Démarrer un stream :
```bash
GET http://<server-ip>:<port>/start
```

## Arrêter un stream :
```bash
GET http://<server-ip>:<port>/stop
```
