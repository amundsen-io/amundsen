module.exports = {
  coverageThreshold: {
      './js/config': {
          branches: 0, // ??
          functions: 0, // ??
          lines: 0, // ??
          statements: 0, // ??
      },
      './js/components': {
          branches: 15, // 75
          functions: 25, // 75
          lines: 25, // 75
          statements: 25, // 75
      },
      './js/ducks': {
          branches: 0, // 75
          functions: 0, // 75
          lines: 0, // 75
          statements: 0, // 75
      },
      './js/fixtures': {
          branches: 100,
          functions: 100,
          lines: 100,
          statements: 100,
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
