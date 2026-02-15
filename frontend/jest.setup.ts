import '@testing-library/jest-dom';

// Mock scrollIntoView as it's not implemented in JSDOM
// This is often needed for UI libraries that interact with the DOM directly, like Radix UI (used by shadcn/ui Select)
if (typeof Element !== 'undefined') {
  Element.prototype.scrollIntoView = jest.fn();
}