# How to track Amundsen user metric

After you have deployed Amundsen into production, you want to track how user interacts with Amundsen for various reasons.

The easier way is to leverage [Google Analytics](https://analytics.google.com/analytics/web/) for basic user tracking. You could first
get the analytics token for your domain and put it as the [frontend config](https://github.com/amundsen-io/amundsenfrontendlibrary/blob/54de01bdc574665316f0517aefbd55cf7ca37ef0/amundsen_application/static/js/config/config-default.ts#L22)


Besides implementing Google Analytics, we provide a way called `action_logging` to do fine grained user action tracking.
The `action_logging` is a decorator to allow you to integrate user info and pipe it to your inhouse event tracking system(e.g Kafka).

You need to put the custom method into entry_points following this
[example](https://github.com/amundsen-io/amundsenfrontendlibrary/blob/54de01bdc574665316f0517aefbd55cf7ca37ef0/docs/configuration.md#action-logging).

And here is the IDL proto we used at Lyft to send the event message:
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

1. WAU

Sample query if the event table named as `default.event_amundsenfrontend_user_action`
```
SELECT date_trunc('week', CAST("ds" AS TIMESTAMP)) AS "__timestamp",
   COUNT(DISTINCT user_value) AS "count_distinct_active_users"
FROM
(SELECT *
FROM default.event_amundsenfrontend_user_action
WHERE ds > '2019-09-01') AS "expr_qry"
WHERE "ds" >= '2020-04-21 00:00:00.000000'
AND "ds" <= '2020-10-21 05:31:14.000000'
GROUP BY date_trunc('week', CAST("ds" AS TIMESTAMP))
ORDER BY "count_distinct_active_users" DESC
LIMIT 10000
```

2. DAU

Sample query if the event table named as `default.event_amundsenfrontend_user_action`
```
SELECT date_trunc('day', CAST("ds" AS TIMESTAMP)) AS "__timestamp",
   COUNT(DISTINCT user_value) AS "count_distinct_active_users"
FROM
(SELECT *
FROM default.event_amundsenfrontend_user_action
WHERE ds > '2019-09-01') AS "expr_qry"
WHERE "ds" >= '2020-07-21 00:00:00.000000'
AND "ds" <= '2020-10-21 00:00:00.000000'
GROUP BY date_trunc('day', CAST("ds" AS TIMESTAMP))
ORDER BY "count_distinct_active_users" DESC
LIMIT 50000
```

You could also exclude weekends:
```
SELECT date_trunc('day', CAST("ds" AS TIMESTAMP)) AS "__timestamp",
   COUNT(DISTINCT user_value) AS "count_distinct_active_users"
FROM
(SELECT *
FROM default.event_amundsenfrontend_user_action
WHERE ds > '2019-09-01') AS "expr_qry"
WHERE "ds" >= '2020-04-21 00:00:00.000000'
AND "ds" <= '2020-10-21 05:33:11.000000'
AND day_of_week(logged_at) NOT IN (6,
                                 7)
GROUP BY date_trunc('day', CAST("ds" AS TIMESTAMP))
ORDER BY "count_distinct_active_users" DESC
LIMIT 50000
```

3. User Penetration per role

Sample query if the event table named as `default.event_amundsenfrontend_user_action` and a table for user:
```
SELECT "title" AS "title",
   COUNT(DISTINCT email) * 100 / MAX(role_count) AS "penetration_percent"
FROM
(SELECT e.occurred_at,
      u.email,
      u.title,
      tmp.role_count
FROM default.family_user u
JOIN default.event_amundsenfrontend_user_action e ON u.email = e.user_value
JOIN
 (SELECT title,
         count(*) role_count
  FROM default.family_user
  GROUP BY 1) as tmp ON u.title = tmp.title
where ds is not NULL) AS "expr_qry"
WHERE "occurred_at" >= from_iso8601_timestamp('2020-10-14T00:00:00.000000')
AND "occurred_at" <= from_iso8601_timestamp('2020-10-21T00:00:00.000000')
AND "role_count" > 20
GROUP BY "title"
ORDER BY "penetration_percent" DESC
LIMIT 100
```

4. Usage breakdown per role_count

sample query:
```
SELECT "title" AS "title",
   count("email") AS "COUNT(email)"
FROM
(SELECT e.occurred_at,
      u.email,
      u.title,
      tmp.role_count
FROM default.family_user u
JOIN default.event_amundsenfrontend_user_action e ON u.email = e.user_value
JOIN
 (SELECT title,
         count(*) role_count
  FROM default.family_user
  GROUP BY 1) as tmp ON u.title = tmp.title
where ds is not NULL) AS "expr_qry"
WHERE "occurred_at" >= from_iso8601_timestamp('2020-10-14T00:00:00.000000')
AND "occurred_at" <= from_iso8601_timestamp('2020-10-21T00:00:00.000000')
GROUP BY "title"
ORDER BY "COUNT(email)" DESC
LIMIT 15
```

5. search click through rate

sample query:
```
SELECT date_trunc('day', CAST("occurred_at" AS TIMESTAMP)) AS "__timestamp",
   SUM(CASE
           WHEN CAST(json_extract_scalar(keyword_args_json, '$.index') AS BIGINT) <= 3 THEN 1
           ELSE 0
       END) * 100 / COUNT(*) AS "click_through_rate"
FROM
(SELECT *
FROM default.event_amundsenfrontend_user_action
WHERE ds > '2019-09-01') AS "expr_qry"
WHERE "occurred_at" >= from_iso8601_timestamp('2020-09-21T00:00:00.000000')
AND "occurred_at" <= from_iso8601_timestamp('2020-10-21T00:00:00.000000')
AND "command" IN ('_get_table_metadata',
                '_get_dashboard_metadata',
                '_log_get_user')
AND json_extract_scalar(keyword_args_json, '$.source') IN ('search_results',
                                                         'inline_search')
GROUP BY date_trunc('day', CAST("occurred_at" AS TIMESTAMP))
ORDER BY "click_through_rate" DESC
LIMIT 10000
```

6. Top 50 active user

7. Top search term

8. Top popular tables

9. Search click index

10. Metadata edits

11. Metadata edit leaders

12. Amundsen user per role (by joining with employee data)

13. ...
