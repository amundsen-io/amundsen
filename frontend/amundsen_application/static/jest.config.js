module.exports = {
  coverageThreshold: {
    './js/config': {
      branches: 90,
      functions: 90,
      lines: 90,
      statements: 90,
    },
    './js/components': {
      branches: 60, // 75
      functions: 65, // 75
      lines: 65, // 75
      statements: 70, // 75
    },
    './js/ducks': {
      branches: 75,
      functions: 80,
      lines: 80,
      statements: 85,
    },
    './js/fixtures': {
      branches: 100,
      functions: 100,
      lines: 100,
      statements: 100,
    },
  },
  roots: ['<rootDir>/js'],
  setupFiles: ['<rootDir>/test-setup.ts'],
  transform: {
    '^.+\\.tsx?$': 'ts-jest',
    '^.+\\.js$': 'babel-jest',
  },
  testRegex: '(test|spec)\\.(j|t)sx?$',
  moduleDirectories: ['node_modules', 'js'],
  moduleFileExtensions: ['ts', 'tsx', 'js', 'jsx', 'json'],
  moduleNameMapper: {
    '^.+\\.(css|scss)$': '<rootDir>/node_modules/jest-css-modules',
  },
  globals: {
    'ts-jest': {
      diagnostics: false,
    },
  },
};
