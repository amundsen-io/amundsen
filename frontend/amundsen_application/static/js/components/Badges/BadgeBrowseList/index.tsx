// Copyright Contributors to the Amundsen project.
// SPDX-License-Identifier: Apache-2.0

import * as React from "react";
import {Badge} from "interfaces/Badges";
import BadgeList from "features/BadgeList";
import "./styles.scss";
import {AVAILABLE_BADGES_TITLE, BROWSE_BADGES_TITLE} from "components/Badges/BadgeBrowseList/constants";

export interface BadgeBrowseListProps {
  badges: Badge[];
}

export class BadgeBrowseListShort extends React.Component<BadgeBrowseListProps> {
    render() {
        return (
            <article className="badges-browse-section badges-browse-section-short">
                <h2 className="available-badges-header-title">{AVAILABLE_BADGES_TITLE}</h2>
                <BadgeList badges={this.props.badges} />
            </article>
        )
    }
}

export class BadgeBrowseListLong extends React.Component<BadgeBrowseListProps> {
    render() {
        return (
            <article className="badges-browse-section badges-browse-section-long">
                <h1 className="header-title">{BROWSE_BADGES_TITLE}</h1>
                <hr className="header-hr"/>
                <label className="section-label">
                    <span className="section-title title-2">{AVAILABLE_BADGES_TITLE}</span>
                </label>
                <BadgeList badges={this.props.badges} />
            </article>
        )
    }
}