/**
 * Browser Compatibility Test Suite
 * Automated tests for browser compatibility using Puppeteer
 */

const puppeteer = require('puppeteer');
const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

// Base URL for testing
const BASE_URL = process.env.TEST_URL || 'http://localhost:5000';

// Test configurations
const BROWSERS = [
  { name: 'Chrome', launchOptions: { product: 'chrome' } },
  { name: 'Firefox', launchOptions: { product: 'firefox' } },
  // Add Edge testing if on Windows
  ...(process.platform === 'win32' ? [{ name: 'Edge', executablePath: 'C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe' }] : []),
];

// Device emulation for responsive testing
const DEVICES = [
  { name: 'Desktop', viewport: { width: 1920, height: 1080 } },
  { name: 'Laptop', viewport: { width: 1366, height: 768 } },
  { name: 'Tablet', viewport: { width: 768, height: 1024 }, userAgent: 'Mozilla/5.0 (iPad; CPU OS 12_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/12.1 Mobile/15E148 Safari/604.1' },
  { name: 'Mobile', viewport: { width: 375, height: 667 }, userAgent: 'Mozilla/5.0 (iPhone; CPU iPhone OS 12_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/12.1 Mobile/15E148 Safari/604.1' },
];

// Pages to test
const PAGES = [
  { name: 'Home', path: '/' },
  { name: 'Dashboard', path: '/dashboard' },
  { name: 'Job Openings', path: '/job_openings' },
  { name: 'Campaigns', path: '/campaigns' },
  { name: 'Segments', path: '/segments' },
  { name: 'Analytics', path: '/analytics' },
];

// Test scenarios
const SCENARIOS = [
  { 
    name: 'Page Load',
    test: async (page) => {
      const loadTime = await page.evaluate(() => {
        return performance.timing.loadEventEnd - performance.timing.navigationStart;
      });
      return { success: loadTime < 5000, details: { loadTime } };
    }
  },
  {
    name: 'JavaScript Compatibility',
    test: async (page) => {
      const result = await page.evaluate(() => {
        try {
          // Check if our compatibility service is available
          if (typeof window.runCompatibilityTest === 'function') {
            return window.runCompatibilityTest();
          }
          
          // Fallback compatibility check
          return {
            ecmascript6: typeof Promise === 'function' && typeof Symbol === 'function',
            fetch: typeof fetch === 'function',
            localStorage: (() => {
              try {
                localStorage.setItem('test', 'test');
                localStorage.removeItem('test');
                return true;
              } catch (e) {
                return false;
              }
            })(),
            webSockets: typeof WebSocket === 'function',
          };
        } catch (error) {
          return { error: error.message };
        }
      });
      return { 
        success: !result.error && 
                 result.ecmascript6 && 
                 result.fetch && 
                 result.localStorage, 
        details: result 
      };
    }
  },
  {
    name: 'CSS Compatibility',
    test: async (page) => {
      const result = await page.evaluate(() => {
        try {
          return {
            grid: CSS.supports('display: grid'),
            flexbox: CSS.supports('display: flex'),
            cssVariables: (() => {
              try {
                return window.getComputedStyle(document.documentElement)
                  .getPropertyValue('--test') !== undefined;
              } catch (e) {
                return false;
              }
            })(),
          };
        } catch (error) {
          return { error: error.message };
        }
      });
      return { 
        success: !result.error && 
                 result.flexbox, // Flexbox is critical
        details: result 
      };
    }
  },
  {
    name: 'Responsive Layout',
    test: async (page, device) => {
      // Take screenshot for visual comparison
      const screenshotPath = path.join(__dirname, 'screenshots', 
        `${device.name.toLowerCase()}_${page.url().split('/').pop() || 'home'}.png`);
      await page.screenshot({ path: screenshotPath, fullPage: true });
      
      // Check for horizontal overflow
      const hasHorizontalOverflow = await page.evaluate(() => {
        return document.documentElement.scrollWidth > document.documentElement.clientWidth;
      });
      
      // Check for tiny text (potentially unreadable)
      const hasTinyText = await page.evaluate(() => {
        const textElements = Array.from(document.querySelectorAll('p, h1, h2, h3, h4, h5, h6, a, span, button'));
        for (const el of textElements) {
          const fontSize = parseInt(window.getComputedStyle(el).fontSize);
          if (fontSize < 10) { // 10px is considered minimal readable size
            return true;
          }
        }
        return false;
      });
      
      return { 
        success: !hasHorizontalOverflow && !hasTinyText, 
        details: { 
          hasHorizontalOverflow,
          hasTinyText,
          screenshotPath
        } 
      };
    }
  },
  {
    name: 'Interactive Features',
    test: async (page) => {
      // Test a basic interaction (clicking a button)
      const interactiveElements = await page.evaluate(() => {
        const buttons = Array.from(document.querySelectorAll('button:not([disabled]), a.btn:not([disabled])'));
        return buttons.map(btn => ({
          text: btn.textContent.trim(),
          id: btn.id,
          classes: btn.className,
        })).slice(0, 3); // Limit to first 3 buttons
      });
      
      // If no interactive elements found, skip test
      if (interactiveElements.length === 0) {
        return { success: true, details: { skipped: true, reason: 'No interactive elements found' } };
      }
      
      // Try to click each element and check for errors
      const results = [];
      for (const element of interactiveElements) {
        try {
          // Try to find and click the element
          const selector = element.id ? 
            `#${element.id}` : 
            `.${element.classes.split(' ').join('.')}:contains("${element.text}")`;
          
          await page.evaluate((selector) => {
            const el = document.querySelector(selector);
            if (el) el.click();
          }, selector);
          
          // Check for console errors after click
          const errors = await page.evaluate(() => {
            return window._lastConsoleError || null;
          });
          
          results.push({
            element,
            success: !errors,
            error: errors
          });
        } catch (error) {
          results.push({
            element,
            success: false,
            error: error.message
          });
        }
      }
      
      return { 
        success: results.every(r => r.success), 
        details: { interactiveElements, results } 
      };
    }
  }
];

