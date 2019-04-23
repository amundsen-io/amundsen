module.exports = {
  coverageThreshold: {
      './js/components': {
          branches: 10, // 75
          functions: 10, // 75
          lines: 10, // 75
          statements: 10, // 75
      },
      './js/ducks': {
          branches: 0, // 75
          functions: 0, // 75
          lines: 0, // 75
          statements: 0, // 75
      },
  },
  roots: [
    '<rootDir>/js',
  ],
  setupFiles: [
    '<rootDir>/test-setup.ts',
  ],
  transform: {
    '^.+\\.tsx?$': 'ts-jest',
    '^.+\\.js$': 'babel-jest',
    '^.+\\.(css|scss)$': '<rootDir>/node_modules/jest-css-modules',
  },
  testRegex: '(/tests/.*|(\\.|/)(test|spec))\\.(j|t)sx?$',
  moduleDirectories: ['node_modules', 'js'],
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
