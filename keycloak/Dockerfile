FROM quay.io/keycloak/keycloak:22.0.1

COPY paraiba-hotdog-realm.json /opt/keycloak/data/import/paraiba-hotdog-realm.json

RUN /opt/keycloak/bin/kc.sh build

ENTRYPOINT ["/bin/sh", "-c"]
CMD ["exec /opt/keycloak/bin/kc.sh start-dev --import-realm --http-host=0.0.0.0 --http-port=${PORT:-8080}"]
