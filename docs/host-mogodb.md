1. Check if MongoDB Server is Running
Run: `sudo systemctl status mongod`
If it's inactive, start it: `sudo systemctl start mongod`

2. Verify MongoDB is Listening on Port 27017
`ss -tulnp | grep 27017`

3. Check MongoDB Config File:
```yaml
net:
  port: 27017
  bindIp: 127.0.0.1

```

4. Connects to a MongoDB instance running locally on your machine:
- Via cli: `mongosh`
- Via GUI:  MongoDB Compass (GUI)