/**
 * Run browser compatibility tests
 */
async function runBrowserCompatibilityTests() {
  console.log(`Starting browser compatibility tests against ${BASE_URL}`);
  
  // Create screenshots directory if it doesn't exist
  const screenshotsDir = path.join(__dirname, 'screenshots');
  if (!fs.existsSync(screenshotsDir)) {
    fs.mkdirSync(screenshotsDir, { recursive: true });
  }
  
  const results = {
    browsers: {},
    summary: {
      total: 0,
      passed: 0,
      failed: 0,
      skipped: 0
    }
  };
  
  // Test each browser
  for (const browser of BROWSERS) {
    console.log(`\nTesting on ${browser.name}...`);
    results.browsers[browser.name] = { devices: {} };
    
    let browserInstance;
    try {
      // Launch browser
      browserInstance = await puppeteer.launch({
        headless: true,
        ...browser.launchOptions
      });
      
      // Test each device
      for (const device of DEVICES) {
        console.log(`\n  Testing on ${device.name}...`);
        results.browsers[browser.name].devices[device.name] = { pages: {} };
        
        // Create a new page for each device
        const page = await browserInstance.newPage();
        
        // Set viewport and user agent
        await page.setViewport(device.viewport);
        if (device.userAgent) {
          await page.setUserAgent(device.userAgent);
        }
        
        // Capture console errors
        page.on('console', msg => {
          if (msg.type() === 'error') {
            page.evaluate((errorMessage) => {
              window._lastConsoleError = errorMessage;
            }, msg.text());
          }
        });
        
        // Test each page
        for (const pageConfig of PAGES) {
          console.log(`\n    Testing ${pageConfig.name}...`);
          results.browsers[browser.name].devices[device.name].pages[pageConfig.name] = { scenarios: {} };
          
          try {
            // Navigate to page
            await page.goto(`${BASE_URL}${pageConfig.path}`, { waitUntil: 'networkidle0' });
            
            // Run each test scenario
            for (const scenario of SCENARIOS) {
              console.log(`      Running ${scenario.name}...`);
              results.summary.total++;
              
              try {
                const result = await scenario.test(page, device);
                results.browsers[browser.name].devices[device.name].pages[pageConfig.name].scenarios[scenario.name] = result;
                
                if (result.details?.skipped) {
                  console.log(`      SKIPPED: ${scenario.name}`);
                  results.summary.skipped++;
                } else if (result.success) {
                  console.log(`      PASSED: ${scenario.name}`);
                  results.summary.passed++;
                } else {
                  console.log(`      FAILED: ${scenario.name}`);
                  results.summary.failed++;
                }
              } catch (error) {
                console.error(`      ERROR in ${scenario.name}:`, error);
                results.browsers[browser.name].devices[device.name].pages[pageConfig.name].scenarios[scenario.name] = {
                  success: false,
                  error: error.message
                };
                results.summary.failed++;
              }
            }
          } catch (error) {
            console.error(`    ERROR loading ${pageConfig.name}:`, error);
            results.browsers[browser.name].devices[device.name].pages[pageConfig.name].error = error.message;
            // Mark all scenarios as failed for this page
            for (const scenario of SCENARIOS) {
              results.summary.total++;
              results.summary.failed++;
            }
          }
        }
        
        await page.close();
      }
    } catch (error) {
      console.error(`ERROR with browser ${browser.name}:`, error);
      results.browsers[browser.name].error = error.message;
    } finally {
      if (browserInstance) {
        await browserInstance.close();
      }
    }
  }
  
  // Generate report
  const report = {
    timestamp: new Date().toISOString(),
    baseUrl: BASE_URL,
    summary: results.summary,
    details: results
  };
  
  // Save report to file
  const reportPath = path.join(__dirname, 'reports', `browser_compatibility_${Date.now()}.json`);
  fs.mkdirSync(path.dirname(reportPath), { recursive: true });
  fs.writeFileSync(reportPath, JSON.stringify(report, null, 2));
  
  console.log('\nBrowser compatibility testing complete!');
  console.log(`Total: ${results.summary.total}, Passed: ${results.summary.passed}, Failed: ${results.summary.failed}, Skipped: ${results.summary.skipped}`);
  console.log(`Report saved to ${reportPath}`);
  
  return report;
}

// If run directly (node browser_compatibility_test.js)
if (require.main === module) {
  // Check if the app is running
  try {
    execSync(`curl -s ${BASE_URL}`);
  } catch (error) {
    console.error(`ERROR: Application doesn't seem to be running at ${BASE_URL}`);
    console.error('Please start the application before running the tests.');
    process.exit(1);
  }
  
  runBrowserCompatibilityTests().catch(error => {
    console.error('Error running browser compatibility tests:', error);
    process.exit(1);
  });
}

module.exports = { runBrowserCompatibilityTests };