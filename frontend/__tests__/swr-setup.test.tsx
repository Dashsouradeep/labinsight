/**
 * Tests for SWR setup and configuration
 */

import { renderHook, waitFor } from "@testing-library/react";
import { SessionProvider } from "next-auth/react";
import { SWRProvider } from "@/lib/swr-config";
import { useReports } from "@/lib/use-api";
import { ReactNode } from "react";

// Mock next-auth
jest.mock("next-auth/react", () => ({
  SessionProvider: ({ children }: { children: ReactNode }) => <>{children}</>,
  useSession: jest.fn(),
}));

// Mock fetch
global.fetch = jest.fn();

const mockSession = {
  user: {
    id: "user-123",
    email: "test@example.com",
    accessToken: "mock-token-123",
  },
  expires: "2024-12-31",
};

describe("SWR Setup", () => {
  beforeEach(() => {
    jest.clearAllMocks();
    (global.fetch as jest.Mock).mockClear();
  });

  const wrapper = ({ children }: { children: ReactNode }) => (
    <SessionProvider>
      <SWRProvider>{children}</SWRProvider>
    </SessionProvider>
  );

  describe("useReports hook", () => {
    it("should fetch reports with authentication token", async () => {
      const { useSession } = require("next-auth/react");
      useSession.mockReturnValue({
        data: mockSession,
        status: "authenticated",
      });

      const mockReports = [
        {
          id: "report-1",
          file_name: "test-report.pdf",
          upload_date: "2024-01-01",
          processing_status: "completed",
          file_size: 1024,
          file_type: "pdf",
        },
      ];

      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: async () => mockReports,
      });

      const { result } = renderHook(() => useReports(), { wrapper });

      // Initially loading
      expect(result.current.isLoading).toBe(true);
      expect(result.current.reports).toBeUndefined();

      // Wait for data to load
      await waitFor(() => {
        expect(result.current.reports).toEqual(mockReports);
      });

      expect(result.current.isLoading).toBe(false);
      
      // Verify the Authorization header was included
      expect(global.fetch).toHaveBeenCalledWith(
        "http://localhost:8000/api/reports",
        expect.objectContaining({
          headers: expect.objectContaining({
            Authorization: "Bearer mock-token-123",
            "Content-Type": "application/json",
          }),
        })
      );
    });

    it("should not fetch when user is not authenticated", () => {
      const { useSession } = require("next-auth/react");
      useSession.mockReturnValue({
        data: null,
        status: "unauthenticated",
      });

      const { result } = renderHook(() => useReports(), { wrapper });

      expect(result.current.isLoading).toBe(false);
      expect(result.current.reports).toBeUndefined();
      expect(global.fetch).not.toHaveBeenCalled();
    });
  });
});
