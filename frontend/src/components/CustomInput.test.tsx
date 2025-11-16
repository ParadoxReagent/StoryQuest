/**
 * Tests for CustomInput Component
 */

import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import CustomInput from './CustomInput';

describe('CustomInput', () => {
  it('initially renders as collapsed button', () => {
    const onSubmit = vi.fn();
    render(<CustomInput onSubmit={onSubmit} />);

    expect(screen.getByText('Or type your own idea!')).toBeInTheDocument();
    expect(screen.queryByRole('textbox')).not.toBeInTheDocument();
  });

  it('expands when button is clicked', async () => {
    const onSubmit = vi.fn();
    const user = userEvent.setup();
    render(<CustomInput onSubmit={onSubmit} />);

    const expandButton = screen.getByRole('button', { name: /type your own response/i });
    await user.click(expandButton);

    expect(screen.getByRole('textbox')).toBeInTheDocument();
    expect(screen.getByLabelText(/what would you like to do/i)).toBeInTheDocument();
  });

  it('shows character counter', async () => {
    const onSubmit = vi.fn();
    const user = userEvent.setup();
    render(<CustomInput onSubmit={onSubmit} maxLength={200} />);

    // Expand
    await user.click(screen.getByRole('button', { name: /type your own response/i }));

    expect(screen.getByText('200 characters left')).toBeInTheDocument();
  });

  it('updates character counter as user types', async () => {
    const onSubmit = vi.fn();
    const user = userEvent.setup();
    render(<CustomInput onSubmit={onSubmit} maxLength={200} />);

    // Expand
    await user.click(screen.getByRole('button', { name: /type your own response/i }));

    const textarea = screen.getByRole('textbox');
    await user.type(textarea, 'Hello');

    expect(screen.getByText('195 characters left')).toBeInTheDocument();
  });

  it('shows warning when characters are running low', async () => {
    const onSubmit = vi.fn();
    const user = userEvent.setup();
    render(<CustomInput onSubmit={onSubmit} maxLength={25} />);

    // Expand
    await user.click(screen.getByRole('button', { name: /type your own response/i }));

    const textarea = screen.getByRole('textbox');
    await user.type(textarea, 'This is a test');

    const counter = screen.getByText(/characters left/);
    expect(counter).toHaveClass('text-red-500');
  });

  it('disables submit button when input is empty', async () => {
    const onSubmit = vi.fn();
    const user = userEvent.setup();
    render(<CustomInput onSubmit={onSubmit} />);

    // Expand
    await user.click(screen.getByRole('button', { name: /type your own response/i }));

    const submitButton = screen.getByRole('button', { name: /submit custom input/i });
    expect(submitButton).toBeDisabled();
  });

  it('enables submit button when input has text', async () => {
    const onSubmit = vi.fn();
    const user = userEvent.setup();
    render(<CustomInput onSubmit={onSubmit} />);

    // Expand
    await user.click(screen.getByRole('button', { name: /type your own response/i }));

    const textarea = screen.getByRole('textbox');
    await user.type(textarea, 'I want to explore');

    const submitButton = screen.getByRole('button', { name: /submit custom input/i });
    expect(submitButton).not.toBeDisabled();
  });

  it('calls onSubmit with trimmed text when form is submitted', async () => {
    const onSubmit = vi.fn();
    const user = userEvent.setup();
    render(<CustomInput onSubmit={onSubmit} />);

    // Expand
    await user.click(screen.getByRole('button', { name: /type your own response/i }));

    const textarea = screen.getByRole('textbox');
    await user.type(textarea, '  I want to explore  ');

    const submitButton = screen.getByRole('button', { name: /submit custom input/i });
    await user.click(submitButton);

    expect(onSubmit).toHaveBeenCalledWith('I want to explore');
  });

  it('clears input and collapses after submission', async () => {
    const onSubmit = vi.fn();
    const user = userEvent.setup();
    render(<CustomInput onSubmit={onSubmit} />);

    // Expand
    await user.click(screen.getByRole('button', { name: /type your own response/i }));

    const textarea = screen.getByRole('textbox');
    await user.type(textarea, 'Test input');

    const submitButton = screen.getByRole('button', { name: /submit custom input/i });
    await user.click(submitButton);

    // Should collapse back to button
    expect(screen.getByText('Or type your own idea!')).toBeInTheDocument();
    expect(screen.queryByRole('textbox')).not.toBeInTheDocument();
  });

  it('collapses and clears when cancel is clicked', async () => {
    const onSubmit = vi.fn();
    const user = userEvent.setup();
    render(<CustomInput onSubmit={onSubmit} />);

    // Expand
    await user.click(screen.getByRole('button', { name: /type your own response/i }));

    const textarea = screen.getByRole('textbox');
    await user.type(textarea, 'Some text');

    const cancelButton = screen.getByRole('button', { name: /cancel custom input/i });
    await user.click(cancelButton);

    // Should collapse and not call onSubmit
    expect(screen.getByText('Or type your own idea!')).toBeInTheDocument();
    expect(onSubmit).not.toHaveBeenCalled();
  });

  it('does not submit when input is only whitespace', async () => {
    const onSubmit = vi.fn();
    const user = userEvent.setup();
    render(<CustomInput onSubmit={onSubmit} />);

    // Expand
    await user.click(screen.getByRole('button', { name: /type your own response/i }));

    const textarea = screen.getByRole('textbox');
    await user.type(textarea, '   ');

    const submitButton = screen.getByRole('button', { name: /submit custom input/i });
    expect(submitButton).toBeDisabled();
  });

  it('respects maxLength prop', async () => {
    const onSubmit = vi.fn();
    const user = userEvent.setup();
    render(<CustomInput onSubmit={onSubmit} maxLength={10} />);

    // Expand
    await user.click(screen.getByRole('button', { name: /type your own response/i }));

    const textarea = screen.getByRole('textbox') as HTMLTextAreaElement;
    expect(textarea).toHaveAttribute('maxLength', '10');

    expect(screen.getByText('10 characters left')).toBeInTheDocument();
  });

  it('is disabled when disabled prop is true', () => {
    const onSubmit = vi.fn();
    render(<CustomInput onSubmit={onSubmit} disabled={true} />);

    const button = screen.getByRole('button');
    expect(button).toBeDisabled();
  });

  it('disables textarea when disabled prop is true in expanded state', async () => {
    const onSubmit = vi.fn();
    const user = userEvent.setup();

    // Render enabled first
    const { rerender } = render(<CustomInput onSubmit={onSubmit} disabled={false} />);

    // Expand
    await user.click(screen.getByRole('button', { name: /type your own response/i }));

    // Re-render with disabled=true
    rerender(<CustomInput onSubmit={onSubmit} disabled={true} />);

    const textarea = screen.getByRole('textbox');
    expect(textarea).toBeDisabled();
  });
});
