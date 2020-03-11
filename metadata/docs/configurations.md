Most of the configurations are set through Flask [Config Class](https://github.com/lyft/amundsenmetadatalibrary/blob/master/metadata_service/config.py).

#### USER_DETAIL_METHOD `OPTIONAL`
This is a method that can be used to get the user details from any third-party or custom system.
This custom function takes user_id  as a parameter, and returns a tuple consisting user details defined in [UserSchema](https://github.com/lyft/amundsencommon/blob/master/amundsen_common/models/user.py) along with the status code. 

Example:
```python

def get_user_details(user_id):
    from amundsen_common.models.user import UserSchema
    from http import HTTPStatus
    user_info = {
        'email': 'test@email.com',
        'user_id': user_id,
        'first_name': 'Firstname',
        'last_name': 'Lastname',
        'full_name': 'Firstname Lastname',
    }
    return UserSchema().dump(user_info).data, HTTPStatus.OK

USER_DETAIL_METHOD = get_user_details
```