FROM nginx

#REMOVING DEFAULTS
RUN rm -rf /etc/nginx/conf.d/default.conf
RUN rm -rf /etc/nginx/nginx.conf

#COPYING SSL CERTIFICATES INTO CONTAINER
COPY ssl /etc/ssl

#MOVING NGINX CONFIGS
COPY webapp.conf /etc/nginx/conf.d
COPY nginx.conf /etc/nginx/
COPY ssl-params.conf /etc/nginx/snippets/ssl-params.conf
COPY self-signed.conf /etc/nginx/snippets/self-signed.conf
