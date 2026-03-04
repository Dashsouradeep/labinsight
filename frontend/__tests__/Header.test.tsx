import React from "react";
import { render, screen, fireEvent } from "@testing-library/react";
import "@testing-library/jest-dom";
import Header from "@/components/Header";

// Mock next/link
jest.mock("next/link", () => {
  return ({ children, href }: { children: React.ReactNode; href: string }) => {
    return <a href={href}>{children}</a>;
  };
});

// Mock useAuth hook
jest.mock("@/lib/use-auth", () => ({
  useAuth: jest.fn(() => ({
    user: null,
    logout: jest.fn(),
  })),
}));

describe("Header Component", () => {
  const mockUser = {
    email: "test@example.com",
    profile: {
      age: 30,
      gender: "male",
    },
  };

  const mockLogout = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it("renders logo and navigation links", () => {
    render(<Header user={mockUser} onLogout={mockLogout} />);

    // Check logo
    expect(screen.getByText("LabInsight")).toBeInTheDocument();

    // Check navigation links (desktop)
    expect(screen.getByText("Dashboard")).toBeInTheDocument();
    expect(screen.getByText("Upload Report")).toBeInTheDocument();
    expect(screen.getByText("Health Trends")).toBeInTheDocument();
  });

  it("displays user profile information", () => {
    render(<Header user={mockUser} onLogout={mockLogout} />);

    // Check user email is displayed
    expect(screen.getByText("test@example.com")).toBeInTheDocument();

    // Check age and gender are displayed
    expect(screen.getByText(/30y/)).toBeInTheDocument();
    expect(screen.getByText(/male/)).toBeInTheDocument();
  });

  it("displays logout button and calls onLogout when clicked", () => {
    render(<Header user={mockUser} onLogout={mockLogout} />);

    // Find logout button (there are two - desktop and mobile)
    const logoutButtons = screen.getAllByRole("button", { name: /logout/i });
    expect(logoutButtons.length).toBeGreaterThan(0);

    // Click the first logout button (desktop)
    fireEvent.click(logoutButtons[0]);

    // Check that logout was called
    expect(mockLogout).toHaveBeenCalledTimes(1);
  });

  it("toggles mobile menu when hamburger button is clicked", () => {
    render(<Header user={mockUser} onLogout={mockLogout} />);

    // Find mobile menu button
    const mobileMenuButton = screen.getByLabelText("Toggle mobile menu");
    expect(mobileMenuButton).toBeInTheDocument();

    // Initially, mobile menu should not be expanded
    expect(mobileMenuButton).toHaveAttribute("aria-expanded", "false");

    // Click to open mobile menu
    fireEvent.click(mobileMenuButton);

    // Mobile menu should now be expanded
    expect(mobileMenuButton).toHaveAttribute("aria-expanded", "true");

    // Click again to close
    fireEvent.click(mobileMenuButton);

    // Mobile menu should be closed
    expect(mobileMenuButton).toHaveAttribute("aria-expanded", "false");
  });

  it("renders without user profile information when user is null", () => {
    render(<Header user={null} onLogout={mockLogout} />);

    // Logo should still be present
    expect(screen.getByText("LabInsight")).toBeInTheDocument();

    // Navigation should still be present
    expect(screen.getByText("Dashboard")).toBeInTheDocument();

    // User email should not be present
    expect(screen.queryByText("test@example.com")).not.toBeInTheDocument();
  });

  it("renders with partial user profile (no age/gender)", () => {
    const userWithoutProfile = {
      email: "test@example.com",
    };

    render(<Header user={userWithoutProfile} onLogout={mockLogout} />);

    // Email should be displayed
    expect(screen.getByText("test@example.com")).toBeInTheDocument();

    // Age and gender should not be displayed
    expect(screen.queryByText(/30y/)).not.toBeInTheDocument();
    expect(screen.queryByText(/male/)).not.toBeInTheDocument();
  });

  it("mobile menu visibility toggles correctly", () => {
    const { container } = render(<Header user={mockUser} onLogout={mockLogout} />);

    // Open mobile menu
    const mobileMenuButton = screen.getByLabelText("Toggle mobile menu");
    
    // Initially closed
    expect(mobileMenuButton).toHaveAttribute("aria-expanded", "false");
    
    // Open menu
    fireEvent.click(mobileMenuButton);
    expect(mobileMenuButton).toHaveAttribute("aria-expanded", "true");
    
    // Mobile menu should be visible
    const mobileMenu = container.querySelector('.md\\:hidden.border-t');
    expect(mobileMenu).toBeInTheDocument();

    // Close menu
    fireEvent.click(mobileMenuButton);
    expect(mobileMenuButton).toHaveAttribute("aria-expanded", "false");
  });

  it("has accessible ARIA labels", () => {
    render(<Header user={mockUser} onLogout={mockLogout} />);

    // Check for ARIA labels
    expect(screen.getByLabelText("Toggle mobile menu")).toBeInTheDocument();
    expect(screen.getAllByLabelText("Logout").length).toBeGreaterThan(0);
  });
});
