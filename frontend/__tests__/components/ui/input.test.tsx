import { render, screen, fireEvent } from '@testing-library/react';
import { Input } from '@/components/ui/input';

describe('Input Component', () => {
  it('renders input element', () => {
    render(<Input placeholder="Enter text" />);
    expect(screen.getByPlaceholderText('Enter text')).toBeInTheDocument();
  });

  it('renders label when provided', () => {
    render(<Input label="Username" />);
    expect(screen.getByText('Username')).toBeInTheDocument();
  });

  it('does not render label when not provided', () => {
    render(<Input placeholder="test" />);
    expect(screen.queryByRole('label')).not.toBeInTheDocument();
  });

  it('renders error message when provided', () => {
    render(<Input error="This field is required" />);
    expect(screen.getByText('This field is required')).toBeInTheDocument();
  });

  it('applies error styles when error is present', () => {
    render(<Input error="Error" data-testid="error-input" />);
    const input = screen.getByTestId('error-input');
    expect(input).toHaveClass('border-red-500');
  });

  it('renders icon when provided', () => {
    render(<Input icon={<span data-testid="icon">@</span>} />);
    expect(screen.getByTestId('icon')).toBeInTheDocument();
  });

  it('applies left padding when icon is present', () => {
    render(<Input icon={<span>@</span>} data-testid="icon-input" />);
    const input = screen.getByTestId('icon-input');
    expect(input).toHaveClass('pl-10');
  });

  it('handles onChange events', () => {
    const handleChange = jest.fn();
    render(<Input onChange={handleChange} data-testid="input" />);

    fireEvent.change(screen.getByTestId('input'), { target: { value: 'test' } });
    expect(handleChange).toHaveBeenCalled();
  });

  it('updates value correctly', () => {
    render(<Input data-testid="input" />);
    const input = screen.getByTestId('input') as HTMLInputElement;

    fireEvent.change(input, { target: { value: 'hello' } });
    expect(input.value).toBe('hello');
  });

  it('is disabled when disabled prop is true', () => {
    render(<Input disabled data-testid="input" />);
    expect(screen.getByTestId('input')).toBeDisabled();
  });

  it('applies disabled styles when disabled', () => {
    render(<Input disabled data-testid="input" />);
    expect(screen.getByTestId('input')).toHaveClass('disabled:opacity-50');
  });

  it('uses text type by default', () => {
    render(<Input data-testid="input" />);
    expect(screen.getByTestId('input')).toHaveAttribute('type', 'text');
  });

  it('accepts different input types', () => {
    render(<Input type="password" data-testid="input" />);
    expect(screen.getByTestId('input')).toHaveAttribute('type', 'password');
  });

  it('accepts email type', () => {
    render(<Input type="email" data-testid="input" />);
    expect(screen.getByTestId('input')).toHaveAttribute('type', 'email');
  });

  it('accepts number type', () => {
    render(<Input type="number" data-testid="input" />);
    expect(screen.getByTestId('input')).toHaveAttribute('type', 'number');
  });

  it('applies custom className', () => {
    render(<Input className="custom-class" data-testid="input" />);
    expect(screen.getByTestId('input')).toHaveClass('custom-class');
  });

  it('applies glassmorphism styles', () => {
    render(<Input data-testid="input" />);
    const input = screen.getByTestId('input');
    expect(input).toHaveClass('backdrop-blur-sm');
    expect(input).toHaveClass('bg-white/70');
    expect(input).toHaveClass('rounded-xl');
  });

  it('forwards additional props', () => {
    render(<Input data-testid="input" aria-label="test input" maxLength={50} />);
    const input = screen.getByTestId('input');
    expect(input).toHaveAttribute('aria-label', 'test input');
    expect(input).toHaveAttribute('maxLength', '50');
  });
});
