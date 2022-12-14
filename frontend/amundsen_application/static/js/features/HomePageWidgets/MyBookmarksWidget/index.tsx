// Copyright Contributors to the Amundsen project.
// SPDX-License-Identifier: Apache-2.0

import * as React from 'react';

import MyBookmarks, { MyBookmarksProps } from 'features/MyBookmarks';

type MyBookmarksWidgetProps = MyBookmarksProps;

class MyBookmarksWidget extends React.Component<MyBookmarksWidgetProps> {
    render() {
        return(
            <div><MyBookmarks /></div>
        )
    }
}

export default MyBookmarksWidget;