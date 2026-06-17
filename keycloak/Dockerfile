FROM quay.io/keycloak/keycloak:22.0.1

ENV KC_HTTP_ENABLED=true
ENV KC_HTTP_HOST=0.0.0.0
ENV KC_HTTP_PORT=8080

COPY paraiba-hotdog-realm.json /opt/keycloak/data/import/paraiba-hotdog-realm.json

RUN /opt/keycloak/bin/kc.sh build

ENTRYPOINT ["/opt/keycloak/bin/kc.sh"]
CMD ["start-dev", "--import-realm", "--http-enabled=true", "--http-host=0.0.0.0", "--http-port=8080"]