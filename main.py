# Imports from Python
from datetime import date, datetime
from typing import Optional
from unittest import result
from uuid import UUID
import json

# Imports from Pydantic
from pydantic import BaseModel, EmailStr, Field

# Imports from FastAPI
from fastapi import Body, FastAPI, Path, status

app = FastAPI()

# Models
class UserBase(BaseModel):
    user_id: UUID = Field(...)
    email: EmailStr = Field(...)

class UserLogin(UserBase):
    password: str = Field(..., min_length=8, max_length=64)

class User(UserBase):
    first_name: str = Field(
                        ...,
                        min_length=1,
                        max_length=50                
                    )
    last_name: str = Field(
                        ...,
                        min_length=1,
                        max_length=50                
                    )
    birth_date: Optional[date] = Field(default=None)

class UserRegister(User, UserLogin):
    pass


class Tweet(BaseModel):
    tweet_id: UUID = Field(...)
    content: str = Field(
                        ..., 
                        min_length=1, 
                        max_length=256
                    )
    created_at: datetime = Field(default=datetime.now())
    updated_at: Optional[datetime] = Field(default=None)
    by: User = Field(...)

# Path Operations
## Users

### Register a User
@app.post(
            path="/signup",
            response_model=User,
            status_code=status.HTTP_201_CREATED,
            summary="Register a User",
            tags=["Users"]
        )
def signup(user: UserRegister = Body(...)):
    """
    Signup

    This Path Operation registar a user in the app

    Parameters:
    -   Request Body Parameter
        - user: UserRegister
    
    Returns a json with the basic user information
    - user_id: UUID
    - email: EmailStr
    - first_name: str
    - last_name: str
    - bith_date: date
    """    
    with open("users.json", "r+", encoding="utf-8") as f:
        results = json.loads(f.read())
        user_dict = user.dict()
        user_dict["user_id"] = str(user_dict["user_id"])
        user_dict["birth_date"] = str(user_dict["birth_date"])
        results.append(user_dict)
        f.seek(0)
        f.write(json.dumps(results))

    return user


### Login a User
@app.post(
            path="/login",
            response_model=User,
            status_code=status.HTTP_200_OK,
            summary="Login a User",
            tags=["Users"]
        )
def login():
    pass

### Show all Users
@app.get(
            path="/users",
            response_model=list[User],
            status_code=status.HTTP_200_OK,
            summary="Show all Users",
            tags=["Users"]
        )
def show_all_users():
    """
    Show All Users

    This path operations shows all users in the app

    Parameters:
    - None

    Returns:
    - Description: Returns a json list with all users in the app
    users: [
        {
    - user_id: UUID
    - email: EmailStr
    - first_name: str
    - last_name: str
    - bith_date: date
        }
    ]
    """    
    with open("users.json", "r", encoding="utf-8") as f:
        results = json.loads(f.read())
        return results

### Show a User By ID
@app.get(
            path="/users/{user_id}",
            response_model=User,
            status_code=status.HTTP_200_OK,
            summary="Show a User",
            tags=["Users"]
        )
def show_a_user(
                user_id: UUID = Path(
                    ...,
                    title="User UUID",
                    description="This is the User UUID",
                    example="3fa85f64-5717-4562-b3fc-2c963f66afa8")
                ):
    with open("users.json", "r", encoding="utf-8") as f:
        results = json.loads(f.read())
    user = [user for user in results if user["user_id"] == str(user_id)]
    return User(user_id=user[0]["user_id"], 
                email=user[0]["email"], 
                first_name=user[0]["first_name"], 
                last_name=user[0]["last_name"], 
                birth_date=user[0]["birth_date"])

### Delete a User
@app.delete(
            path="/users/{user_id}/delete",
            status_code=status.HTTP_200_OK,
            summary="Delete a User",
            tags=["Users"]
        )
def delete_a_user(user_id: UUID = Path(
                    ...,
                    title="User UUID",
                    description="This is the User UUID",
                    example="3fa85f64-5717-4562-b3fc-2c963f66afa8")):
    with open("users.json", "r", encoding="utf-8") as f:
        results = json.loads(f.read())
        results_with_user_deleted = [user for user in results if user["user_id"] != str(user_id) ]
        user_to_delete = [user for user in results if user["user_id"] == str(user_id) ]
    if len(user_to_delete) == 0:
        return {"mensaje": f"The User with {user_id} not found"}
    else:    
        with open("users.json", "w", encoding="utf-8") as f:
            f.seek(0)
            f.write(json.dumps(results_with_user_deleted))
        return {"mensaje": f"The User with {user_id} was deleted"}

### Update a User
@app.put(
            path="/users/{user_id}/update",
            response_model=User,
            status_code=status.HTTP_200_OK,
            summary="Update a User",
            tags=["Users"]
        )
def update_a_user(user_id: UUID = Path(
                    ...,
                    title="User UUID",
                    description="This is the User UUID",
                    example="3fa85f64-5717-4562-b3fc-2c963f66afa8"),
                    user: User = Body(...)):
    with open("users.json", "r", encoding="utf-8") as f:
        results = json.loads(f.read())
    user_new = user.dict()
    user_founded = [user for user in results if user["user_id"] == str(user_id)][0]
    index_user = results.index(user_founded)
    results[index_user]["email"] = str(user_new["email"])
    results[index_user]["fisrt_name"] = str(user_new["first_name"])
    results[index_user]["last_name"] = str(user_new["last_name"])
    results[index_user]["birth_date"] = str(user_new["birth_date"])
    with open("users.json", "w", encoding="utf-8") as f:
        f.write(json.dumps(results))
    return User(user_id=str(user_id),
                email=str(user_new["email"]),
                first_name=str(user_new["first_name"]),
                last_name=str(user_new["last_name"]),
                birth_date=str(user_new["birth_date"]))
