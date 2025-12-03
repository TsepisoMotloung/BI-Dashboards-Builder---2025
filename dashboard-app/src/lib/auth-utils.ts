import bcrypt from 'bcryptjs'

/**
 * Hash password using bcrypt
 */
export async function hashPassword(password: string): Promise<string> {
  return bcrypt.hash(password, 10)
}

/**
 * Verify password against bcrypt hash
 * This only supports bcrypt hashes. For Argon2 verification (from ETL app),
 * use verifyPasswordWithArgon2() instead (server-only)
 */
export async function verifyPassword(password: string, hashedPassword: string): Promise<boolean> {
  try {
    // Check if it's a bcrypt hash (starts with $2)
    if (hashedPassword.startsWith('$2')) {
      return await bcrypt.compare(password, hashedPassword)
    }
    
    // For Argon2 hashes, we need to use a separate function that won't run in Edge Runtime
    // This will be called from server-side code only
    if (hashedPassword.startsWith('$argon2')) {
      console.warn('Argon2 hash detected - use verifyPasswordWithArgon2() instead')
      return false
    }
    
    console.error('Unknown hash format:', hashedPassword.substring(0, 10))
    return false
  } catch (error) {
    console.error('Password verification error:', error)
    return false
  }
}

/**
 * Verify Argon2 password (server-only, not available in Edge Runtime)
 * This function dynamically imports argon2 to avoid Edge Runtime issues
 */
export async function verifyPasswordWithArgon2(password: string, hashedPassword: string): Promise<boolean> {
  try {
    if (hashedPassword.startsWith('$argon2')) {
      const argon2 = await import('argon2')
      return await argon2.verify(hashedPassword, password)
    }
    
    // Fallback to bcrypt
    return verifyPassword(password, hashedPassword)
  } catch (error) {
    console.error('Argon2 password verification error:', error)
    return false
  }
}

/**
 * Convert session user ID (string) to integer for Prisma queries
 */
export function getUserId(sessionUserId: string | number | undefined): number {
  if (!sessionUserId) {
    throw new Error('User ID is required')
  }
  const id = parseInt(String(sessionUserId), 10)
  if (isNaN(id)) {
    throw new Error('Invalid user ID')
  }
  return id
}
