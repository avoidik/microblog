# API Endpoints


## Tokens

### Create new token

```
POST http://localhost:5000/api/tokens
```

Parameters:
```
Basic-auth login & password
```

### Revoke token

```
DELETE http://localhost:5000/api/tokens
```

Parameters:
```
Basic-auth login & password
```

## Users

### Get all users

```
GET http://localhost:5000/api/users
```

Token required

### Get one user

```
GET http://localhost:5000/api/users/1
```

Token required

### Get followers for user

```
GET http://localhost:5000/api/users/1/followers
```

Token required

### Get followed for user

```
GET http://localhost:5000/api/users/1/followed
```

Token required

### Create new user

```
POST http://localhost:5000/api/users
```

Token not required

Parameters:
```
{
    "username": "blah",
    "password": "blah",
    "email": "blah@blah.com",
    "about_me": "cool guy"
}
```

### Update user

```
PUT http://localhost:5000/api/users/1
```

Token required

Parameters:
```
{
    "username": "blah",
    "password": "blah",
    "email": "blah@blah.com",
    "about_me": "cool guy"
}
```
