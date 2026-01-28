import { render, screen } from '@testing-library/react';
import { GlassCard } from '@/components/ui/glass-card';

describe('GlassCard Component', () => {
  it('renders children correctly', () => {
    render(<GlassCard>Card Content</GlassCard>);
    expect(screen.getByText('Card Content')).toBeInTheDocument();
  });

  it('applies default glassmorphism styles', () => {
    render(<GlassCard>Default</GlassCard>);
    const card = screen.getByText('Default').closest('div');
    expect(card).toHaveClass('backdrop-blur-xl');
    expect(card).toHaveClass('rounded-2xl');
    expect(card).toHaveClass('border');
  });

  it('applies default variant styles', () => {
    render(<GlassCard>Default</GlassCard>);
    const card = screen.getByText('Default').closest('div');
    expect(card).toHaveClass('bg-white/70');
  });

  it('applies elevated variant styles', () => {
    render(<GlassCard variant="elevated">Elevated</GlassCard>);
    const card = screen.getByText('Elevated').closest('div');
    expect(card).toHaveClass('bg-white/80');
    expect(card).toHaveClass('shadow-lg');
  });

  it('applies subtle variant styles', () => {
    render(<GlassCard variant="subtle">Subtle</GlassCard>);
    const card = screen.getByText('Subtle').closest('div');
    expect(card).toHaveClass('bg-white/50');
  });

  it('applies hover effects when hover prop is true', () => {
    render(<GlassCard hover>Hoverable</GlassCard>);
    const card = screen.getByText('Hoverable').closest('div');
    expect(card).toHaveClass('hover:scale-[1.02]');
  });

  it('does not apply hover effects by default', () => {
    render(<GlassCard>No Hover</GlassCard>);
    const card = screen.getByText('No Hover').closest('div');
    expect(card).not.toHaveClass('hover:scale-[1.02]');
  });

  it('applies glow effects when glow prop is true', () => {
    render(<GlassCard glow>Glowing</GlassCard>);
    const card = screen.getByText('Glowing').closest('div');
    expect(card).toHaveClass('hover:border-primary/30');
  });

  it('applies custom className', () => {
    render(<GlassCard className="custom-class">Custom</GlassCard>);
    const card = screen.getByText('Custom').closest('div');
    expect(card).toHaveClass('custom-class');
  });

  it('forwards additional props', () => {
    render(<GlassCard data-testid="glass-card">With Props</GlassCard>);
    expect(screen.getByTestId('glass-card')).toBeInTheDocument();
  });

  it('renders complex children', () => {
    render(
      <GlassCard>
        <h1>Title</h1>
        <p>Description</p>
      </GlassCard>
    );
    expect(screen.getByText('Title')).toBeInTheDocument();
    expect(screen.getByText('Description')).toBeInTheDocument();
  });
});
