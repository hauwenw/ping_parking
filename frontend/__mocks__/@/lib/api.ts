import { jest } from '@jest/globals';
import { ApiError } from '@/lib/api'; // Assuming ApiError is exported from here

// Mock the entire api module
const mockApi = {
  get: jest.fn(),
  post: jest.fn(),
  put: jest.fn(),
  delete: jest.fn(),
};

export const api = mockApi;
export { ApiError };
