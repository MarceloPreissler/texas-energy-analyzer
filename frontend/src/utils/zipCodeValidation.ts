/**
 * Texas ZIP Code Validation Utility
 * Provides robust validation for Texas ZIP codes with specific range checking
 */

// Texas ZIP code ranges (ERCOT service territory)
// Main ranges: 750xx-799xx plus El Paso area 88510-88589
const TEXAS_ZIP_RANGES = [
  { min: 75001, max: 79999 },  // Main Texas
  { min: 88510, max: 88589 },  // El Paso area
];

// Common Texas ZIP codes for quick validation (major cities)
const COMMON_TEXAS_ZIPS = new Set([
  // Dallas-Fort Worth
  '75201', '75202', '75204', '75214', '75219', '75225', '75230', '75240',
  '76001', '76002', '76006', '76010', '76011', '76012', '76013', '76014',
  // Houston
  '77001', '77002', '77003', '77004', '77005', '77006', '77007', '77008',
  '77009', '77010', '77019', '77020', '77021', '77024', '77025', '77030',
  '77040', '77041', '77042', '77043', '77054', '77055', '77056', '77057',
  // Austin
  '78701', '78702', '78703', '78704', '78705', '78712', '78721', '78722',
  '78723', '78724', '78725', '78726', '78727', '78728', '78729', '78730',
  '78731', '78732', '78733', '78734', '78735', '78736', '78737', '78738',
  '78739', '78741', '78742', '78744', '78745', '78746', '78747', '78748',
  '78749', '78750', '78751', '78752', '78753', '78754', '78756', '78757',
  '78758', '78759',
  // San Antonio
  '78201', '78202', '78203', '78204', '78205', '78207', '78208', '78209',
  '78210', '78211', '78212', '78213', '78214', '78215', '78216', '78217',
  '78218', '78219', '78220', '78221', '78222', '78223', '78224', '78225',
  '78226', '78227', '78228', '78229', '78230', '78231', '78232', '78233',
  '78234', '78235', '78236', '78237', '78238', '78239', '78240', '78241',
  '78242', '78243', '78244', '78245', '78246', '78247', '78248', '78249',
  '78250', '78251', '78252', '78253', '78254', '78255', '78256', '78257',
  '78258', '78259', '78260', '78261', '78263', '78264', '78266',
  // Corpus Christi
  '78401', '78402', '78404', '78405', '78406', '78407', '78408', '78409',
  '78410', '78411', '78412', '78413', '78414', '78415', '78416', '78417',
  '78418', '78419',
  // El Paso
  '79901', '79902', '79903', '79904', '79905', '79906', '79907', '79908',
  '79910', '79911', '79912', '79915', '79920', '79922', '79924', '79925',
  '79927', '79928', '79930', '79932', '79934', '79935', '79936', '79938',
]);

export interface ZipValidationResult {
  isValid: boolean;
  isTexas: boolean;
  errorMessage: string | null;
  formattedZip: string;
  suggestion?: string;
}

/**
 * Sanitize ZIP code input - remove non-digits and trim
 */
export function sanitizeZipInput(input: string): string {
  return input.replace(/\D/g, '').slice(0, 5);
}

/**
 * Check if a ZIP code is within Texas ranges
 */
export function isTexasZipCode(zip: string): boolean {
  const numericZip = parseInt(zip, 10);
  if (isNaN(numericZip)) return false;

  return TEXAS_ZIP_RANGES.some(
    range => numericZip >= range.min && numericZip <= range.max
  );
}

/**
 * Check if ZIP is a known common Texas ZIP (high confidence)
 */
export function isCommonTexasZip(zip: string): boolean {
  return COMMON_TEXAS_ZIPS.has(zip);
}

/**
 * Validate a ZIP code for Texas electricity plans
 */
