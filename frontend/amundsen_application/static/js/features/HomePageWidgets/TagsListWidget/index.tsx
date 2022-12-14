// Copyright Contributors to the Amundsen project.
// SPDX-License-Identifier: Apache-2.0

import * as React from 'react';

import TagsListContainer, { TagsListContainerProps } from 'features/Tags';


type TagsListWidgetProps = TagsListContainerProps;

class TagsListWidget extends React.Component<TagsListWidgetProps> {
    render() {
        return(
            <div><TagsListContainer shortTagsList /></div>
        );
    }
}

export default TagsListWidget;