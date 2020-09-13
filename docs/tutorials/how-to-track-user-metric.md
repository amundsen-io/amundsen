# How to track Amundsen user metric

After you have deployed Amundsen into production, you want to track how user interacts with Amundsen for various reasons. 

The easier way is to leverage [google analytics](https://analytics.google.com/analytics/web/) for basic user tracking. You could first
get the analytics token for your domain and put it as the [frontend config(https://github.com/amundsen-io/amundsenfrontendlibrary/blob/master/amundsen_application/static/js/config/config-default.ts#L22)


Besides implementing the google analytics, we provide a way called `action_logging` to do fine grain user action tracking. 
The `action_logging` is a decorator to allow you to integrate user info and pipe it to your inhouse event tracking system(e.g Kafka).

You need to put the custom method into entry_points following this 
[example](https://github.com/amundsen-io/amundsenfrontendlibrary/blob/54de01bdc574665316f0517aefbd55cf7ca37ef0/docs/configuration.md#action-logging).

And here is the IDL proto we used at Lyft to send the event message
```bash
message UserAction {
    // Sending host name
    google.protobuf.StringValue host_name = 1;
    // start time in epoch ms
    google.protobuf.Int64Value start_epoch_ms = 2;
    // end time in epoch ms
    google.protobuf.Int64Value end_epoch_ms = 3;
    // json array contains positional arguments
    common.LongString pos_args_json = 4;
    // json object contains key word arguments
    common.LongString keyword_args_json = 5;
    // json object contains output of command
    common.LongString output = 6;
    // an error message or exception stacktrace
    common.LongString error = 7;
    // `user`
    google.protobuf.StringValue user = 8;
}
```

It matches the action log model defined in [here](https://github.com/amundsen-io/amundsenfrontendlibrary/blob/ccfd2d6b82957fef347e956b243e4048c191fc0d/amundsen_application/log/action_log_model.py).

Once you have the event in your data warehouse, you could start building different KPI user metric:
- WAU
- DAU
- Top 50 active user
- Top search term
- Top popular tables
- Search click index
- Metadata edits
- Metadata edit leaders
- Amundsen user per role (by joining with employee data)
- ...

