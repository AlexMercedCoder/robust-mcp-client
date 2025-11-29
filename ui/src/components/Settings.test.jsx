import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { Settings } from './Settings';
import { vi, describe, it, expect, beforeEach, beforeAll } from 'vitest';

const fetchMock = vi.fn();

describe('Settings Component', () => {
  beforeAll(() => {
    vi.stubGlobal('fetch', fetchMock);
  });

  beforeEach(() => {
    fetchMock.mockClear();
    fetchMock.mockResolvedValue({
      ok: true,
      json: async () => ({
        provider: 'local',
        openai_key: '',
        gemini_key: '',
        anthropic_key: '',
        mcp_servers: []
      })
    });
  });

  it('renders settings form', async () => {
    render(<Settings onBack={() => {}} />);
    
    // Wait for initial fetch
    await waitFor(() => expect(fetchMock).toHaveBeenCalledTimes(1));
    
    expect(screen.getByText('Settings')).toBeInTheDocument();
  });

  it('submits form successfully', async () => {
    render(<Settings onBack={() => {}} />);
    
    await waitFor(() => expect(fetchMock).toHaveBeenCalledTimes(1));
    
    const input = screen.getByPlaceholderText('sk-...');
    fireEvent.change(input, { target: { value: 'test-key' } });
    
    const saveButton = screen.getByText('Save Settings');
    fireEvent.click(saveButton);
    
    await waitFor(() => {
      expect(fetchMock).toHaveBeenCalledWith('http://localhost:8000/api/config', expect.objectContaining({
        method: 'POST',
        body: expect.stringContaining('"openai_key":"test-key"')
      }));
    });
    
    expect(await screen.findByText('Settings saved successfully!')).toBeInTheDocument();
  });

  it('adds a new MCP server', async () => {
    render(<Settings onBack={() => {}} />);
    await waitFor(() => expect(fetchMock).toHaveBeenCalledTimes(1));
    
    const nameInput = screen.getByPlaceholderText('Name');
    fireEvent.change(nameInput, { target: { value: 'TestServer' } });
    
    const cmdInput = screen.getByPlaceholderText('Command (e.g., npx)');
    fireEvent.change(cmdInput, { target: { value: 'echo' } });
    
    const argsInput = screen.getByPlaceholderText('Args (space separated)');
    fireEvent.change(argsInput, { target: { value: 'hello' } });
    
    const addButton = screen.getByText('Add Server');
    fireEvent.click(addButton);
    
    expect(screen.getByText('TestServer')).toBeInTheDocument();
  });
});
