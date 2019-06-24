**Usage:**

Settings stored in config.json 

```bash
git clone https://gitlab.intes.by/dimao/pyticket.git
cd pyticket
pip install -r requirements.txt
python3 pyticket -m pyticket/
```

docker-compose.yml example:
```yaml
version: '2'
services:
  ftp_sync:
    container_name: ftp-sync
    image: registry.intes.by/dimao/ftp-sync:master
    environment:
      - USER=
      - PASSWORD=
      - SERVER=
      - CHECK_INTERVAL=5
    volumes:
      - /intes/import-ticket/tickets:/tickets
    restart: always

  pyticket:
    image: registry.intes.by/dimao/pyticket:master
    container_name: import-ticket
    hostname: import-ticket
    volumes:
      - ./config.json/:/config.json
      - /intes/import-ticket/tickets:/tickets
      - /var/run/docker.sock:/docker.sock
    ports:
      - "9090:9090"
    depends_on:
      - ftp_sync
    restart: always
```

