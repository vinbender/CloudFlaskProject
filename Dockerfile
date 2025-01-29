FROM python 3.9 slim 

#allow statements and log messages to immediately appear in the Knative logs
ENV PYTHONUNBUFFERED True

#copy local code to the container image
ENV APP_HOME /APP
WORKDIR $APP_HOME
COPY . ./

# Install production dependencies
RUN pip install Flask gunicorn

#run the web service on container startup. Here we use the gunicorn
#webserver with one worker process and 8 threads
#For enviorments with multiple CPU cores, increase the number of workers
#to be equal to the cores avalible
#TImeout is set to 0 to disable the timeouts of the workers to allow Cloud Run to increase scaling
CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 main:app
