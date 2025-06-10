# desploy

## ejecutar en tu maquina

siempre situado en la raiz del proyecto

```bash

rsync -avzP --no-perms --no-owner --no-group --delete --exclude='.venv' --exclude='.git' --exclude='.idea'  -e 'ssh' ./ root@10.2.6.169:/uprchat/code

```

## ejecutar en el servidor

```bash

cd /uprchat/code

podman-compose -f docker-compose.yml down && podman-compose -f docker-compose.yml up -d

```
