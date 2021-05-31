DEV=arn:aws:lambda:us-east-1:484461028173:function:ask-TransitBuddy-default-ski-AlexaSkillFunctionDev-6C2D4kHwBgmA
PROD=arn:aws:lambda:us-east-1:484461028173:function:ask-TransitBuddy-default-skillS-AlexaSkillFunction-TPHNA1SH5L3V

if [[ "$1" == "prod" ]]; then
    sed -i '' "s/$DEV/$PROD/" skill-package/skill.json
    ask deploy
else
    sed -i '' "s/$PROD/$DEV/" skill-package/skill.json
    docker build -t transitbuddy-alexa .
    docker run -v ${HOME}/.aws/credentials:/root/.aws/credentials:ro -it transitbuddy-alexa
fi