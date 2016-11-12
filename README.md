# IP Address Logger Using Dynamo DB
```
python3 -mvenv ~/venvs/ip
. ~/venvs/ip/bin/activate
pip install -r requirements.txt
cp credentials.json.sample credentials.json
```

- edit credentials.json to add the user and pass you want to use
- make sure AWS keys are in environment or config file
- create dynamodb table ip_log (hash key: location sort key: date)

```
python ip.py
```
- browse to localhost:5000

## Questions?
Github: [@thoolihan](https://github.com/thoolihan)
Twitter: [@thoolihan](https://twitter.com/thoolihan)
