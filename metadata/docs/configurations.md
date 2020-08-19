Most of the configurations are set through Flask [Config Class](https://github.com/amundsen-io/amundsenmetadatalibrary/blob/master/metadata_service/config.py).

#### USER_DETAIL_METHOD `OPTIONAL`
This is a method that can be used to get the user details from any third-party or custom system.
This custom function takes user_id as a parameter, and returns a dictionary consisting user details' fields defined in [UserSchema](https://github.com/amundsen-io/amundsencommon/blob/master/amundsen_common/models/user.py). 

Example:
```python

def get_user_details(user_id):
    user_info = {
        'email': 'test@email.com',
        'user_id': user_id,
        'first_name': 'Firstname',
        'last_name': 'Lastname',
        'full_name': 'Firstname Lastname',
    }
    return user_info

USER_DETAIL_METHOD = get_user_details
```

#### STATISTICS_FORMAT_SPEC `OPTIONAL`

This is a variable enabling possibility to reformat statistics displayed in UI.

The key is name of statistic and a value is a dictionary with optional keys:
* **new_name** - how to rename statistic (if absent proxy should default to old name)
* **format** - how to format numerical statistics (if absent, proxy should default to original format)
* **drop** - should given statistic not be displayed in UI (if absent, proxy should keep it)

Example (if you're using [deeque](https://aws.amazon.com/blogs/big-data/test-data-quality-at-scale-with-deequ/) library), you might want to:
```python
STATISTICS_FORMAT_SPEC = {
        'stdDev': dict(new_name='standard deviation', format='{:,.2f}'),
        'mean': dict(format='{:,.2f}'),
        'maximum': dict(format='{:,.2f}'),
        'minimum': dict(format='{:,.2f}'),
        'completeness': dict(format='{:.2%}'),
        'approximateNumDistinctValues': dict(new_name='distinct values', format='{:,.0f}', ),
        'sum': dict(drop=True)
}
```
