import anysort from 'anysort';
import { addParameters } from '@storybook/react';

import '../css/styles.scss';

const categoriesOrder = [
  'Overview/Introduction',
  'Attributes/**',
  'Components/**',
];

addParameters({
  options: {
    showRoots: true,
    storySort: (previous, next) => {
      const [previousStory, previousMeta] = previous;
      const [nextStory, nextMeta] = next;

      return anysort(previousMeta.kind, nextMeta.kind, categoriesOrder);
    },
  },
});
