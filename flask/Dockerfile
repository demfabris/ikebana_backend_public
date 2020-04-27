FROM python AS flaskapp

# Setting required ENV variables
ENV HOME /root
ENV EMAIL_PASSWORD email_password
ENV EMAIL_USER noreply.email@email.com
ENV GOOGLE_CLIENT_ID google_oauth_id
ENV GOOGLE_CLIENT_SECRET google_oauth_secret
ENV GOOGLE_DISCOVERY_URL google_oauth_request_uri
ENV APP_SECRET_KEY flask_app_key

# COPY .aws $HOME/.aws
COPY . $HOME/flask

WORKDIR $HOME/flask

# Run WSGI server
# RUN rm -r Pipfile Pipfile.lock
RUN pip install -r requirements.txt
CMD uwsgi --ini wsgi.ini
