import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import SpacesPage from './page';
import { api, ApiError } from '@/lib/api';
import { toast } from 'sonner';

// Mock the API calls
jest.mock('@/lib/api', () => ({
  api: {
    get: jest.fn(),
    post: jest.fn(),
  },
  ApiError: jest.fn((message, code, status) => {
    const error = new Error(message);
    // @ts-ignore
    error.code = code;
    // @ts-ignore
    error.status = status;
    return error;
  }),
}));

// Mock sonner toast
jest.mock('sonner', () => ({
  toast: {
    success: jest.fn(),
    error: jest.fn(),
  },
}));

describe('SpacesPage', () => {
  const mockSites = [{ id: 'site-1', name: 'Site A', monthly_base_price: 100, daily_base_price: 10 }];
  const mockTags = [{ id: 'tag-1', name: 'Tag A', color: '#FF0000' }];
  const mockSpaces = [
    {
      id: 'space-1',
      site_id: 'site-1',
      name: 'A-01',
      status: 'available',
      tags: ['Tag A'],
      site_name: 'Site A',
      effective_monthly_price: 100,
      price_tier: 'site',
      created_at: '', updated_at: ''
    },
  ];

  beforeEach(() => {
    (api.get as jest.Mock).mockClear();
    (api.post as jest.Mock).mockClear();
    (toast.success as jest.Mock).mockClear();
    (toast.error as jest.Mock).mockClear();

    // Default mock for API GET calls
    (api.get as jest.Mock).mockImplementation((url: string) => {
      if (url.includes('/api/v1/sites')) {
        return Promise.resolve(mockSites);
      }
      if (url.includes('/api/v1/tags')) {
        return Promise.resolve(mockTags);
      }
      if (url.includes('/api/v1/spaces')) {
        return Promise.resolve(mockSpaces);
      }
      return Promise.reject(new Error('Unknown API GET endpoint'));
    });
  });

  it('displays a toast error when creating a duplicate space name', async () => {
    // Mock the API POST call to simulate a 409 Conflict
    (api.post as jest.Mock).mockRejectedValue(
      new ApiError('此場地已存在同名車位', 'conflict', 409)
    );

    render(<SpacesPage />);

    // Wait for initial data loading and the "新增車位" button to be available
    const addSpaceButton = await screen.findByRole('button', { name: '新增車位' });
    fireEvent.click(addSpaceButton);

    // Wait for the dialog to open
    await waitFor(() => expect(screen.getByRole('dialog')).toBeInTheDocument());

    // Select a site
    fireEvent.click(screen.getByText('選擇停車場')); // Open the select
    const siteAOption = await screen.findByRole('option', { name: 'Site A' });
    fireEvent.click(siteAOption);

    // Fill in the space name
    fireEvent.change(screen.getByLabelText('車位名稱'), {
      target: { value: 'DUPE-01' },
    });

    // Submit the form
    fireEvent.click(screen.getByRole('button', { name: '新增' }));

    // Assert that the toast error is displayed
    await waitFor(() => {
      expect(toast.error).toHaveBeenCalledWith('此場地已存在同名車位');
    });

    // Optionally, check if the dialog is still open or closed
    // expect(screen.getByRole('dialog')).toBeInTheDocument(); // Depends on desired UX
  });
});
