import * as React from 'react';

import { ResourceReport } from 'interfaces/index';
import { Dropdown } from 'react-bootstrap';

export interface ResourceReportProps {
  resourceReports: ResourceReport[];
}

const TableReportsDropdown: React.FC<ResourceReportProps> = ({
  resourceReports,
}: ResourceReportProps) => {
  if (!resourceReports || resourceReports.length < 1) {
    return null;
  }

  return (
    <Dropdown id="user-dropdown">
      <Dropdown.Toggle className="btn btn-default btn-lg">
        Reports
      </Dropdown.Toggle>
      <Dropdown.Menu className="profile-menu">
        {resourceReports.map((report) => (
          <li key={report.url}>
            <a target="_blank" rel="noreferrer" href={`${report.url}`}>
              {`${report.name}`}
            </a>
          </li>
        ))}
      </Dropdown.Menu>
    </Dropdown>
  );
};

export default TableReportsDropdown;
