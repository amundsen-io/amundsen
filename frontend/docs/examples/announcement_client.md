# Overview

Amundsen's announcement feature requires that developers create a custom implementation of `announcement_client` for collecting announcements. This feature provide ability to deliver to Users announcements of different sort regarding data discovery service.

## Implementation

Implement the `announcement_client` to make a request to system storing announcements.

### Shared Logic
[`announcement_client`](https://github.com/lyft/amundsenfrontendlibrary/tree/master/amundsen_application/base/base_announcement_client.py) implements `_get_posts()` of `base_announcement_client` with the minimal logic for this use case.

It collects the posts from `get_posts()` method.

```python
try:
    announcements = self.get_posts()
except Exception as e:
    message = 'Encountered exception getting posts: ' + str(e)
    return _create_error_response(message)
```

It verifies the shape of the data before returning it to the application. If the data does not match the `AnnouncementsSchema`, the request will fail.

```python
# validate the returned object
data, errors = AnnouncementsSchema().dump(announcements)
if not errors:
    payload = jsonify({'posts': data.get('posts'), 'msg': 'Success'})
    return make_response(payload, HTTPStatus.OK)
else:
    message = 'Announcement data dump returned errors: ' + str(errors)
    return _create_error_response(message)
```

### Custom Logic
`announcement_client` has an abstract method `get_posts()`. 

This method will contain whatever custom logic is needed to collect announcements. The system within which they are stored can be anything that has programmatic access.

Announcements could be collected from database (as in exemplary SQLAlchemyAnnouncementClient), kafka persistent topic, web rss feed, etc.

See the following [`example_announcement_client`](https://github.com/lyft/amundsenfrontendlibrary/tree/master/amundsen_application/base/examples/example_announcement_client.py) for an example implementation of `base_announcement_client` and `get_posts()`. This example assumes a temporary sqlite database with no security, authentication, persistence or authorization configured.

## Usage

Under the `[announcement_client]` group, point the `announcement_client` entry point in your local `setup.py` to your custom class.

```
entry_points="""
    ...

    [announcement_client]
    announcement_client_class = amundsen_application.base.examples.example_announcement_client:SQLAlchemyAnnouncementClient
"""
```
### What do I need to run exemplary announcement_client ?

Exemplary client requires installation of SQLAlchemy to run properly:

```bash
pip install SQLAlchemy==1.3.17
```

Run `python3 setup.py install` in your virtual environment and restart the application for the entry point changes to take effect
