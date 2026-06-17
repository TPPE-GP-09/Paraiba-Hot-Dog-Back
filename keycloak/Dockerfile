FROM quay.io/keycloak/keycloak:22.0.1

COPY paraiba-hotdog-realm.json /opt/keycloak/data/import/paraiba-hotdog-realm.json

CMD ["sh", "-c", "start-dev --import-realm --http-host=0.0.0.0 --http-port=${PORT:-8080}"]
