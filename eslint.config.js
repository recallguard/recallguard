import react from 'eslint-plugin-react';
import babelParser from '@babel/eslint-parser';

export default [
  {
    files: ['**/*.js', '**/*.jsx'],
    languageOptions: {
      parser: babelParser,
      ecmaVersion: 'latest',
      sourceType: 'module',
      parserOptions: { requireConfigFile: false, babelOptions: { presets: ['@babel/preset-react'] } }
    },
    plugins: { react },
    rules: {},
    settings: { react: { version: 'detect' } }
  }
];
