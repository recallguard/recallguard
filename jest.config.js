export default {
  testEnvironment: 'jsdom',
  transform: {
    '^.+\\.[tj]sx?$': 'babel-jest'
  },
<<<<<<< HEAD
  moduleFileExtensions: ['js', 'jsx']
=======
  moduleFileExtensions: ['js', 'jsx'],
  setupFiles: ['./jest.setup.js']
>>>>>>> 9ced1687 (Improve recall fetching and add pagination tests)
};
