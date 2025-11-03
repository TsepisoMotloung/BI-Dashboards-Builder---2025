import bcrypt from 'bcryptjs'
import argon2 from 'argon2'

/**
 * Hash password using Argon2 (compatible with ETL app)
 */
export async function hashPassword(password: string): Promise<string> {
  return argon2.hash(password)
}

/**
 * Verify password against hash
 * Automatically detects and verifies both bcrypt and Argon2 hashes
 */
export async function verifyPassword(password: string, hashedPassword: string): Promise<boolean> {
  try {
    // Check if it's an Argon2 hash (starts with $argon2)
    if (hashedPassword.startsWith('$argon2')) {
      return await argon2.verify(hashedPassword, password)
    }
    
    // Check if it's a bcrypt hash (starts with $2)
    if (hashedPassword.startsWith('$2')) {
      return await bcrypt.compare(password, hashedPassword)
    }
    
    console.error('Unknown hash format:', hashedPassword.substring(0, 10))
    return false
  } catch (error) {
    console.error('Password verification error:', error)
    return false
  }
}
