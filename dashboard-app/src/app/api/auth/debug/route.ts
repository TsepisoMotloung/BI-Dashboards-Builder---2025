import { prisma } from "@/lib/prisma"
import { verifyPasswordWithArgon2 } from "@/lib/auth-utils"

export async function POST(req: Request) {
  try {
    const { email, password } = await req.json()

    if (!email || !password) {
      return Response.json({ error: "Email and password required" }, { status: 400 })
    }

    // Find user
    const user = await prisma.user.findUnique({
      where: { email },
      include: { user_roles: { include: { role: true } } },
    })

    if (!user) {
      return Response.json({ error: "User not found", email }, { status: 404 })
    }

    // Check status
    if (user.status !== "ACTIVE") {
      return Response.json(
        { error: "Account not active", status: user.status },
        { status: 403 }
      )
    }

    // Verify password
    const isValid = await verifyPasswordWithArgon2(password, user.password_hash)

    return Response.json({
      found: true,
      email: user.email,
      name: user.full_name,
      status: user.status,
      passwordValid: isValid,
      passwordHash: user.password_hash.substring(0, 20) + "...",
      roles: user.user_roles.map((r) => r.role.name),
    })
  } catch (error: any) {
    return Response.json(
      { error: error.message, stack: error.stack },
      { status: 500 }
    )
  }
}
