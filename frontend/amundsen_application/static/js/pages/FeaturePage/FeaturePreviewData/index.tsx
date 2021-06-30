// Copyright Contributors to the Amundsen project.
// SPDX-License-Identifier: Apache-2.0

import * as React from 'react';
import { PreviewData } from 'interfaces/PreviewData';

import './styles.scss';
import * as Constants from '../../TableDetailPage/DataPreviewButton/constants';

export type FeaturePreviewDataProps = {
  isLoading: boolean;
  previewData: PreviewData;
};

export const FeaturePreviewLoader = () => (
  <div className="shimmer-block">
    <div className="shimmer-line shimmer-line--1 is-shimmer-animated" />
    <div className="shimmer-line shimmer-line--2 is-shimmer-animated" />
    <div className="shimmer-line shimmer-line--3 is-shimmer-animated" />
    <div className="shimmer-line shimmer-line--4 is-shimmer-animated" />
    <div className="shimmer-line shimmer-line--5 is-shimmer-animated" />
    <div className="shimmer-line shimmer-line--6 is-shimmer-animated" />
  </div>
);

const getSanitizedValue = (value) => {
  // Display the string interpretation of the following "false-y" values
  // return 'Data Exceeds Render Limit' msg if column is too long
  let sanitizedValue = '';
  if (value === 0 || typeof value === 'boolean') {
    sanitizedValue = value.toString();
  } else if (typeof value === 'object') {
    sanitizedValue = JSON.stringify(value);
  } else {
    sanitizedValue = value;
  }

  if (sanitizedValue.length > Constants.PREVIEW_COLUMN_MAX_LEN) {
    return Constants.PREVIEW_COLUMN_MSG;
  }
  return sanitizedValue;
};

export const FeaturePreviewData: React.FC<FeaturePreviewDataProps> = ({
  isLoading,
  previewData,
}) => {
  if (isLoading) {
    return <FeaturePreviewLoader />;
  }
  if (!previewData) {
    return (
      <div className="feature-preview-data">
        <div className="empty-message" />
      </div>
    );
  }
  return (
    <div className="feature-preview-data">
      <div className="grid">
        {previewData.columns?.map((col, colId) => {
          const fieldName = col.column_name;
          return (
            <div key={fieldName} id={fieldName} className="grid-column">
              <div className="grid-cell grid-header subtitle-3">
                {fieldName.toUpperCase()}
              </div>
              {(previewData.data || []).map((row, rowId) => {
                const cellId = `${colId}:${rowId}`;
                const dataItemValue = getSanitizedValue(row[fieldName]);
                return (
                  <div key={cellId} className="grid-cell">
                    {dataItemValue}
                  </div>
                );
              })}
            </div>
          );
        })}
      </div>
    </div>
  );
};
