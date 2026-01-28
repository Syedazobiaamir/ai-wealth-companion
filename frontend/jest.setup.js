import '@testing-library/jest-dom';

// Mock next/navigation
jest.mock('next/navigation', () => ({
  useRouter() {
    return {
      push: jest.fn(),
      replace: jest.fn(),
      prefetch: jest.fn(),
      back: jest.fn(),
    };
  },
  usePathname() {
    return '/dashboard';
  },
  useSearchParams() {
    return new URLSearchParams();
  },
}));

// Mock next-themes
jest.mock('next-themes', () => ({
  useTheme() {
    return {
      theme: 'light',
      setTheme: jest.fn(),
      resolvedTheme: 'light',
    };
  },
  ThemeProvider: ({ children }) => children,
}));

// Mock framer-motion - filter out motion-specific props to avoid React warnings
jest.mock('framer-motion', () => {
  const filterMotionProps = (props) => {
    const motionProps = [
      'whileHover', 'whileTap', 'whileFocus', 'whileDrag', 'whileInView',
      'initial', 'animate', 'exit', 'transition', 'variants', 'layout',
      'layoutId', 'drag', 'dragConstraints', 'onDragStart', 'onDragEnd',
    ];
    const filtered = { ...props };
    motionProps.forEach((prop) => delete filtered[prop]);
    return filtered;
  };

  return {
    motion: {
      div: ({ children, ...props }) => <div {...filterMotionProps(props)}>{children}</div>,
      button: ({ children, ...props }) => <button {...filterMotionProps(props)}>{children}</button>,
      span: ({ children, ...props }) => <span {...filterMotionProps(props)}>{children}</span>,
      svg: ({ children, ...props }) => <svg {...filterMotionProps(props)}>{children}</svg>,
      p: ({ children, ...props }) => <p {...filterMotionProps(props)}>{children}</p>,
      h1: ({ children, ...props }) => <h1 {...filterMotionProps(props)}>{children}</h1>,
      h2: ({ children, ...props }) => <h2 {...filterMotionProps(props)}>{children}</h2>,
      h3: ({ children, ...props }) => <h3 {...filterMotionProps(props)}>{children}</h3>,
    },
    AnimatePresence: ({ children }) => children,
  };
});

// Mock window.matchMedia
Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: jest.fn().mockImplementation((query) => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: jest.fn(),
    removeListener: jest.fn(),
    addEventListener: jest.fn(),
    removeEventListener: jest.fn(),
    dispatchEvent: jest.fn(),
  })),
});

// Mock ResizeObserver
global.ResizeObserver = jest.fn().mockImplementation(() => ({
  observe: jest.fn(),
  unobserve: jest.fn(),
  disconnect: jest.fn(),
}));
