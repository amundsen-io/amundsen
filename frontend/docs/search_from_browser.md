# Search From Browser
We can expose Amundsen search to web browsers to allow searching Amundsen directly from the address bar.
We do this by following the [OpenSearch standard](https://datacadamia.com/web/search/opensearch) and including an `opensearch.xml` file to describe
how to template a search URL.

We link to this file from `index.html` as long as the FRONTEND_BASE config [variable](https://github.com/amundsen-io/amundsen/blob/main/frontend/amundsen_application/config.py#L58) is set.
Browsers will automatically follow this link and add Amundsen as a custom search engine. In Chrome these are viewable in `chrome://settings/searchEngines`.
