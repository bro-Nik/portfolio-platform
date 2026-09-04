import { defineConfig } from 'orval';

export default defineConfig({
  portfolio: {
    input: '../../openapi.json',
    output: {
      target: './src/api/generated',
      schemas: './src/api/generated',
      client: 'axios',
      mode: 'tags-split',
      clean: true,
      prettier: false,
      override: {
        mutator: {
          path: './src/api/mutator.ts',
          name: 'mutator',
        },
      },
    },
  },
});
