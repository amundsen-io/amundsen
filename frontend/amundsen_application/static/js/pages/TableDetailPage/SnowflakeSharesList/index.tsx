// Copyright Contributors to the Amundsen project.
// SPDX-License-Identifier: Apache-2.0
import React, { useState } from 'react';

import { ResourceType, TableResource } from 'interfaces/Resources';
import { SnowflakeTableShare } from 'interfaces/Snowflake';
import TableListItem from 'components/ResourceListItem/TableListItem';
import { getHighlightedTableMetadata } from 'components/ResourceListItem/MetadataHighlightList/utils';

import { TableMetadata } from 'interfaces/TableMetadata';
import { NO_SNOWFLAKE_SHARES_INFO } from '../constants';

import './styles.scss';

export interface SnowflakeSharesProps {
  shares: SnowflakeTableShare[];
  tableDetails?: TableMetadata;
}

export const SnowflakeSharesList: React.FC<SnowflakeSharesProps> = ({
  shares,
  tableDetails,
}: SnowflakeSharesProps) => {
  if (shares.length === 0) {
    return (
      <div className="resource-list">
        <div className="empty-message body-placeholder">{NO_SNOWFLAKE_SHARES_INFO}</div>
      </div>
    );
  }

  const [showModal, setShowModal] = useState(false);
  
  return (
    <>
      <div className="list-group">
        {shares.map((share, index) => {
          const logging = {
            index,
            source: `snowflake_table_shares_list`,
          };

          return (
            <div key={index}>
              <div className="share-item">
                <div className="share-info">
                  {share.owner_account}.{share.name}
                </div>
                {share.listing && (
                  <div className="listing-info">
                    <span>Listing:</span>
                    {/* {share.listing.title && ( */}
                      <div>
                        <div className=".name">{share.listing.name}</div>
                        <div className=".title">{share.listing.title}</div>
                        <div className=".subtitle">{share.listing.subtitle}</div>
                        <div className=".desc">{share.listing.description}</div>
                      </div>
                    {/* )} */}
                    {/* <button onClick={() => setShowModal(true)}>Open Modal</button> */}
                    {/* {showModal && (
                        <div>
                            <div className="modal-content">
                                API Data goes here
                                <button onClick={() => setShowModal(false)}>Close Modal</button>
                            </div>
                            <div onClick={() => setShowModal(false)} className="modal-background">

                            </div>
                        </div>
                    )}   */}
                  </div>              
                )}
              </div>
            </div>
          )
         })}
      </div>  
    </>
  );
};

export default SnowflakeSharesList;
