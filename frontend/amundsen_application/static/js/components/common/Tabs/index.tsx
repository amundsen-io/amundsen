import * as React from 'react';
import { Tab, Tabs } from 'react-bootstrap';

import './styles.scss';

export interface TabsProps {
  tabs: TabInfo[];

  defaultTab?: string;
  onSelect?: (key: string) => void;
}

interface TabInfo {
  content: JSX.Element;
  key: string;
  title: string;
}

const TabsComponent: React.SFC<TabsProps> = ({tabs, defaultTab, onSelect}) => {
  return (
      <Tabs
        id="tab"
        className="tabs-component"
        defaultActiveKey={ defaultTab }
        onSelect={ onSelect }
      >
        {
          tabs.map((tab) => {
            return (
              <Tab title={ tab.title } eventKey={ tab.key } key={ tab.key }>
                { tab.content }
              </Tab>
            )
          })
        }
      </Tabs>
    )
};

export default TabsComponent;