## Tweets

### Show all Tweets
@app.get(
            path="/",
            response_model=list[Tweet],
            status_code=status.HTTP_200_OK,
            summary="Show all Tweets",
            tags=["Tweets"]
        )
def home():
    with open("tweets.json", "r", encoding="utf-8") as f:
        results = json.loads(f.read())
        return results

### Post Tweet
@app.post(
            path="/post",
            response_model=Tweet,
            status_code=status.HTTP_201_CREATED,
            summary="Post a Tweet",
            tags=["Tweets"]
        )
def post_tweet(tweet: Tweet = Body(...)):
    with open("tweets.json", "r+", encoding="utf-8") as f:
        results = json.loads(f.read())
        tweet_dict = tweet.dict()
        tweet_user_dict = tweet_dict["by"]

        tweet_dict["tweet_id"] = str(tweet_dict["tweet_id"])
        tweet_dict["created_at"] = str(tweet_dict["created_at"])
        tweet_dict["update_at"] = str(tweet_dict["update_at"])
        tweet_user_dict["user_id"] = str(tweet_user_dict["user_id"])
        tweet_user_dict["birth_date"] = str(tweet_user_dict["birth_date"])
        results.append(tweet_dict)
        f.seek(0)
        f.write(json.dumps(results))
        print(results)
        return tweet
        

### Show a Tweet
@app.get(
            path="/tweet/{tweet_id}",
            response_model=Tweet,
            status_code=status.HTTP_200_OK,
            summary="Show a Tweet",
            tags=["Tweets"]
        )
def show_tweet(tweet_id: UUID = Path(..., title="Tweet ID", description="Here you need put the tweet ID", example="3fab5f64-5717-4562-b3fc-2c963f66afa8")):
    with open("tweets.json", "r", encoding="utf-8") as f:
        results = json.loads(f.read())
    tweet = [tweet for tweet in results if tweet["tweet_id"] == str(tweet_id)]
    return Tweet(tweet_id=tweet[0]["tweet_id"],
                content=tweet[0]["content"],
                created_at=tweet[0]["created_at"],
                updated_at=tweet[0]["update_at"],
                by=tweet[0]["by"])

### Delete a Tweet
@app.delete(
                path="/tweet/{tweet_id}/delete",
                status_code=status.HTTP_204_NO_CONTENT,
                summary="Delete a Tweet",
                tags=["Tweets"]
            )
def delete_tweet(tweet_id: UUID = Path(..., title="Tweet ID", description="Here you need put the tweet ID", example="3fab5f64-5717-4562-b3fc-2c963f66afa8")):
    with open("tweets.json","r", encoding='utf-8') as f:
        results = json.loads(f.read())
        results_with_tweet_deleted = [tweet for tweet in results if tweet["tweet_id"] != str(tweet_id) ]
        tweet_to_delete = [tweet for tweet in results if tweet["tweet_id"] == str(tweet_id) ]
    if len(tweet_to_delete) == 0:
        return {"message": f"The Tweet with {tweet_id} ID not found"}
    else:
        with open("tweets.json", "w", encoding="utf-8") as f:
            f.seek(0)
            f.write(json.dumps(results_with_tweet_deleted))
        return {"message": f"The Tweet with {tweet_id} ID was deleted"}


### Update a Tweet
@app.put(
            path="/tweet/{tweet_id}/update",
            response_model=Tweet,
            status_code=status.HTTP_200_OK,
            summary="Update a Tweet",
            tags=["Tweets"]
        )
def update_tweet(tweet_id: UUID = Path(..., title="Tweet ID", description="Here you need put the tweet ID", example="3fab5f64-5717-4562-b3fc-2c963f66afa8"), tweet: Tweet = Body(...)):
    with open("tweets.json", "r", encoding="utf-8") as f:
        results = json.loads(f.read())
    tweet_new = tweet.dict()
    tweet_founded = [tweet for tweet in results if tweet["tweet_id"] == str(tweet_id)][0]
    index_tweet = results.index(tweet_founded)
    results[index_tweet]["content"] = str(tweet_new["content"])
    results[index_tweet]["created_at"] = str(tweet_new["created_at"])
    results[index_tweet]["update_at"] = str(tweet_new["update_at"])
    results[index_tweet]["by"]["user_id"] = str(tweet_new["by"]["user_id"])
    results[index_tweet]["by"]["email"] = str(tweet_new["by"]["email"])
    results[index_tweet]["by"]["first_name"] = str(tweet_new["by"]["first_name"])
    results[index_tweet]["by"]["last_name"] = str(tweet_new["by"]["last_name"])
    results[index_tweet]["by"]["birth_date"] = str(tweet_new["by"]["birth_date"])
    with open("tweets.json", "w", encoding="utf-8") as f:
        f.write(json.dumps(results))
    return Tweet(tweet_id=str(tweet_id),
                content=str(tweet_new["content"]),
                created_at=str(tweet_new["created_at"]),
                updated_at=str(tweet_new["update_at"]),
                by=tweet_new["by"])