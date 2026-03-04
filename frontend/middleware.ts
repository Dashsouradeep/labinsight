import { withAuth } from "next-auth/middleware";
import { NextResponse } from "next/server";

/**
 * Middleware to protect routes that require authentication
 * Redirects unauthenticated users to the login page
 */
export default withAuth(
  function middleware(req) {
    return NextResponse.next();
  },
  {
    callbacks: {
      authorized: ({ token }) => !!token,
    },
    pages: {
      signIn: "/auth/login",
    },
  }
);

/**
 * Configure which routes require authentication
 * All routes except auth pages and public assets
 */
export const config = {
  matcher: [
    "/dashboard/:path*",
    "/upload/:path*",
    "/reports/:path*",
    "/trends/:path*",
  ],
};
