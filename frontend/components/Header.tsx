"use client";

import { useState } from "react";
import Link from "next/link";
import { useAuth } from "@/lib/use-auth";

interface HeaderProps {
  user?: {
    email?: string | null;
    profile?: {
      age?: number;
      gender?: string;
    };
  } | null;
  onLogout?: () => void;
}

/**
 * Header Component
 * Displays logo, navigation, user profile, and logout button
 * Includes responsive mobile menu
 * Requirements: 11.3
 */
export default function Header({ user, onLogout }: HeaderProps) {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const auth = useAuth();

  // Use props if provided, otherwise fall back to useAuth hook
  const currentUser = user ?? auth.user;
  const handleLogout = onLogout ?? auth.logout;

  const toggleMobileMenu = () => {
    setMobileMenuOpen(!mobileMenuOpen);
  };

  return (
    <header className="bg-white shadow-sm">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center py-4">
          {/* Logo */}
          <Link href="/dashboard" className="flex items-center">
            <h1 className="text-2xl font-bold text-primary-dark hover:text-primary transition-colors">
              LabInsight
            </h1>
          </Link>

          {/* Desktop Navigation */}
          <nav className="hidden md:flex items-center space-x-6">
            <Link
              href="/dashboard"
              className="text-gray-700 hover:text-primary transition-colors"
            >
              Dashboard
            </Link>
            <Link
              href="/upload"
              className="text-gray-700 hover:text-primary transition-colors"
            >
              Upload Report
            </Link>
            <Link
              href="/trends"
              className="text-gray-700 hover:text-primary transition-colors"
            >
              Health Trends
            </Link>
          </nav>

          {/* Desktop User Profile & Logout */}
          <div className="hidden md:flex items-center space-x-4">
            {currentUser && (
              <div className="flex items-center space-x-3">
                <div className="text-right">
                  <p className="text-sm font-medium text-gray-900">
                    {currentUser.email}
                  </p>
                  {currentUser.profile && (
                    <p className="text-xs text-gray-500">
                      {currentUser.profile.age && `${currentUser.profile.age}y`}
                      {currentUser.profile.age && currentUser.profile.gender && " • "}
                      {currentUser.profile.gender}
                    </p>
                  )}
                </div>
                <button
                  onClick={handleLogout}
                  className="bg-primary text-white px-4 py-2 rounded-md hover:bg-primary-dark transition-colors text-sm font-medium"
                  aria-label="Logout"
                >
                  Logout
                </button>
              </div>
            )}
          </div>

          {/* Mobile Menu Button */}
          <button
            onClick={toggleMobileMenu}
            className="md:hidden p-2 rounded-md text-gray-700 hover:text-primary hover:bg-gray-100 transition-colors"
            aria-label="Toggle mobile menu"
            aria-expanded={mobileMenuOpen}
          >
            <svg
              className="h-6 w-6"
              fill="none"
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth="2"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              {mobileMenuOpen ? (
                <path d="M6 18L18 6M6 6l12 12" />
              ) : (
                <path d="M4 6h16M4 12h16M4 18h16" />
              )}
            </svg>
          </button>
        </div>

        {/* Mobile Menu */}
        {mobileMenuOpen && (
          <div className="md:hidden border-t border-gray-200 py-4">
            <nav className="flex flex-col space-y-3">
              <Link
                href="/dashboard"
                className="text-gray-700 hover:text-primary transition-colors px-2 py-2 rounded-md hover:bg-gray-50"
                onClick={() => setMobileMenuOpen(false)}
              >
                Dashboard
              </Link>
              <Link
                href="/upload"
                className="text-gray-700 hover:text-primary transition-colors px-2 py-2 rounded-md hover:bg-gray-50"
                onClick={() => setMobileMenuOpen(false)}
              >
                Upload Report
              </Link>
              <Link
                href="/trends"
                className="text-gray-700 hover:text-primary transition-colors px-2 py-2 rounded-md hover:bg-gray-50"
                onClick={() => setMobileMenuOpen(false)}
              >
                Health Trends
              </Link>
            </nav>

            {/* Mobile User Profile & Logout */}
            {currentUser && (
              <div className="mt-4 pt-4 border-t border-gray-200">
                <div className="px-2 mb-3">
                  <p className="text-sm font-medium text-gray-900">
                    {currentUser.email}
                  </p>
                  {currentUser.profile && (
                    <p className="text-xs text-gray-500 mt-1">
                      {currentUser.profile.age && `${currentUser.profile.age} years old`}
                      {currentUser.profile.age && currentUser.profile.gender && " • "}
                      {currentUser.profile.gender}
                    </p>
                  )}
                </div>
                <button
                  onClick={() => {
                    setMobileMenuOpen(false);
                    handleLogout();
                  }}
                  className="w-full bg-primary text-white px-4 py-2 rounded-md hover:bg-primary-dark transition-colors text-sm font-medium"
                  aria-label="Logout"
                >
                  Logout
                </button>
              </div>
            )}
          </div>
        )}
      </div>
    </header>
  );
}
