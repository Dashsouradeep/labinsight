/**
 * Unit tests for API client utilities
 * Tests error handling, interceptors, and request/response processing
 */

import {
  apiRequest,
  uploadFile,
  deleteReport,
  APIError,
  NetworkError,
  TimeoutError,
  ValidationError,
  AuthenticationError,
  AuthorizationError,
  NotFoundError,
  RateLimitError,
  addRequestInterceptor,
  addResponseInterceptor,
  addErrorInterceptor,
  clearInterceptors,
  getErrorMessage,
  isAPIError,
  isNetworkError,
  isTimeoutError,
  isAuthenticationError,
  isValidationError,
  createAuthInterceptor,
} from "../lib/api-client";

// Mock fetch globally
global.fetch = jest.fn();

describe("API Client Error Types", () => {
  it("should create APIError with correct properties", () => {
    const error = new APIError("Test error", 500, "TEST_CODE", { detail: "test" });
    expect(error.message).toBe("Test error");
    expect(error.statusCode).toBe(500);
    expect(error.code).toBe("TEST_CODE");
    expect(error.details).toEqual({ detail: "test" });
    expect(error.name).toBe("APIError");
  });

  it("should create ValidationError with validation errors", () => {
    const validationErrors = { email: ["Invalid email"], password: ["Too short"] };
    const error = new ValidationError("Validation failed", validationErrors);
    expect(error.statusCode).toBe(400);
    expect(error.validationErrors).toEqual(validationErrors);
    expect(error.name).toBe("ValidationError");
  });

  it("should create AuthenticationError with 401 status", () => {
    const error = new AuthenticationError();
    expect(error.statusCode).toBe(401);
    expect(error.message).toBe("Authentication required");
  });

  it("should create RateLimitError with retry after", () => {
    const error = new RateLimitError("Too many requests", 60);
    expect(error.statusCode).toBe(429);
    expect(error.retryAfter).toBe(60);
  });
});

describe("API Client Error Type Guards", () => {
  it("should correctly identify APIError", () => {
    const error = new APIError("Test", 500);
    expect(isAPIError(error)).toBe(true);
    expect(isAPIError(new Error("Test"))).toBe(false);
  });

  it("should correctly identify NetworkError", () => {
    const error = new NetworkError("Network failed");
    expect(isNetworkError(error)).toBe(true);
    expect(isNetworkError(new Error("Test"))).toBe(false);
  });

  it("should correctly identify TimeoutError", () => {
    const error = new TimeoutError();
    expect(isTimeoutError(error)).toBe(true);
    expect(isTimeoutError(new Error("Test"))).toBe(false);
  });

  it("should correctly identify AuthenticationError", () => {
    const error = new AuthenticationError();
    expect(isAuthenticationError(error)).toBe(true);
    expect(isAuthenticationError(new APIError("Test", 500))).toBe(false);
  });

  it("should correctly identify ValidationError", () => {
    const error = new ValidationError("Invalid", {});
    expect(isValidationError(error)).toBe(true);
    expect(isValidationError(new APIError("Test", 400))).toBe(false);
  });
});

describe("getErrorMessage", () => {
  it("should return message from APIError", () => {
    const error = new APIError("API failed", 500);
    expect(getErrorMessage(error)).toBe("API failed");
  });

  it("should return friendly message for NetworkError", () => {
    const error = new NetworkError("Network failed");
    expect(getErrorMessage(error)).toBe("Network connection failed. Please check your internet connection.");
  });

  it("should return friendly message for TimeoutError", () => {
    const error = new TimeoutError();
    expect(getErrorMessage(error)).toBe("Request timed out. Please try again.");
  });

  it("should return message from generic Error", () => {
    const error = new Error("Generic error");
    expect(getErrorMessage(error)).toBe("Generic error");
  });

  it("should return default message for unknown error", () => {
    expect(getErrorMessage("string error")).toBe("An unexpected error occurred");
  });
});

