/**
 * Tests for ChoiceButton Component
 */

import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import ChoiceButton from './ChoiceButton';
import type { Choice } from '../types/api';

describe('ChoiceButton', () => {
  const mockChoice: Choice = {
    choice_id: 'choice-1',
    text: 'Explore the cave',
  };

  it('renders choice text correctly', () => {
    const onClick = vi.fn();
    render(<ChoiceButton choice={mockChoice} onClick={onClick} />);

    expect(screen.getByText('Explore the cave')).toBeInTheDocument();
  });

  it('renders with correct aria-label', () => {
    const onClick = vi.fn();
    render(<ChoiceButton choice={mockChoice} onClick={onClick} />);

    const button = screen.getByRole('button');
    expect(button).toHaveAttribute('aria-label', 'Choice: Explore the cave');
  });

  it('calls onClick when clicked', async () => {
    const onClick = vi.fn();
    const user = userEvent.setup();
    render(<ChoiceButton choice={mockChoice} onClick={onClick} />);

    const button = screen.getByRole('button');
    await user.click(button);

    expect(onClick).toHaveBeenCalledTimes(1);
  });

  it('is disabled when disabled prop is true', () => {
    const onClick = vi.fn();
    render(<ChoiceButton choice={mockChoice} onClick={onClick} disabled={true} />);

    const button = screen.getByRole('button');
    expect(button).toBeDisabled();
  });

  it('does not call onClick when disabled and clicked', async () => {
    const onClick = vi.fn();
    const user = userEvent.setup();
    render(<ChoiceButton choice={mockChoice} onClick={onClick} disabled={true} />);

    const button = screen.getByRole('button');
    await user.click(button);

    expect(onClick).not.toHaveBeenCalled();
  });

  it('is enabled by default', () => {
    const onClick = vi.fn();
    render(<ChoiceButton choice={mockChoice} onClick={onClick} />);

    const button = screen.getByRole('button');
    expect(button).not.toBeDisabled();
  });
});
