import { render, screen, waitFor } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { beforeEach, describe, expect, it, vi } from 'vitest';

vi.mock('../src/services/api', () => ({
  getRepositories: vi.fn(),
  getPipelines: vi.fn().mockResolvedValue({ data: { total: 0 } }),
  createRepository: vi.fn(),
  deleteRepository: vi.fn(),
  formatApiError: (err) => err?.message || 'Hata',
  formatDate: (d) => d || '—',
}));

import { getRepositories } from '../src/services/api';
import RepositoriesPage from '../src/components/RepositoriesPage';

const mockRepos = [
  {
    id: 'r1',
    url: 'https://github.com/u/owned-repo',
    my_role: 'owner',
    default_branch: 'main',
    created_at: '2026-01-01',
  },
  {
    id: 'r2',
    url: 'https://github.com/t/member-repo',
    my_role: 'member',
    default_branch: 'main',
    created_at: '2026-01-01',
  },
];

describe('RepositoriesPage', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    getRepositories.mockResolvedValue({ data: mockRepos });
  });

  it('owner_section_visible', async () => {
    render(<MemoryRouter><RepositoriesPage /></MemoryRouter>);
    await waitFor(() => {
      expect(screen.getByText('Sahip Olduğum Repolar')).toBeInTheDocument();
    });
  });

  it('member_section_visible', async () => {
    render(<MemoryRouter><RepositoriesPage /></MemoryRouter>);
    await waitFor(() => {
      expect(screen.getByText('Üye Olduğum Repolar')).toBeInTheDocument();
    });
  });

  it('owned_repo_url_shown', async () => {
    render(<MemoryRouter><RepositoriesPage /></MemoryRouter>);
    await waitFor(() => {
      expect(screen.getByText('u/owned-repo')).toBeInTheDocument();
    });
  });

  it('role_badges_rendered', async () => {
    render(<MemoryRouter><RepositoriesPage /></MemoryRouter>);
    await waitFor(() => {
      expect(screen.getByText('Owner')).toBeInTheDocument();
      expect(screen.getByText('Member')).toBeInTheDocument();
    });
  });

  it('add_repo_button_exists', async () => {
    render(<MemoryRouter><RepositoriesPage /></MemoryRouter>);
    await waitFor(() => {
      expect(screen.getByText(/Repo Ekle/)).toBeInTheDocument();
    });
  });
});
