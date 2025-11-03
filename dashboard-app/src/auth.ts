import NextAuth, { DefaultSession } from "next-auth"
import Credentials from "next-auth/providers/credentials"
import { PrismaAdapter } from "@auth/prisma-adapter"
import { prisma } from "@/lib/prisma"
import { verifyPassword } from "@/lib/auth-utils"
import { UserStatus } from "@prisma/client"

declare module "next-auth" {
  interface Session {
    user: {
      id: number
      status: UserStatus
      roles: string[]
    } & DefaultSession["user"]
  }

  interface User {
    id: number
    status: UserStatus
    roles: string[]
  }
}

export const { handlers, signIn, signOut, auth } = NextAuth({
  adapter: PrismaAdapter(prisma),
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
          return null
        }

        try {
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
            return null
          }

          // Check if user is active
          if (user.status !== UserStatus.active) {
            throw new Error("Account is not active")
          }

          // Verify password (supports both Argon2 from ETL app and bcrypt)
          const isPasswordValid = await verifyPassword(
            credentials.password as string,
            user.password_hash
          )

          if (!isPasswordValid) {
            return null
          }

          // Get user roles
          const roles = user.user_roles.map((ur) => ur.role.name)

          // Return user object
          return {
            id: user.id,
            email: user.email,
            name: user.full_name,
            status: user.status,
            roles: roles,
          }
        } catch (error) {
          console.error("Authorization error:", error)
          return null
        }
      },
    }),
  ],
  callbacks: {
    async jwt({ token, user }) {
      if (user) {
        token.id = user.id
        token.status = user.status
        token.roles = user.roles
      }
      return token
    },
    async session({ session, token }) {
      if (token && session.user) {
        session.user.id = token.id as number
        session.user.status = token.status as UserStatus
        session.user.roles = token.roles as string[]
      }
      return session
    },
  },
})