describe("apiRequest", () => {
  beforeEach(() => {
    jest.clearAllMocks();
    clearInterceptors();
  });

  afterEach(() => {
    clearInterceptors();
  });

  it("should make successful GET request", async () => {
    const mockData = { id: 1, name: "Test" };
    (global.fetch as jest.Mock).mockResolvedValueOnce({
      ok: true,
      json: async () => mockData,
    });

    const result = await apiRequest("/api/test");
    
    expect(global.fetch).toHaveBeenCalledWith(
      "http://localhost:8000/api/test",
      expect.objectContaining({
        headers: expect.objectContaining({
          "Content-Type": "application/json",
        }),
      })
    );
    expect(result).toEqual(mockData);
  });

  it("should inject authentication token", async () => {
    const mockData = { success: true };
    (global.fetch as jest.Mock).mockResolvedValueOnce({
      ok: true,
      json: async () => mockData,
    });

    await apiRequest("/api/protected", { token: "test-token" });
    
    expect(global.fetch).toHaveBeenCalledWith(
      "http://localhost:8000/api/protected",
      expect.objectContaining({
        headers: expect.objectContaining({
          "Authorization": "Bearer test-token",
        }),
      })
    );
  });

  it("should handle 400 validation error", async () => {
    (global.fetch as jest.Mock).mockResolvedValueOnce({
      ok: false,
      status: 400,
      json: async () => ({
        message: "Validation failed",
        validation_errors: { email: ["Invalid email"] },
      }),
    });

    await expect(apiRequest("/api/test")).rejects.toThrow(ValidationError);
  });

  it("should handle 401 authentication error", async () => {
    (global.fetch as jest.Mock).mockResolvedValueOnce({
      ok: false,
      status: 401,
      json: async () => ({ message: "Unauthorized" }),
    });

    await expect(apiRequest("/api/test")).rejects.toThrow(AuthenticationError);
  });

  it("should handle 403 authorization error", async () => {
    (global.fetch as jest.Mock).mockResolvedValueOnce({
      ok: false,
      status: 403,
      json: async () => ({ message: "Forbidden" }),
    });

    await expect(apiRequest("/api/test")).rejects.toThrow(AuthorizationError);
  });

  it("should handle 404 not found error", async () => {
    (global.fetch as jest.Mock).mockResolvedValueOnce({
      ok: false,
      status: 404,
      json: async () => ({ message: "Not found" }),
    });

    await expect(apiRequest("/api/test")).rejects.toThrow(NotFoundError);
  });

  it("should handle network errors", async () => {
    (global.fetch as jest.Mock).mockRejectedValueOnce(new Error("Network failure"));

    await expect(apiRequest("/api/test", { retry: false })).rejects.toThrow(NetworkError);
  });

  it("should retry GET requests on failure", async () => {
    (global.fetch as jest.Mock)
      .mockRejectedValueOnce(new Error("Network failure"))
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({ success: true }),
      });

    const result = await apiRequest("/api/test", { retries: 1 });
    
    expect(global.fetch).toHaveBeenCalledTimes(2);
    expect(result).toEqual({ success: true });
  }, 10000); // 10 second timeout for retry test

  it("should not retry on authentication errors", async () => {
    (global.fetch as jest.Mock).mockResolvedValueOnce({
      ok: false,
      status: 401,
      json: async () => ({ message: "Unauthorized" }),
    });

    await expect(apiRequest("/api/test")).rejects.toThrow(AuthenticationError);
    expect(global.fetch).toHaveBeenCalledTimes(1);
  });

  it("should not retry POST requests by default", async () => {
    (global.fetch as jest.Mock).mockRejectedValueOnce(new Error("Network failure"));

    await expect(
      apiRequest("/api/test", { method: "POST", retry: false })
    ).rejects.toThrow(NetworkError);
    
    expect(global.fetch).toHaveBeenCalledTimes(1);
  });
});

describe("Request Interceptors", () => {
  beforeEach(() => {
    jest.clearAllMocks();
    clearInterceptors();
  });

  afterEach(() => {
    clearInterceptors();
  });

  it("should apply request interceptor", async () => {
    const mockData = { success: true };
    (global.fetch as jest.Mock).mockResolvedValueOnce({
      ok: true,
      json: async () => mockData,
    });

    const interceptor = jest.fn((endpoint, options) => {
      return {
        endpoint,
        options: {
          ...options,
          headers: {
            ...options.headers,
            "X-Custom-Header": "test",
          },
        },
      };
    });

    addRequestInterceptor(interceptor);
    await apiRequest("/api/test");

    expect(interceptor).toHaveBeenCalled();
    expect(global.fetch).toHaveBeenCalledWith(
      "http://localhost:8000/api/test",
      expect.objectContaining({
        headers: expect.objectContaining({
          "X-Custom-Header": "test",
        }),
      })
    );
  });

  it("should remove request interceptor", async () => {
    const mockData = { success: true };
    (global.fetch as jest.Mock).mockResolvedValueOnce({
      ok: true,
      json: async () => mockData,
    });

    const interceptor = jest.fn((endpoint, options) => ({ endpoint, options }));
    const remove = addRequestInterceptor(interceptor);
    
    remove();
    await apiRequest("/api/test");

    expect(interceptor).not.toHaveBeenCalled();
  });
});

