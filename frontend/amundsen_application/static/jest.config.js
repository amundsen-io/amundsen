module.exports = {
  roots: [
    '<rootDir>/js',
  ],
  transform: {
    '^.+\\.tsx?$': 'ts-jest',
    '^.+\\.js$': 'babel-jest',
    '^.+\\.(css|scss)$': '<rootDir>/node_modules/jest-css-modules',
  },
  testRegex: '(/__tests__/.*|(\\.|/)(test|spec))\\.(j|t)sx?$',
  moduleFileExtensions: [
    'ts',
    'tsx',
    'js',
    'jsx',
    'json',
  ],
  globals: {
    'ts-jest': {
      diagnostics: false,
    },
  },
};
