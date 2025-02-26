import React from 'react'

declare global {
  namespace JSX {
    interface IntrinsicElements {
      [elemName: string]: any;
    }
  }
}

// Add explicit declaration for jsx-runtime
declare module 'react/jsx-runtime' {
  export default React;
  export const jsx: typeof React.createElement;
  export const jsxs: typeof React.createElement;
  export const Fragment: typeof React.Fragment;
}
