// Copyright Contributors to the Amundsen project.
// SPDX-License-Identifier: Apache-2.0

import * as React from 'react';
import { bindActionCreators } from 'redux';
import { connect } from 'react-redux';
import { RouteComponentProps } from 'react-router';
import { FeatureMetadata } from 'interfaces/Feature';

interface StateFromProps {
  isLoading: boolean;
  statusCode: number | null;
  featureMetadata: FeatureMetadata;
}

export interface DispatchFromProps {
  getFeature: () => void;
}

export type FeaturePageProps = StateFromProps & DispatchFromProps;

const FeaturePage: React.FC<FeaturePageProps> = ({
  isLoading,
  statusCode,
  featureMetadata,
  getFeature,
}: FeaturePageProps) => null;
