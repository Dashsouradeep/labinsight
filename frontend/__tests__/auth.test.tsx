/**
 * Authentication Tests
 * Tests for NextAuth.js configuration and auth utilities
 */

import { render, screen } from "@testing-library/react";
import { AuthProvider } from "@/lib/auth-context";

// Mock NextAuth
jest.mock("next-auth/react", () => ({
  SessionProvider: ({ children }: { children: React.ReactNode }) => (
    <div data-testid="session-provider">{children}</div>
  ),
  useSession: jest.fn(),
  signIn: jest.fn(),
  signOut: jest.fn(),
}));

// Mock next/navigation
jest.mock("next/navigation", () => ({
  useRouter: () => ({
    push: jest.fn(),
    replace: jest.fn(),
    prefetch: jest.fn(),
  }),
}));

describe("Authentication", () => {
  describe("AuthProvider", () => {
    it("should render children", () => {
      render(
        <AuthProvider>
          <div>Test Content</div>
        </AuthProvider>
      );

      expect(screen.getByText("Test Content")).toBeTruthy();
    });

    it("should wrap children with SessionProvider", () => {
      render(
        <AuthProvider>
          <div>Test Content</div>
        </AuthProvider>
      );

      expect(screen.getByTestId("session-provider")).toBeTruthy();
    });
  });

  describe("Configuration", () => {
    it("should have correct environment variables", () => {
      expect(process.env.NEXT_PUBLIC_API_URL).toBe("http://localhost:8000");
      expect(process.env.NEXTAUTH_URL).toBe("http://localhost:3000");
      expect(process.env.NEXTAUTH_SECRET).toBe("test-secret");
    });
  });
});
