# docker buildx build --platform linux/amd64,linux/arm64,linux/x86_64 -t 192.168.0.17:5000/auto_instagram:0.0.5 --push --output=type=registry,registry.insecure=true -f ./Dockerfile .
# docker build --tag  192.168.0.17:5000/auto_instagram:0.0.1 -f ./Dockerfile .

# docker build --tag  localhost:5000/auto_instagram:0.0.6 -f ./Dockerfile .
# docker push localhost:5000/auto_instagram:0.0.6

# linux로 빌드
# docker build --platform linux/x86_64 --tag 192.168.0.17:5000/auto_instagram:0.0.3 -f ./Dockerfile .
# docker push 192.168.0.17:5000/auto_instagram:0.0.3


FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Set environment variables for configurable files
ENV SESSION_FILE_PATH="user_sessions/dodo.lunch_session.json"
ENV CONFIG_FILE_PATH="configs/dodo.lunch_config.yaml"

COPY $SESSION_FILE_PATH ./$SESSION_FILE_PATH
COPY $CONFIG_FILE_PATH ./$CONFIG_FILE_PATH

COPY .env .
COPY key.key .

# python files
COPY automate_* .
COPY utils.py .
COPY templates/ ./templates/
COPY comment_generator.py .


# Set the entrypoint to run automate_main.py
# ENTRYPOINT ["python", "automate_main.py"]

# Create a shell script to run the main program and handle errors
RUN echo '#!/bin/sh\n\
python automate_main.py\n\
if [ $? -ne 0 ]; then\n\
    echo "An error occurred. Waiting for 10 minutes before exiting."\n\
    sleep 600\n\
fi' > /app/run_with_delay.sh

RUN chmod +x /app/run_with_delay.sh

# Set the entrypoint to run the shell script
ENTRYPOINT ["/app/run_with_delay.sh"]