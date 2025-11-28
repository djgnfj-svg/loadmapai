import { describe, it, expect, vi } from 'vitest';
import { render, screen, waitFor } from '@/test/test-utils';
import userEvent from '@testing-library/user-event';
import { Toast, ToastContainer } from './Toast';

describe('Toast', () => {
  const defaultProps = {
    id: '1',
    type: 'success' as const,
    message: 'Test message',
    onClose: vi.fn(),
  };

  it('renders message', () => {
    render(<Toast {...defaultProps} />);
    expect(screen.getByText(/test message/i)).toBeInTheDocument();
  });

  it('renders success variant', () => {
    const { container } = render(<Toast {...defaultProps} type="success" />);
    expect(container.firstChild).toHaveClass('bg-green-50');
  });

  it('renders error variant', () => {
    const { container } = render(<Toast {...defaultProps} type="error" />);
    expect(container.firstChild).toHaveClass('bg-red-50');
  });

  it('renders warning variant', () => {
    const { container } = render(<Toast {...defaultProps} type="warning" />);
    expect(container.firstChild).toHaveClass('bg-yellow-50');
  });

  it('renders info variant', () => {
    const { container } = render(<Toast {...defaultProps} type="info" />);
    expect(container.firstChild).toHaveClass('bg-blue-50');
  });

  it('calls onClose when close button is clicked', async () => {
    const onClose = vi.fn();
    render(<Toast {...defaultProps} onClose={onClose} />);

    await userEvent.click(screen.getByRole('button'));

    await waitFor(() => {
      expect(onClose).toHaveBeenCalledWith('1');
    });
  });

  it('auto-closes after duration', async () => {
    const onClose = vi.fn();
    render(<Toast {...defaultProps} onClose={onClose} duration={100} />);

    await waitFor(
      () => {
        expect(onClose).toHaveBeenCalledWith('1');
      },
      { timeout: 500 }
    );
  });
});

describe('ToastContainer', () => {
  it('renders multiple toasts', () => {
    const toasts = [
      { id: '1', type: 'success' as const, message: 'Success message' },
      { id: '2', type: 'error' as const, message: 'Error message' },
    ];
    const onClose = vi.fn();

    render(<ToastContainer toasts={toasts} onClose={onClose} />);

    expect(screen.getByText(/success message/i)).toBeInTheDocument();
    expect(screen.getByText(/error message/i)).toBeInTheDocument();
  });

  it('renders empty when no toasts', () => {
    const { container } = render(<ToastContainer toasts={[]} onClose={vi.fn()} />);
    expect(container.firstChild).toBeEmptyDOMElement();
  });
});
