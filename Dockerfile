FROM amazonlinux:latest

RUN amazon-linux-extras enable python3.8
RUN yum install -y python3.8 zip awscli
COPY lambda/ /deploy
WORKDIR /deploy
RUN python3.8 -m pip install -r requirements.txt --target /deploy
RUN rm -rf __pycache__/
RUN zip -r function.zip *
CMD aws lambda update-function-code --function-name ask-TransitBuddy-default-ski-AlexaSkillFunctionDev-6C2D4kHwBgmA --zip-file fileb://function.zip