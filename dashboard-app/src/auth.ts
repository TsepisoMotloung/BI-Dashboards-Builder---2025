import NextAuth, { DefaultSession } from "next-auth"
import Credentials from "next-auth/providers/credentials"
import { prisma } from "@/lib/prisma"
import { verifyPasswordWithArgon2 } from "@/lib/auth-utils"

declare module "next-auth" {
  interface Session {
    user: {
      id: number
      status: string
      roles: any[]
    } & DefaultSession["user"]
  }

  interface User {
    id: number
    status: string
    roles: any[]
  }
}

export const { handlers, signIn, signOut, auth } = NextAuth({
  session: {
    strategy: "jwt",
  },
  pages: {
    signIn: "/auth/signin",
    error: "/auth/error",
  },
  providers: [
    Credentials({
      name: "credentials",
      credentials: {
        email: { label: "Email", type: "email" },
        password: { label: "Password", type: "password" },
      },
      async authorize(credentials) {
        if (!credentials?.email || !credentials?.password) {
                    console.log("[AUTH] Missing credentials - email:", credentials?.email);
          return null
        }

        try {
                    console.log("[AUTH] Attempting to find user with email:", credentials.email);
          // Find user by email
          const user = await prisma.user.findUnique({
            where: {
              email: credentials.email as string,
            },
            include: {
              user_roles: {
                include: {
                  role: true,
                },
              },
            },
          })

          if (!user) {
                console.log("[AUTH] User not found with email:", credentials.email);
                      console.log("[AUTH] User found, verifying status");
            return null
          }

          // Check if user is active
          if (user.status !== "ACTIVE") {
            console.log("[AUTH] Account is not active for user:", credentials.email, "status:", user.status);
            throw new Error("Account is not active")
          }

          // Verify password (supports both Argon2 from ETL app and bcrypt)
          const isPasswordValid = await verifyPasswordWithArgon2(
            credentials.password as string,
            user.password_hash
          )

          if (!isPasswordValid) {
                console.log("[AUTH] Invalid password for user:", credentials.email);
                      console.log("[AUTH] Password verified, extracting roles");
            return null
          }

          // Get user roles
          const roles = user.user_roles.map((ur) => ur.role)
          console.log("[AUTH] Authorization successful, roles count:", roles.length);

          // Return user object
          return {
            id: user.id,
            email: user.email,
            name: user.full_name,
            status: user.status,
            roles: roles,
          }
        } catch (error) {
          console.error("[AUTH] Authorization exception:", error);
          if (error instanceof Error) {
            console.error("[AUTH] Error message:", error.message);
            console.error("[AUTH] Error stack:", error.stack);
          }
          return null
        }
      },
    }),
  ],
  callbacks: {
    async jwt({ token, user }: any) {
      if (user) {
        token.id = user.id
        token.status = user.status
        token.roles = user.roles
      }
      return token
    },
    async session({ session, token }: any) {
      if (token && session.user) {
        session.user.id = token.id || 0
        session.user.status = token.status || ""
        session.user.roles = token.roles || []
      }
      return session
    },
  },
})
