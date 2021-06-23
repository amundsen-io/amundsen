// Copyright Contributors to the Amundsen project.
// SPDX-License-Identifier: Apache-2.0

import * as React from 'react';
import { FeatureCode } from 'interfaces/Feature';

import './styles.scss';

type GenerationCodeProps = {
  isLoading: boolean;
  featureCode: FeatureCode;
};

const LazyComponent = React.lazy(() => import('features/CodeBlock/index'));

export const GenerationCodeLoader = () => (
  <div className="shimmer-block">
    <div className="shimmer-line shimmer-line--1 is-shimmer-animated" />
    <div className="shimmer-line shimmer-line--2 is-shimmer-animated" />
    <div className="shimmer-line shimmer-line--3 is-shimmer-animated" />
    <div className="shimmer-line shimmer-line--4 is-shimmer-animated" />
    <div className="shimmer-line shimmer-line--5 is-shimmer-animated" />
    <div className="shimmer-line shimmer-line--6 is-shimmer-animated" />
  </div>
);

export const GenerationCode: React.FC<GenerationCodeProps> = ({
  isLoading,
  featureCode,
}) => {
  if (isLoading) {
    return <GenerationCodeLoader />;
  }
  return (
    <div className="generation-code">
      <React.Suspense fallback={<GenerationCodeLoader />}>
        <LazyComponent text={featureCode.text} />
      </React.Suspense>
    </div>
  );
};
