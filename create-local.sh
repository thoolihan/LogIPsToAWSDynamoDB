aws dynamodb create-table --table-name ip_log \
    --attribute-definitions AttributeName=location,AttributeType=S \
                            AttributeName=date,AttributeType=S \
    --key-schema AttributeName=location,KeyType=HASH \
                 AttributeName=date,KeyType=RANGE \
    --provisioned-throughput ReadCapacityUnits=5,WriteCapacityUnits=5 \
    --endpoint-url http://localhost:8000