describe("Response Interceptors", () => {
  beforeEach(() => {
    jest.clearAllMocks();
    clearInterceptors();
  });

  afterEach(() => {
    clearInterceptors();
  });

  it("should apply response interceptor", async () => {
    const mockData = { success: true };
    (global.fetch as jest.Mock).mockResolvedValueOnce({
      ok: true,
      json: async () => mockData,
    });

    const interceptor = jest.fn((response) => response);
    addResponseInterceptor(interceptor);
    
    await apiRequest("/api/test");

    expect(interceptor).toHaveBeenCalled();
  });
});

describe("Error Interceptors", () => {
  beforeEach(() => {
    jest.clearAllMocks();
    clearInterceptors();
  });

  afterEach(() => {
    clearInterceptors();
  });

  it("should apply error interceptor", async () => {
    (global.fetch as jest.Mock).mockResolvedValueOnce({
      ok: false,
      status: 500,
      json: async () => ({ message: "Server error" }),
    });

    const interceptor = jest.fn((error) => {
      throw error;
    });
    addErrorInterceptor(interceptor);

    await expect(apiRequest("/api/test", { retry: false })).rejects.toThrow();
    expect(interceptor).toHaveBeenCalled();
  });
});

describe("createAuthInterceptor", () => {
  beforeEach(() => {
    jest.clearAllMocks();
    clearInterceptors();
  });

  afterEach(() => {
    clearInterceptors();
  });

  it("should inject token from getter function", async () => {
    const mockData = { success: true };
    (global.fetch as jest.Mock).mockResolvedValueOnce({
      ok: true,
      json: async () => mockData,
    });

    const getToken = () => "global-token";
    const { install } = createAuthInterceptor(getToken);
    install();

    await apiRequest("/api/test");

    expect(global.fetch).toHaveBeenCalledWith(
      "http://localhost:8000/api/test",
      expect.objectContaining({
        headers: expect.objectContaining({
          "Authorization": "Bearer global-token",
        }),
      })
    );
  });

  it("should not override existing Authorization header", async () => {
    const mockData = { success: true };
    (global.fetch as jest.Mock).mockResolvedValueOnce({
      ok: true,
      json: async () => mockData,
    });

    const getToken = () => "global-token";
    const { install } = createAuthInterceptor(getToken);
    install();

    await apiRequest("/api/test", { token: "request-token" });

    expect(global.fetch).toHaveBeenCalledWith(
      "http://localhost:8000/api/test",
      expect.objectContaining({
        headers: expect.objectContaining({
          "Authorization": "Bearer request-token",
        }),
      })
    );
  });
});

describe("uploadFile", () => {
  beforeEach(() => {
    jest.clearAllMocks();
    clearInterceptors();
  });

  afterEach(() => {
    clearInterceptors();
  });

  it("should upload file successfully", async () => {
    const mockData = { report_id: "123", status: "uploaded" };
    (global.fetch as jest.Mock).mockResolvedValueOnce({
      ok: true,
      json: async () => mockData,
    });

    const file = new File(["test"], "test.pdf", { type: "application/pdf" });
    const result = await uploadFile("/api/reports/upload", file, "test-token");

    expect(result).toEqual(mockData);
    expect(global.fetch).toHaveBeenCalledWith(
      "http://localhost:8000/api/reports/upload",
      expect.objectContaining({
        method: "POST",
        headers: expect.objectContaining({
          "Authorization": "Bearer test-token",
        }),
        body: expect.any(FormData),
      })
    );
  });

  it("should handle upload errors", async () => {
    (global.fetch as jest.Mock).mockResolvedValueOnce({
      ok: false,
      status: 400,
      json: async () => ({ message: "Invalid file" }),
    });

    const file = new File(["test"], "test.pdf", { type: "application/pdf" });
    
    await expect(
      uploadFile("/api/reports/upload", file, "test-token")
    ).rejects.toThrow(APIError);
  });
});

describe("deleteReport", () => {
  beforeEach(() => {
    jest.clearAllMocks();
    clearInterceptors();
  });

  it("should delete report successfully", async () => {
    (global.fetch as jest.Mock).mockResolvedValueOnce({
      ok: true,
      json: async () => ({ message: "Deleted" }),
    });

    await deleteReport("report-123", "test-token");

    expect(global.fetch).toHaveBeenCalledWith(
      "http://localhost:8000/api/reports/report-123",
      expect.objectContaining({
        method: "DELETE",
        headers: expect.objectContaining({
          "Authorization": "Bearer test-token",
        }),
      })
    );
  });
});
