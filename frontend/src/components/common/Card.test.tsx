import { describe, it, expect } from 'vitest';
import { render, screen } from '@/test/test-utils';
import { Card, CardHeader, CardTitle, CardContent, CardFooter } from './Card';

describe('Card', () => {
  it('renders children', () => {
    render(<Card>Card content</Card>);
    expect(screen.getByText(/card content/i)).toBeInTheDocument();
  });

  it('applies variant styles', () => {
    const { container, rerender } = render(<Card variant="default">Default</Card>);
    expect(container.firstChild).toHaveClass('bg-white');

    rerender(<Card variant="bordered">Bordered</Card>);
    expect(container.firstChild).toHaveClass('border');

    rerender(<Card variant="elevated">Elevated</Card>);
    expect(container.firstChild).toHaveClass('shadow-lg');
  });

  it('applies custom className', () => {
    const { container } = render(<Card className="custom-class">Content</Card>);
    expect(container.firstChild).toHaveClass('custom-class');
  });

  it('applies padding styles', () => {
    const { container, rerender } = render(<Card padding="sm">Small</Card>);
    expect(container.firstChild).toHaveClass('p-4');

    rerender(<Card padding="md">Medium</Card>);
    expect(container.firstChild).toHaveClass('p-6');

    rerender(<Card padding="lg">Large</Card>);
    expect(container.firstChild).toHaveClass('p-8');
  });
});

describe('CardHeader', () => {
  it('renders children', () => {
    render(<CardHeader>Header content</CardHeader>);
    expect(screen.getByText(/header content/i)).toBeInTheDocument();
  });
});

describe('CardTitle', () => {
  it('renders as h3 by default', () => {
    render(<CardTitle>Title</CardTitle>);
    expect(screen.getByRole('heading', { level: 3 })).toBeInTheDocument();
  });

  it('renders with custom className', () => {
    render(<CardTitle className="custom-class">Title</CardTitle>);
    expect(screen.getByRole('heading')).toHaveClass('custom-class');
  });
});

describe('CardContent', () => {
  it('renders children', () => {
    render(<CardContent>Content</CardContent>);
    expect(screen.getByText(/content/i)).toBeInTheDocument();
  });
});

describe('CardFooter', () => {
  it('renders children', () => {
    render(<CardFooter>Footer</CardFooter>);
    expect(screen.getByText(/footer/i)).toBeInTheDocument();
  });
});

describe('Full Card', () => {
  it('renders complete card structure', () => {
    render(
      <Card>
        <CardHeader>
          <CardTitle>Test Title</CardTitle>
        </CardHeader>
        <CardContent>Test Content</CardContent>
        <CardFooter>Test Footer</CardFooter>
      </Card>
    );

    expect(screen.getByText(/test title/i)).toBeInTheDocument();
    expect(screen.getByText(/test content/i)).toBeInTheDocument();
    expect(screen.getByText(/test footer/i)).toBeInTheDocument();
  });
});
