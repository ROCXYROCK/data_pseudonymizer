
# run Database
#create image
sudo docker build -f docker/Database -t medizinische-db .

#run the container
sudo docker run -d --name database -p 5432:5432 -e POSTGRES_HOST_AUTH_METHOD=trust medizinische-db
# alternative dazu: 
# sudo docker run -d --name database -p 5432:5432 -e POSTGRES_PASSWORD=deinPasswort medizinische-db



# enter the Container: sudo docker exec -it database bash
# Verbindung zur DB testen: psql -U postgres
# Docker container in einem Netzwerk erstellen
# sudo docker network create mein-netzwerk
# sudo docker run -d --name db-container --network mein-netzwerk medizinische-db
# sudo docker run -d --name app-container --network mein-netzwerk meine-app


# Docker Cheatsheet

# 1. **Container Management**
# Container auflisten
# sudo docker ps -a

# Container starten
# sudo docker start <container_name_or_id>

# Container stoppen
# sudo docker stop <container_name_or_id>

# Container entfernen
# sudo docker rm <container_name_or_id>

# Container betreten
# sudo docker exec -it <container_name_or_id> bash

# 2. **Image Management**
# Images auflisten
# sudo docker images

# Image entfernen
# sudo docker rmi <image_name_or_id>

# Image neu bauen
# sudo docker build -t <image_name> .

# 3. **Logs und Debugging**
# Logs eines Containers lesen
# sudo docker logs <container_name_or_id>

# 4. **Netzwerk und Kommunikation**
# Container-Network erstellen
# sudo docker network create <network_name>

# Container zu einem Netzwerk hinzufügen
# sudo docker network connect <network_name> <container_name_or_id>

# 5. **Container und Images löschen**
# Alle gestoppten Container entfernen
# sudo docker container prune

# Alle ungenutzten Images entfernen
# sudo docker image prune

# Alle Container und Images entfernen (Vorsicht)
# sudo docker rm -f $(sudo docker ps -aq) && sudo docker rmi -f $(sudo docker images -q)

# 6. **Häufige Probleme**
# Container startet nicht (mit Logs prüfen)
# sudo docker logs <container_name_or_id>





# 1. Zugriff auf den Container
# sudo docker exec -it database psql -U postgres

# 2. Auswahl der Datenbank (wenn erforderlich)
# \c medizinische_db

# 3. Auflisten der Tabellen
# \dt

# 4. Detaillierte Anzeige einer spezifischen Tabelle
# \d arzt

# 5. Beenden von psql
# \q