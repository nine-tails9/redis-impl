# Redis Implementation

Its an implementation of some basic functionalities of Redis. [Playground link](https://redis-impl.herokuapp.com/)

## Installation

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install the app.

```bash
pip install -r requirements.txt
```

## Apis
* Get - Returns value of key if present
> Endpoint - /get
>> Request Type - GET
>>> Expected Request - /get?key=xyz
* SET
> Endpoint - /set
>> Request Type - POST
>>> Request should contain payload as - {"key": "abc", value:"xyz"}
* Delete - Deletes the key
> Endpoint - /delete
>> Request Type - GET
>>> Expected Request - /delete?key=xyz
* Expire - Sets expiry time of a key
> Endpoint - /set-expiry
>> Request Type - POST
>>> Request should contain payload as - {"key": "1","expiry": "5"} where expiry is in seconds
* Zadd - Adds key to sorted set
> Endpoint - /zadd
>> Request Type - POST
>>> Request should contain payload as - {"key": "abc", value:"xyz"}
* Zrank - Returns Rank of key in sorted set
> Endpoint - /zrank
>> Request Type - GET
>>> Expected Request - /zrank?key=xyz
* Zrange - Returns Values of elements in index range start to end from sorted set
> Endpoint - /zrange
>> Request Type - GET
>>> Expected Request - /zrange?start=1&end=3
```
