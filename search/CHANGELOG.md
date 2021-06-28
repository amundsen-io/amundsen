## 2.6.0

### Feature
* Search service adding suport for AWS Elasticsearch (https://github.com/amundsen-io/amundsen/pull/1141)
* use chart_names in dashboard basic search (https://github.com/amundsen-io/amundsen/pull/1140)
* Atlas Dashboard Support (https://github.com/amundsen-io/amundsen/pull/1066)


### Fix
* remove a comment in the Search Service user model get_id function that conflicts with implementation (https://github.com/amundsen-io/amundsen/pull/1154)
* search_table API swagger file bug fix (https://github.com/amundsen-io/amundsen/pull/1120)
* aws config (https://github.com/amundsen-io/amundsen/pull/1167)

### Chore
* bump marshmallow to 3 (https://github.com/amundsen-io/amundsensearchlibrary/pull/192)
* refactor: shared dependencies unification (https://github.com/amundsen-io/amundsen/pull/1163)

# 2.5.1 and before

### Feature
* Add dashboard search filter support ([#112](https://github.com/amundsen-io/amundsensearchlibrary/issues/112)) ([`17c6739`](https://github.com/amundsen-io/amundsensearchlibrary/commit/17c673903e2db3b1145af69fb31659d7be185eb4))
* Use query parameter for basic search [AtlasProxy] ([#105](https://github.com/amundsen-io/amundsensearchlibrary/issues/105)) ([`9961fde`](https://github.com/amundsen-io/amundsensearchlibrary/commit/9961fdef30f5bcd467f05df65d4ac7f40130ef1e))

### Fix
* Add id field to Dashboard ([#174](https://github.com/amundsen-io/amundsensearchlibrary/issues/174)) ([`53634fa`](https://github.com/amundsen-io/amundsensearchlibrary/commit/53634fa355bee468341d391b2fd5291b4991fc38))
* Fix table post/put api bug ([#172](https://github.com/amundsen-io/amundsensearchlibrary/issues/172)) ([`38bccba`](https://github.com/amundsen-io/amundsensearchlibrary/commit/38bccba0dab00941aec9ae187c31a4251b586003))
* Fix dashboard model errors, change deprecated pytest function ([#160](https://github.com/amundsen-io/amundsensearchlibrary/issues/160)) ([`1304234`](https://github.com/amundsen-io/amundsensearchlibrary/commit/1304234d5f7bf2fb238ae9c0011d3265efa99ab7))

### Documentation
* Fix build and coverage status links in README.md ([#134](https://github.com/amundsen-io/amundsensearchlibrary/issues/134)) ([`1c95ff4`](https://github.com/amundsen-io/amundsensearchlibrary/commit/1c95ff4362dac5d3674c735244855186cf7fa744))
