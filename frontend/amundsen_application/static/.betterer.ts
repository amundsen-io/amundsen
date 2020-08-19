import { typescript } from '@betterer/typescript';

export default {
  'strict null compilation': typescript('./tsconfig.json', {
    strictNullChecks: true,
  }),
};
