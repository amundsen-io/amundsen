import React from 'react';

import Flag, { CaseType } from '.';

export default {
  title: 'Components/Flags',
  component: Flag,
};

export const SimpleFlag = () => {
  return <Flag caseType={CaseType.LOWER_CASE} text="Test Flag" />;
};

SimpleFlag.story = {
  name: 'simple flag',
};