export function validateTexasZip(input: string): ZipValidationResult {
  const sanitized = sanitizeZipInput(input);

  // Empty input
  if (!sanitized) {
    return {
      isValid: false,
      isTexas: false,
      errorMessage: null, // Not an error, just empty
      formattedZip: '',
    };
  }

  // Partial input (still typing)
  if (sanitized.length < 5) {
    return {
      isValid: false,
      isTexas: false,
      errorMessage: null, // Don't show error while typing
      formattedZip: sanitized,
    };
  }

  // Full 5 digits but not Texas
  if (!isTexasZipCode(sanitized)) {
    // Check if it might be a Texas ZIP with a typo
    const firstTwo = sanitized.slice(0, 2);
    let suggestion: string | undefined;

    if (firstTwo === '74' || firstTwo === '80') {
      suggestion = `Did you mean ${firstTwo === '74' ? '75' : '79'}${sanitized.slice(2)}?`;
    }

    return {
      isValid: false,
      isTexas: false,
      errorMessage: 'This ZIP code is not in the ERCOT service territory. Please enter a Texas ZIP code (75xxx-79xxx).',
      formattedZip: sanitized,
      suggestion,
    };
  }

  // Valid Texas ZIP
  return {
    isValid: true,
    isTexas: true,
    errorMessage: null,
    formattedZip: sanitized,
  };
}

/**
 * Get a user-friendly error message for API errors
 */
export function getZipErrorMessage(error: unknown): string {
  if (error instanceof Error) {
    const message = error.message.toLowerCase();

    if (message.includes('network') || message.includes('fetch')) {
      return 'Unable to connect to the server. Please check your internet connection and try again.';
    }

    if (message.includes('timeout')) {
      return 'The request timed out. The PowerToChoose API may be experiencing high traffic. Please try again.';
    }

    if (message.includes('404') || message.includes('not found')) {
      return 'No plans found for this ZIP code. This area may not have competitive electricity options.';
    }

    if (message.includes('500') || message.includes('server')) {
      return 'The PowerToChoose server is temporarily unavailable. Please try again in a few minutes.';
    }

    if (message.includes('rate limit') || message.includes('429')) {
      return 'Too many requests. Please wait a moment before trying again.';
    }
  }

  return 'Unable to retrieve plans. Please verify the ZIP code and try again.';
}

/**
 * Get TDU (Transmission/Distribution Utility) for a Texas ZIP code
 */
export function getTDUForZip(zip: string): string | null {
  const numericZip = parseInt(zip, 10);
  if (isNaN(numericZip)) return null;

  // Rough TDU territory mapping based on ZIP prefix
  // This is approximate - actual TDU is determined by the utility
  const prefix = Math.floor(numericZip / 100);

  // Dallas/Fort Worth area - Oncor
  if (prefix >= 750 && prefix <= 769) return 'Oncor';
  if (prefix >= 760 && prefix <= 768) return 'Oncor';

  // Houston area - CenterPoint
  if (prefix >= 770 && prefix <= 779) return 'CenterPoint';

  // Austin area - Mixed (Oncor, TNMP)
  if (prefix >= 786 && prefix <= 789) return 'Oncor/TNMP';

  // San Antonio area - CPS Energy (municipal, not in ERCOT retail)
  if (prefix >= 780 && prefix <= 785) return 'AEP Texas';

  // Corpus Christi - AEP Texas Central
  if (prefix >= 783 && prefix <= 785) return 'AEP Texas Central';

  // West Texas - Varies
  if (prefix >= 790 && prefix <= 799) return 'AEP Texas/Oncor';

  // El Paso - El Paso Electric (separate grid)
  if (prefix >= 885 && prefix <= 889) return 'El Paso Electric';
  if (prefix >= 799) return 'El Paso Electric';

  return null;
}

export default {
  sanitizeZipInput,
  isTexasZipCode,
  isCommonTexasZip,
  validateTexasZip,
  getZipErrorMessage,
  getTDUForZip,
};
