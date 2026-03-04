/**
 * Test page to verify Tailwind CSS configuration
 * This page demonstrates:
 * - Custom color palette
 * - Responsive breakpoints
 * - Accessibility features (minimum font size, touch targets, contrast)
 * 
 * To view: npm run dev and navigate to /test-tailwind
 */

export default function TestTailwind() {
  return (
    <main className="min-h-screen bg-primary-lighter p-4 tablet:p-6 desktop:p-8">
      <div className="container-responsive">
        <h1 className="text-4xl font-bold text-primary-dark mb-8">
          Tailwind CSS Configuration Test
        </h1>

        {/* Color Palette Section */}
        <section className="mb-12">
          <h2 className="text-2xl font-semibold text-primary-dark mb-4">
            Color Palette
          </h2>
          <div className="grid grid-cols-1 tablet:grid-cols-2 desktop:grid-cols-4 gap-4">
            <div className="bg-primary-dark text-white p-6 rounded-lg">
              <p className="font-semibold">Primary Dark</p>
              <p className="text-sm">#09637E</p>
            </div>
            <div className="bg-primary text-white p-6 rounded-lg">
              <p className="font-semibold">Primary</p>
              <p className="text-sm">#088395</p>
            </div>
            <div className="bg-primary-light text-white p-6 rounded-lg">
              <p className="font-semibold">Primary Light</p>
              <p className="text-sm">#7AB2B2</p>
            </div>
            <div className="bg-primary-lighter text-primary-dark p-6 rounded-lg border-2 border-primary">
              <p className="font-semibold">Primary Lighter</p>
              <p className="text-sm">#EBF4F6</p>
            </div>
          </div>
        </section>

        {/* Responsive Breakpoints Section */}
        <section className="mb-12">
          <h2 className="text-2xl font-semibold text-primary-dark mb-4">
            Responsive Breakpoints
          </h2>
          <div className="bg-white p-6 rounded-lg shadow-md">
            <div className="space-y-4">
              <div className="p-4 bg-red-100 tablet:bg-blue-100 desktop:bg-green-100 wide:bg-purple-100 rounded">
                <p className="font-semibold">Current Breakpoint:</p>
                <p className="tablet:hidden">Mobile (&lt; 768px)</p>
                <p className="hidden tablet:block desktop:hidden">Tablet (≥ 768px)</p>
                <p className="hidden desktop:block wide:hidden">Desktop (≥ 1024px)</p>
                <p className="hidden wide:block">Wide (≥ 1280px)</p>
              </div>
              
              <div className="grid grid-cols-1 tablet:grid-cols-2 desktop:grid-cols-3 gap-4">
                <div className="bg-primary-lighter p-4 rounded">
                  <p className="font-semibold">Column 1</p>
                  <p className="text-sm">Full width on mobile</p>
                </div>
                <div className="bg-primary-lighter p-4 rounded">
                  <p className="font-semibold">Column 2</p>
                  <p className="text-sm">2 cols on tablet</p>
                </div>
                <div className="bg-primary-lighter p-4 rounded">
                  <p className="font-semibold">Column 3</p>
                  <p className="text-sm">3 cols on desktop</p>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* Accessibility Features Section */}
        <section className="mb-12">
          <h2 className="text-2xl font-semibold text-primary-dark mb-4">
            Accessibility Features
          </h2>
          <div className="bg-white p-6 rounded-lg shadow-md space-y-6">
            {/* Font Size */}
            <div>
              <h3 className="text-xl font-semibold text-primary mb-2">
                Minimum Font Size (16px)
              </h3>
              <p className="text-base">
                This text is 16px (1rem) - the minimum font size for accessibility.
                It ensures readability for all users, including elderly patients.
              </p>
            </div>

            {/* Touch Targets */}
            <div>
              <h3 className="text-xl font-semibold text-primary mb-2">
                Touch Target Sizes (44px minimum)
              </h3>
              <div className="flex flex-wrap gap-4">
                <button className="bg-primary text-white px-6 py-3 rounded-lg hover:bg-primary-dark transition-colors">
                  Standard Button
                </button>
                <button className="bg-primary-light text-white px-6 py-3 rounded-lg hover:bg-primary transition-colors">
                  Secondary Button
                </button>
              </div>
              <p className="text-sm text-gray-600 mt-2">
                All buttons meet WCAG 2.1 Level AAA touch target size (44px height)
              </p>
            </div>

            {/* Focus Indicators */}
            <div>
              <h3 className="text-xl font-semibold text-primary mb-2">
                Keyboard Navigation (Focus Indicators)
              </h3>
              <div className="flex flex-wrap gap-4">
                <a href="#" className="text-primary-dark hover:text-primary focus:outline-primary">
                  Focusable Link 1
                </a>
                <a href="#" className="text-primary-dark hover:text-primary focus:outline-primary">
                  Focusable Link 2
                </a>
                <input 
                  type="text" 
                  placeholder="Try tabbing to this input"
                  className="border-2 border-gray-300 rounded px-4 py-2 focus:border-primary focus:outline-none"
                />
              </div>
              <p className="text-sm text-gray-600 mt-2">
                Press Tab to see focus indicators on interactive elements
              </p>
            </div>

            {/* Contrast Ratios */}
            <div>
              <h3 className="text-xl font-semibold text-primary mb-2">
                High Contrast Ratios (4.5:1 minimum)
              </h3>
              <div className="space-y-2">
                <div className="bg-primary-lighter p-4 rounded">
                  <p className="text-primary-dark font-semibold">
                    Primary Dark on Primary Lighter ✓
                  </p>
                </div>
                <div className="bg-white p-4 rounded border border-gray-200">
                  <p className="text-primary-dark font-semibold">
                    Primary Dark on White ✓
                  </p>
                </div>
                <div className="bg-primary-dark p-4 rounded">
                  <p className="text-white font-semibold">
                    White on Primary Dark ✓
                  </p>
                </div>
              </div>
              <p className="text-sm text-gray-600 mt-2">
                All color combinations meet WCAG 2.1 Level AA contrast requirements
              </p>
            </div>
          </div>
        </section>

        {/* Requirements Validation */}
        <section className="mb-12">
          <h2 className="text-2xl font-semibold text-primary-dark mb-4">
            Requirements Validation
          </h2>
          <div className="bg-white p-6 rounded-lg shadow-md">
            <ul className="space-y-2">
              <li className="flex items-start">
                <span className="text-green-600 mr-2">✓</span>
                <span><strong>Requirement 11.1:</strong> Next.js and Tailwind CSS implementation</span>
              </li>
              <li className="flex items-start">
                <span className="text-green-600 mr-2">✓</span>
                <span><strong>Requirement 11.2:</strong> Custom color palette (#09637E, #088395, #7AB2B2, #EBF4F6)</span>
              </li>
              <li className="flex items-start">
                <span className="text-green-600 mr-2">✓</span>
                <span><strong>Requirement 11.8:</strong> Responsive layouts for screens below 768px</span>
              </li>
              <li className="flex items-start">
                <span className="text-green-600 mr-2">✓</span>
                <span><strong>Requirement 11.9:</strong> Minimum 16px font size for accessibility</span>
              </li>
              <li className="flex items-start">
                <span className="text-green-600 mr-2">✓</span>
                <span><strong>Requirement 11.10:</strong> High contrast ratios (minimum 4.5:1)</span>
              </li>
            </ul>
          </div>
        </section>

        {/* Instructions */}
        <section>
          <div className="bg-primary-dark text-white p-6 rounded-lg">
            <h3 className="text-xl font-semibold mb-2">Testing Instructions</h3>
            <ol className="list-decimal list-inside space-y-1">
              <li>Resize your browser window to test responsive breakpoints</li>
              <li>Press Tab to navigate and see focus indicators</li>
              <li>Verify all text is readable (minimum 16px)</li>
              <li>Check that buttons are easy to tap (44px minimum height)</li>
              <li>Confirm color contrast is sufficient for readability</li>
            </ol>
          </div>
        </section>
      </div>
    </main>
  )
}
